import logging
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import psycopg2
from psycopg2 import sql, DatabaseError, OperationalError, DataError
from psycopg2.extras import RealDictCursor, execute_values

from django.conf import settings
from django.db import connection as django_db

logger = logging.getLogger(__name__)


@dataclass
class HypertableConfig:
    table_name: str
    time_column: str
    chunk_time_interval: str = "1 day"
    migrate_data: bool = True
    if_not_exists: bool = True


@dataclass
class RetentionPolicy:
    table_name: str
    drop_after: str = "30 days"


@dataclass
class ContinuousAggregate:
    aggregate_name: str
    source_table: str
    time_bucket: str
    columns: List[str]
    group_by_columns: List[str]


class TimescaleDBManager:
    """
    Manager for TimescaleDB operations in FinanceHub.
    Handles hypertable creation, data migration, query optimization,
    and automated archiving of time-series data.
    """

    def __init__(self):
        self._connection = None
        self._is_timescaledb_available = None

    @property
    def is_available(self) -> bool:
        """Check if TimescaleDB is available and properly configured."""
        if self._is_timescaledb_available is None:
            self._is_timescaledb_available = self._check_timescaledb_available()
        return self._is_timescaledb_available

    def _check_timescaledb_available(self) -> bool:
        """Verify TimescaleDB extension is installed."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT extname FROM pg_extension WHERE extname = 'timescaledb';"
                    )
                    result = cur.fetchone()
                    return result is not None
        except (DatabaseError, OperationalError) as e:
            logger.error(f"TimescaleDB availability check failed: {e}")
            return False

    @contextmanager
    def get_connection(self):
        """Get a connection to TimescaleDB."""
        conn = None
        try:
            conn = psycopg2.connect(
                host=getattr(settings, "TIMESCALE_DB_HOST", "localhost"),
                port=getattr(settings, "TIMESCALE_DB_PORT", 5432),
                database=getattr(settings, "TIMESCALE_DB_NAME", "financehub"),
                user=getattr(settings, "TIMESCALE_DB_USER", "postgres"),
                password=getattr(settings, "TIMESCALE_DB_PASSWORD", ""),
            )
            yield conn
        finally:
            if conn:
                conn.close()

    def get_django_connection_string(self) -> str:
        """Get Django database connection as a connection string."""
        db_config = settings.DATABASES["default"]
        return (
            f"host={db_config['HOST']} port={db_config['PORT']} "
            f"dbname={db_config['NAME']} user={db_config['USER']} "
            f"password={db_config['PASSWORD']}"
        )

    def create_hypertable(
        self,
        table_name: str,
        time_column: str,
        chunk_time_interval: str = "1 day",
        migrate_data: bool = True,
        if_not_exists: bool = True,
    ) -> bool:
        """
        Create a hypertable for time-series data.

        Args:
            table_name: Name of the table to convert to hypertable
            time_column: Name of the time column
            chunk_time_interval: Time interval for chunks (e.g., '1 day', '1 hour')
            migrate_data: Whether to migrate existing data
            if_not_exists: Skip if hypertable already exists

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("TimescaleDB not available. Skipping hypertable creation.")
            return False

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if if_not_exists:
                        cur.execute(
                            """
                            SELECT create_hypertable(%s, %s, migrate_data := %s, if_not_exists := true);
                        """,
                            (table_name, time_column, migrate_data),
                        )
                    else:
                        cur.execute(
                            """
                            SELECT create_hypertable(%s, %s, migrate_data := %s);
                        """,
                            (table_name, time_column, migrate_data),
                        )

                    cur.execute(
                        """
                        SELECT set_chunk_time_interval(%s, %s);
                    """,
                        (table_name, chunk_time_interval),
                    )

                    conn.commit()
                    logger.info(
                        f"Successfully created hypertable '{table_name}' with time column '{time_column}'"
                    )
                    return True

        except psycopg2.errors.DuplicateTable:
            logger.info(f"Hypertable '{table_name}' already exists")
            return True
        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to create hypertable '{table_name}': {e}")
            return False

    def create_hypertable_from_config(self, config: HypertableConfig) -> bool:
        """Create a hypertable using a HypertableConfig object."""
        return self.create_hypertable(
            table_name=config.table_name,
            time_column=config.time_column,
            chunk_time_interval=config.chunk_time_interval,
            migrate_data=config.migrate_data,
            if_not_exists=config.if_not_exists,
        )

    def add_dimension(
        self, table_name: str, column_name: str, number_partitions: int = 2
    ) -> bool:
        """
        Add an additional dimension to a hypertable for better query performance.

        Args:
            table_name: Name of the hypertable
            column_name: Column to use as dimension
            number_partitions: Number of partitions

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT add_dimension(%s, %s, number_partitions => %s);
                    """,
                        (table_name, column_name, number_partitions),
                    )
                    conn.commit()
                    logger.info(
                        f"Added dimension '{column_name}' to hypertable '{table_name}'"
                    )
                    return True

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to add dimension to '{table_name}': {e}")
            return False

    def set_retention_policy(
        self, table_name: str, drop_after: str = "30 days"
    ) -> bool:
        """
        Set a data retention policy for a hypertable.

        Args:
            table_name: Name of the hypertable
            drop_after: How long to keep data (e.g., '30 days', '1 year')

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT add_retention_policy(%s, INTERVAL %s);
                    """,
                        (table_name, drop_after),
                    )
                    conn.commit()
                    logger.info(
                        f"Set retention policy for '{table_name}': drop after {drop_after}"
                    )
                    return True

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to set retention policy for '{table_name}': {e}")
            return False

    def remove_retention_policy(self, table_name: str) -> bool:
        """Remove the retention policy from a hypertable."""
        if not self.is_available:
            return False

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT remove_retention_policy(%s);
                    """,
                        (table_name,),
                    )
                    conn.commit()
                    logger.info(f"Removed retention policy from '{table_name}'")
                    return True

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to remove retention policy from '{table_name}': {e}")
            return False

    def create_continuous_aggregate(
        self,
        aggregate_name: str,
        source_table: str,
        time_bucket: str,
        columns: List[str],
        group_by_columns: List[str],
    ) -> bool:
        """
        Create a continuous aggregate for pre-computed aggregations.

        Args:
            aggregate_name: Name for the new aggregate view
            source_table: Source hypertable name
            time_bucket: Time bucket interval (e.g., '1 hour', '1 day')
            columns: Columns to aggregate
            group_by_columns: Columns to group by

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            return False

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    columns_sql = ", ".join(columns)
                    group_by_sql = ", ".join(group_by_columns)

                    create_view_sql = f"""
                        CREATE MATERIALIZED VIEW {aggregate_name}
                        WITH (timescaledb.continuous) AS
                        SELECT
                            time_bucket('{time_bucket}', date) AS bucket,
                            {group_by_sql},
                            {self._get_aggregate_selections(columns)}
                        FROM {source_table}
                        GROUP BY bucket, {group_by_sql};
                    """

                    cur.execute(create_view_sql)

                    cur.execute(f"""
                        SELECT add_continuous_aggregate_policy('{aggregate_name}',
                            start_offset => INTERVAL '1 week',
                            end_offset => INTERVAL '1 hour',
                            schedule_interval => INTERVAL '1 hour');
                    """)

                    conn.commit()
                    logger.info(f"Created continuous aggregate '{aggregate_name}'")
                    return True

        except psycopg2.errors.DuplicateTable:
            logger.info(f"Continuous aggregate '{aggregate_name}' already exists")
            return True
        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(
                f"Failed to create continuous aggregate '{aggregate_name}': {e}"
            )
            return False

    def _get_aggregate_selections(self, columns: List[str]) -> str:
        """Generate aggregate function selections for columns."""
        selections = []
        for col in columns:
            if col in ["open", "low"]:
                selections.append(f"MIN({col}) AS {col}")
            elif col in ["high"]:
                selections.append(f"MAX({col}) AS {col}")
            elif col in ["close"]:
                selections.append(f"LAST({col}, date) AS close")
            elif col in ["volume"]:
                selections.append(f"SUM({col}) AS volume")
            else:
                selections.append(f"AVG({col}) AS {col}")
        return ", ".join(selections)

    def get_time_bucketed_data(
        self,
        table_name: str,
        time_bucket: str,
        start_time: datetime,
        end_time: datetime,
        asset_id: Optional[str] = None,
        aggregates: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query time-bucketed data from a hypertable.

        Args:
            table_name: Source table name
            time_bucket: Bucket interval
            start_time: Query start time
            end_time: Query end time
            asset_id: Optional asset filter
            aggregates: Optional custom aggregate functions

        Returns:
            List of bucketed data
        """
        if not self.is_available:
            return []

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    base_select = f"""
                        SELECT
                            time_bucket('{time_bucket}', date) AS bucket,
                            asset_id,
                            MIN(low) AS low,
                            MAX(high) AS high,
                            FIRST(open, date) AS open,
                            LAST(close, date) AS close,
                            SUM(volume) AS volume
                        FROM {table_name}
                        WHERE date >= %s AND date < %s
                    """

                    params = [start_time, end_time]

                    if asset_id:
                        base_select += " AND asset_id = %s"
                        params.append(asset_id)

                    base_select += " GROUP BY bucket, asset_id ORDER BY bucket DESC"

                    cur.execute(base_select, params)
                    results = cur.fetchall()

                    return [dict(row) for row in results]

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to get time-bucketed data from '{table_name}': {e}")
            return []

    def get_ohlcv_data(
        self, symbol: str, interval: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV (Open, High, Low, Close, Volume) data with time bucketing.

        Args:
            symbol: Asset symbol
            interval: Time interval (1min, 5min, 1hour, 1day, 1week, 1month)
            start_date: Start date
            end_date: End date

        Returns:
            List of OHLCV candles
        """
        if not self.is_available:
            return []

        interval_map = {
            "1min": "1 minute",
            "5min": "5 minutes",
            "15min": "15 minutes",
            "30min": "30 minutes",
            "1hour": "1 hour",
            "4hour": "4 hours",
            "1day": "1 day",
            "1week": "1 week",
            "1month": "1 month",
        }

        bucket_interval = interval_map.get(interval, "1 day")

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT
                            time_bucket(%s, date) AS bucket,
                            FIRST(open, date) AS open,
                            MAX(high) AS high,
                            MIN(low) AS low,
                            LAST(close, date) AS close,
                            SUM(volume) AS volume
                        FROM asset_prices_historic aph
                        JOIN assets_asset aa ON aa.id = aph.asset_id
                        WHERE aa.ticker = %s AND date >= %s AND date < %s
                        GROUP BY bucket
                        ORDER BY bucket DESC
                    """,
                        (bucket_interval, symbol, start_date, end_date),
                    )

                    results = cur.fetchall()
                    return [dict(row) for row in results]

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to get OHLCV data for {symbol}: {e}")
            return []

    def migrate_asset_prices_to_hypertable(
        self, batch_size: int = 10000, create_hypertable: bool = True
    ) -> Tuple[int, int]:
        """
        Migrate AssetPricesHistoric data to TimescaleDB hypertable.

        Args:
            batch_size: Number of records to process per batch
            create_hypertable: Whether to create hypertable first

        Returns:
            Tuple of (migrated_count, error_count)
        """
        if not self.is_available:
            logger.warning("TimescaleDB not available. Skipping migration.")
            return (0, 0)

        migrated = 0
        errors = 0

        try:
            from assets.models.historic.prices import AssetPricesHistoric
            from assets.models.asset import Asset

            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if create_hypertable:
                        self.create_hypertable(
                            table_name="asset_prices_historic",
                            time_column="date",
                            chunk_time_interval="7 days",
                        )

                    offset = 0
                    while True:
                        cur.execute(
                            """
                            SELECT id, asset_id, date, open, high, low, close, volume,
                                   volatility, source_id, created_at, updated_at
                            FROM asset_prices_historic
                            ORDER BY id
                            LIMIT %s OFFSET %s
                        """,
                            (batch_size, offset),
                        )

                        rows = cur.fetchall()

                        if not rows:
                            break

                        for row in rows:
                            try:
                                cur.execute(
                                    """
                                    INSERT INTO asset_prices_historic
                                    (id, asset_id, date, open, high, low, close, volume,
                                     volatility, source_id, created_at, updated_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO NOTHING
                                """,
                                    row,
                                )
                                migrated += 1
                            except (DatabaseError, OperationalError, DataError) as e:
                                errors += 1
                                logger.error(f"Error migrating row {row[0]}: {e}")

                        conn.commit()
                        offset += batch_size

                        if len(rows) < batch_size:
                            break

                    logger.info(
                        f"Migration complete: {migrated} records migrated, {errors} errors"
                    )
                    return (migrated, errors)

        except ImportError as e:
            logger.error(f"Import error during migration: {e}")
            return (0, 0)
        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Migration failed: {e}")
            return (migrated, errors)

    def get_compression_stats(self, table_name: str) -> Dict[str, Any]:
        """Get compression statistics for a hypertable."""
        if not self.is_available:
            return {}

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT
                            pg_total_relation_size(oid) AS total_size,
                            pg_relation_size(oid) AS table_size,
                            pg_total_relation_size(oid) - pg_relation_size(oid) AS index_size
                        FROM pg_class WHERE relname = %s
                    """,
                        (table_name,),
                    )

                    result = cur.fetchone()
                    if result:
                        return dict(result)

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to get compression stats: {e}")

        return {}

    def enable_auto_compression(self, table_name: str) -> bool:
        """Enable automatic compression for a hypertable."""
        if not self.is_available:
            return False

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        ALTER TABLE %s SET (
                            timescaledb.compress,
                            timescaledb.compress_segmentby = 'asset_id'
                        );
                    """,
                        (table_name,),
                    )

                    cur.execute(
                        """
                        SELECT add_compression_policy(%s, INTERVAL '7 days');
                    """,
                        (table_name,),
                    )

                    conn.commit()
                    logger.info(f"Enabled auto-compression for '{table_name}'")
                    return True

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to enable compression for '{table_name}': {e}")
            return False

    def get_chunks_info(self, table_name: str) -> List[Dict[str, Any]]:
        """Get information about chunks in a hypertable."""
        if not self.is_available:
            return []

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT
                            chunk_name,
                            range_start,
                            range_end,
                            tablebytes,
                            indexbytes,
                            totalbytes
                        FROM timescaledb_information.chunks
                        WHERE hypertable_name = %s
                        ORDER BY range_start DESC
                    """,
                        (table_name,),
                    )

                    results = cur.fetchall()
                    return [dict(row) for row in results]

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to get chunks info: {e}")
            return []

    def drop_old_chunks(self, table_name: str, older_than: str) -> int:
        """
        Drop chunks older than specified interval.

        Args:
            table_name: Hypertable name
            older_than: Age threshold (e.g., '1 year', '6 months')

        Returns:
            Number of chunks dropped
        """
        if not self.is_available:
            return 0

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT drop_chunks(%s, INTERVAL %s);
                    """,
                        (table_name, older_than),
                    )
                    result = cur.fetchone()
                    dropped = result[0] if result else 0
                    logger.info(
                        f"Dropped {dropped} chunks from '{table_name}' older than {older_than}"
                    )
                    return dropped

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to drop chunks: {e}")
            return 0

    def get_storage_info(self) -> Dict[str, Any]:
        """Get overall storage information for all hypertables."""
        if not self.is_available:
            return {}

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT
                            hypertable_name,
                            table_bytes,
                            index_bytes,
                            toast_bytes,
                            total_bytes,
                            num_chunks
                        FROM timescaledb_information.hypertables
                        ORDER BY total_bytes DESC
                    """)

                    results = cur.fetchall()
                    return {
                        "hypertables": [dict(row) for row in results],
                        "total_storage": sum(row["total_bytes"] for row in results),
                    }

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to get storage info: {e}")
            return {}

    def setup_timescale_functions(self) -> bool:
        """
        Set up all TimescaleDB functions and policies for FinanceHub.
        This is the main setup function to be called during initialization.

        Returns:
            True if successful, False otherwise
        """
        if not self.is_available:
            logger.warning("TimescaleDB not available. Skipping setup.")
            return False

        try:
            logger.info("Setting up TimescaleDB functions...")

            self.create_hypertable(
                table_name="asset_prices_historic",
                time_column="date",
                chunk_time_interval="7 days",
            )

            self.set_retention_policy(
                table_name="asset_prices_historic", drop_after="2 years"
            )

            self.enable_auto_compression("asset_prices_historic")

            self.create_continuous_aggregate(
                aggregate_name="asset_prices_hourly",
                source_table="asset_prices_historic",
                time_bucket="1 hour",
                columns=["open", "high", "low", "close", "volume"],
                group_by_columns=["asset_id"],
            )

            self.create_continuous_aggregate(
                aggregate_name="asset_prices_daily",
                source_table="asset_prices_historic",
                time_bucket="1 day",
                columns=["open", "high", "low", "close", "volume"],
                group_by_columns=["asset_id"],
            )

            logger.info("TimescaleDB setup completed successfully")
            return True

        except (DatabaseError, OperationalError, DataError) as e:
            logger.error(f"Failed to setup TimescaleDB functions: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Check TimescaleDB health and return status information."""
        return {
            "available": self.is_available,
            "storage": self.get_storage_info() if self.is_available else {},
            "compression": self.get_compression_stats("asset_prices_historic")
            if self.is_available
            else {},
            "chunks": self.get_chunks_info("asset_prices_historic")
            if self.is_available
            else [],
        }


timescale_manager = TimescaleDBManager()
