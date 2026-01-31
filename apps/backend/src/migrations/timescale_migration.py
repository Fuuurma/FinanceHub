"""
TimescaleDB Migration Script for FinanceHub

This script handles the migration of existing PostgreSQL tables
to TimescaleDB hypertables with automatic partitioning and compression.
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple

from django.db import connection

from utils.services.timescale_manager import timescale_manager
from utils.services.archive import data_archiver

logger = logging.getLogger(__name__)


class TimescaleMigration:
    """
    Manages database migrations to TimescaleDB.
    Handles schema changes, data migration, and validation.
    """

    MIGRATION_VERSION = "1.0.0"
    MIGRATION_NAME = "timescale_initial_migration"

    def __init__(self):
        self.migration_log = []
        self.start_time = None

    def log_migration(self, action: str, details: str = "", success: bool = True):
        """Log a migration step."""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "action": action,
            "details": details,
            "success": success,
        }
        self.migration_log.append(entry)
        status = "✓" if success else "✗"
        logger.info(f"{status} [{timestamp}] {action}: {details}")

    def check_prerequisites(self) -> Tuple[bool, List[str]]:
        """
        Check if all prerequisites for migration are met.

        Returns:
            Tuple of (all_met: bool, missing_prerequisites: List[str])
        """
        missing = []

        if not timescale_manager.is_available:
            missing.append("TimescaleDB extension not installed")

        try:
            with connection.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                logger.info(f"PostgreSQL version: {version}")
        except Exception as e:
            missing.append(f"Database connection failed: {e}")

        return len(missing) == 0, missing

    def create_timescale_extensions(self) -> bool:
        """Create required TimescaleDB extensions."""
        try:
            with connection.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
            self.log_migration(
                "Create TimescaleDB extension", "Extension created or already exists"
            )
            return True
        except Exception as e:
            self.log_migration("Create TimescaleDB extension", str(e), success=False)
            return False

    def get_table_info(self, table_name: str) -> Dict:
        """Get information about an existing table."""
        try:
            with connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        c.relname AS table_name,
                        c.reltuples AS row_count,
                        pg_total_relation_size(c.oid) AS size_bytes
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE c.relname = %s AND n.nspname = 'public'
                """,
                    (table_name,),
                )

                result = cur.fetchone()
                if result:
                    return {
                        "table_name": result[0],
                        "row_count": result[1],
                        "size_bytes": result[2],
                    }
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")

        return {}

    def migrate_asset_prices_historic(self) -> bool:
        """
        Migrate AssetPricesHistoric table to TimescaleDB hypertable.

        Returns:
            True if successful, False otherwise
        """
        table_name = "asset_prices_historic"

        self.log_migration("Start migration", f"Table: {table_name}")

        try:
            from assets.models.historic.prices import AssetPricesHistoric

            with connection.cursor() as cur:
                cur.execute("SELECT count(*) FROM asset_prices_historic;")
                row_count = cur.fetchone()[0]
                self.log_migration("Table row count", f"{row_count} rows")

                if row_count == 0:
                    self.log_migration("Skip migration", "Table is empty")
                    return True

            success = timescale_manager.create_hypertable(
                table_name=table_name,
                time_column="date",
                chunk_time_interval="7 days",
                migrate_data=True,
                if_not_exists=True,
            )

            if success:
                timescale_manager.set_retention_policy(
                    table_name=table_name, drop_after="2 years"
                )

                timescale_manager.enable_auto_compression(table_name)

                timescale_manager.create_continuous_aggregate(
                    aggregate_name="asset_prices_hourly",
                    source_table=table_name,
                    time_bucket="1 hour",
                    columns=["open", "high", "low", "close", "volume"],
                    group_by_columns=["asset_id"],
                )

                timescale_manager.create_continuous_aggregate(
                    aggregate_name="asset_prices_daily",
                    source_table=table_name,
                    time_bucket="1 day",
                    columns=["open", "high", "low", "close", "volume"],
                    group_by_columns=["asset_id"],
                )

                self.log_migration(
                    "Complete migration", f"Table {table_name} converted to hypertable"
                )
                return True
            else:
                self.log_migration(
                    "Migration failed",
                    f"Failed to create hypertable for {table_name}",
                    success=False,
                )
                return False

        except ImportError as e:
            self.log_migration("Import error", str(e), success=False)
            return False
        except Exception as e:
            self.log_migration("Migration error", str(e), success=False)
            return False

    def create_performance_metrics_hypertable(self) -> bool:
        """Create hypertable for performance metrics if the table exists."""
        table_name = "performance_metrics"

        try:
            with connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = %s
                    );
                """,
                    (table_name,),
                )

                if not cur.fetchone()[0]:
                    self.log_migration(
                        "Skip hypertable", f"Table {table_name} does not exist"
                    )
                    return True

            success = timescale_manager.create_hypertable(
                table_name=table_name,
                time_column="created_at",
                chunk_time_interval="1 day",
                migrate_data=True,
            )

            if success:
                timescale_manager.set_retention_policy(
                    table_name=table_name, drop_after="30 days"
                )

                self.log_migration("Create performance metrics hypertable", "Success")
                return True

        except Exception as e:
            self.log_migration(
                "Create performance metrics hypertable", str(e), success=False
            )
            return False

        return False

    def create_api_usage_hypertable(self) -> bool:
        """Create hypertable for API usage logs if the table exists."""
        table_name = "api_usage_logs"

        try:
            with connection.cursor() as cur:
                cur.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = %s
                    );
                """,
                    (table_name,),
                )

                if not cur.fetchone()[0]:
                    self.log_migration(
                        "Skip hypertable", f"Table {table_name} does not exist"
                    )
                    return True

            success = timescale_manager.create_hypertable(
                table_name=table_name,
                time_column="created_at",
                chunk_time_interval="1 hour",
                migrate_data=True,
            )

            if success:
                timescale_manager.set_retention_policy(
                    table_name=table_name, drop_after="7 days"
                )

                self.log_migration("Create API usage hypertable", "Success")
                return True

        except Exception as e:
            self.log_migration("Create API usage hypertable", str(e), success=False)
            return False

        return False

    def validate_migration(self) -> Dict:
        """Validate the migration was successful."""
        validation = {
            "timescaledb_available": False,
            "hypertables_created": [],
            "continuous_aggregates": [],
            "retention_policies": [],
            "errors": [],
        }

        try:
            validation["timescaledb_available"] = timescale_manager.is_available

            with connection.cursor() as cur:
                cur.execute("""
                    SELECT hypertable_name
                    FROM timescaledb_information.hypertables;
                """)
                validation["hypertables_created"] = [row[0] for row in cur.fetchall()]

                cur.execute("""
                    SELECT view_name
                    FROM timescaledb_information.continuous_aggregates;
                """)
                validation["continuous_aggregates"] = [row[0] for row in cur.fetchall()]

                cur.execute("""
                    SELECT hypertable_name, drop_after
                    FROM timescaledb_information.retention_policies;
                """)
                validation["retention_policies"] = [
                    {"table": row[0], "drop_after": str(row[1])}
                    for row in cur.fetchall()
                ]

        except Exception as e:
            validation["errors"].append(str(e))

        return validation

    def run_migration(self, migrate_all: bool = True) -> Dict:
        """
        Run the complete TimescaleDB migration.

        Args:
            migrate_all: Whether to migrate all possible tables

        Returns:
            Migration result dictionary
        """
        self.start_time = datetime.now()
        self.migration_log = []

        self.log_migration("Start migration", f"Version {self.MIGRATION_VERSION}")

        prerequisites_ok, missing = self.check_prerequisites()

        if not prerequisites_ok:
            self.log_migration(
                "Prerequisites check", f"Missing: {missing}", success=False
            )
            return {
                "success": False,
                "error": f"Missing prerequisites: {missing}",
                "log": self.migration_log,
            }

        self.log_migration("Prerequisites check", "All prerequisites met")

        if not self.create_timescale_extensions():
            return {
                "success": False,
                "error": "Failed to create TimescaleDB extension",
                "log": self.migration_log,
            }

        if not self.migrate_asset_prices_historic():
            return {
                "success": False,
                "error": "Failed to migrate asset_prices_historic",
                "log": self.migration_log,
            }

        if migrate_all:
            self.create_performance_metrics_hypertable()
            self.create_api_usage_hypertable()

        validation = self.validate_migration()

        elapsed = (datetime.now() - self.start_time).total_seconds()

        self.log_migration(
            "Migration complete",
            f"Elapsed: {elapsed:.2f}s, Hypertables: {len(validation['hypertables_created'])}",
        )

        return {
            "success": True,
            "elapsed_seconds": elapsed,
            "validation": validation,
            "log": self.migration_log,
        }

    def rollback_migration(self, table_name: str) -> bool:
        """
        Rollback a specific hypertable migration.

        Args:
            table_name: Name of the hypertable to rollback

        Returns:
            True if successful, False otherwise
        """
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT drop_hypertable(%s);", (table_name,))
            self.log_migration("Rollback", f"Dropped hypertable {table_name}")
            return True
        except Exception as e:
            self.log_migration("Rollback failed", str(e), success=False)
            return False

    def get_migration_status(self) -> Dict:
        """Get the current migration status."""
        validation = self.validate_migration()

        return {
            "is_timescaledb_available": validation["timescaledb_available"],
            "hypertables": validation["hypertables_created"],
            "aggregates": validation["continuous_aggregates"],
            "retention_policies": validation["retention_policies"],
            "migration_log": self.migration_log[-10:],
        }


def run_migration():
    """Entry point for running the TimescaleDB migration."""
    import django

    django.setup()

    migration = TimescaleMigration()
    result = migration.run_migration()

    if result["success"]:
        logger.info("Migration completed successfully")
        logger.info(
            "Hypertables created: %d", len(result["validation"]["hypertables_created"])
        )
        logger.info(
            "Continuous aggregates: %d",
            len(result["validation"]["continuous_aggregates"]),
        )
        logger.info("Elapsed time: %.2fs", result["elapsed_seconds"])
    else:
        logger.error("Migration failed: %s", result["error"])
        logger.info("Migration log:")
        for entry in result["log"]:
            status = "SUCCESS" if entry["success"] else "FAILED"
            logger.info("%s %s: %s", status, entry["action"], entry["details"])

    return result


def check_status():
    """Entry point for checking migration status."""
    import django

    django.setup()

    migration = TimescaleMigration()
    status = migration.get_migration_status()

    logger.info("TimescaleDB Migration Status")
    logger.info("========================================")
    logger.info(
        "TimescaleDB Available: %s",
        "Yes" if status["is_timescaledb_available"] else "No",
    )
    logger.info("Hypertables: %s", ", ".join(status["hypertables"]) or "None")
    logger.info("Continuous Aggregates: %s", ", ".join(status["aggregates"]) or "None")
    logger.info("Retention Policies:")
    for policy in status["retention_policies"]:
        logger.info("  - %s: drop after %s", policy["table"], policy["drop_after"])

    return status


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        check_status()
    else:
        run_migration()
