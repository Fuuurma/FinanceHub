import gzip
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class ArchiveConfig:
    table_name: str
    archive_folder: str
    s3_bucket: Optional[str] = None
    s3_prefix: Optional[str] = None
    compressed: bool = True
    batch_size: int = 100000
    retention_days: int = 365


@dataclass
class ArchiveResult:
    success: bool
    records_archived: int
    file_path: Optional[str]
    file_size_bytes: int
    error_message: Optional[str] = None


class DataArchiver:
    """
    Manages automated archiving of historical data from TimescaleDB.
    Supports local file storage and AWS S3 cloud storage.
    """

    def __init__(self):
        self.s3_client = None
        self._init_s3_client()

    def _init_s3_client(self):
        """Initialize S3 client if configured."""
        aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        aws_region = getattr(settings, 'AWS_REGION', 'us-east-1')

        if aws_access_key and aws_secret_key:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                logger.info("S3 client initialized successfully")
            except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
                logger.error(f"Failed to initialize S3 client: {e}")

    def get_default_archive_folder(self) -> Path:
        """Get the default archive folder path."""
        archive_base = getattr(settings, 'ARCHIVE_BASE_PATH', '/tmp/financehub_archives')
        return Path(archive_base)

    def ensure_archive_directory(self, folder: Path) -> bool:
        """Ensure the archive directory exists."""
        try:
            folder.mkdir(parents=True, exist_ok=True)
            return True
        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Failed to create archive directory {folder}: {e}")
            return False

    def get_oldest_records_query(
        self,
        table_name: str,
        older_than: datetime,
        batch_size: int
    ) -> str:
        """Generate SQL query to fetch old records for archiving."""
        return f"""
            SELECT * FROM {table_name}
            WHERE created_at < %s
            ORDER BY created_at ASC
            LIMIT %s
        """

    def export_to_csv(
        self,
        table_name: str,
        output_path: Path,
        older_than: datetime,
        batch_size: int = 100000
    ) -> Tuple[int, int]:
        """
        Export old records to CSV file.

        Returns:
            Tuple of (records_exported, errors_count)
        """
        from utils.services.timescale_manager import timescale_manager

        if not timescale_manager.is_available:
            logger.warning("TimescaleDB not available. Skipping export.")
            return (0, 0)

        exported = 0
        errors = 0

        try:
            with timescale_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    query = self.get_oldest_records_query(table_name, older_than, batch_size)
                    cur.execute(query, (older_than, batch_size))

                    if cur.description:
                        columns = [desc[0] for desc in cur.description]

                        with open(output_path, 'w', newline='') as f:
                            import csv
                            writer = csv.writer(f)
                            writer.writerow(columns)

                            batch = cur.fetchmany(batch_size)
                            while batch:
                                for row in batch:
                                    try:
                                        writer.writerow(row)
                                        exported += 1
                                    except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
                                        errors += 1
                                        logger.error(f"Error writing row: {e}")

                                batch = cur.fetchmany(batch_size)

                    logger.info(f"Exported {exported} records to {output_path}")
                    return (exported, errors)

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Export failed: {e}")
            return (exported, errors)

    def compress_file(self, file_path: Path) -> Path:
        """Compress a file using gzip."""
        compressed_path = Path(str(file_path) + '.gz')

        try:
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            original_size = file_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100

            logger.info(f"Compressed {file_path.name}: {original_size} -> {compressed_size} bytes ({compression_ratio:.1f}% reduction)")

            file_path.unlink()
            return compressed_path

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Failed to compress {file_path}: {e}")
            return file_path

    def upload_to_s3(
        self,
        file_path: Path,
        bucket: str,
        s3_key: str
    ) -> bool:
        """Upload a file to S3."""
        if not self.s3_client:
            logger.warning("S3 client not initialized. Upload skipped.")
            return False

        try:
            extra_args = {}
            content_type = self._get_content_type(file_path)
            if content_type:
                extra_args['ContentType'] = content_type

            if file_path.suffix == '.gz':
                extra_args['ContentEncoding'] = 'gzip'

            self.s3_client.upload_file(str(file_path), bucket, s3_key, ExtraArgs=extra_args)
            logger.info(f"Uploaded {file_path.name} to s3://{bucket}/{s3_key}")
            return True

        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False

    def _get_content_type(self, file_path: Path) -> Optional[str]:
        """Get the content type for a file."""
        content_types = {
            '.csv': 'text/csv',
            '.csv.gz': 'text/csv',
            '.json': 'application/json',
            '.json.gz': 'application/json',
            '.parquet': 'application/octet-stream',
        }
        return content_types.get(file_path.suffix)

    def delete_archived_records(
        self,
        table_name: str,
        older_than: datetime,
        batch_size: int = 10000
    ) -> Tuple[int, int]:
        """
        Delete archived records from the database.

        Returns:
            Tuple of (records_deleted, errors_count)
        """
        from utils.services.timescale_manager import timescale_manager

        if not timescale_manager.is_available:
            return (0, 0)

        deleted = 0
        errors = 0

        try:
            with timescale_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    while True:
                        cur.execute("""
                            DELETE FROM {table}
                            WHERE created_at < %s
                            LIMIT %s
                        """.format(table=table_name), (older_than, batch_size))

                        batch_deleted = cur.rowcount

                        if batch_deleted == 0:
                            break

                        deleted += batch_deleted
                        conn.commit()

                    logger.info(f"Deleted {deleted} records from {table_name}")
                    return (deleted, errors)

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Failed to delete archived records: {e}")
            return (deleted, errors)

    def archive_table(
        self,
        config: ArchiveConfig,
        older_than: Optional[datetime] = None
    ) -> ArchiveResult:
        """
        Archive a table's old records to compressed files.

        Args:
            config: Archive configuration
            older_than: Archive records older than this date (defaults to retention days ago)

        Returns:
            ArchiveResult with success status and details
        """
        if older_than is None:
            older_than = datetime.now() - timedelta(days=config.retention_days)

        archive_folder = Path(config.archive_folder)
        if not self.ensure_archive_directory(archive_folder):
            return ArchiveResult(
                success=False,
                records_archived=0,
                file_path=None,
                file_size_bytes=0,
                error_message=f"Failed to create archive directory: {archive_folder}"
            )

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        table_safe_name = config.table_name.replace('.', '_')
        csv_filename = f"{table_safe_name}_{timestamp}.csv"
        csv_path = archive_folder / csv_filename

        exported, errors = self.export_to_csv(
            table_name=config.table_name,
            output_path=csv_path,
            older_than=older_than,
            batch_size=config.batch_size
        )

        if exported == 0:
            if csv_path.exists():
                csv_path.unlink()
            return ArchiveResult(
                success=True,
                records_archived=0,
                file_path=None,
                file_size_bytes=0,
                error_message=None
            )

        final_path = csv_path
        file_size = csv_path.stat().st_size if csv_path.exists() else 0

        if config.compressed:
            final_path = self.compress_file(csv_path)
            file_size = final_path.stat().st_size if final_path.exists() else 0

        upload_success = True
        if config.s3_bucket and config.s3_prefix and self.s3_client:
            s3_key = f"{config.s3_prefix}/{final_path.name}"
            upload_success = self.upload_to_s3(final_path, config.s3_bucket, s3_key)

        deleted, delete_errors = self.delete_archived_records(
            config.table_name,
            older_than,
            config.batch_size
        )

        return ArchiveResult(
            success=True,
            records_archived=exported,
            file_path=str(final_path),
            file_size_bytes=file_size,
            error_message=None
        )

    def restore_from_archive(
        self,
        archive_path: Path,
        table_name: str,
        truncate_before_restore: bool = False
    ) -> Tuple[int, int]:
        """
        Restore data from an archived CSV file.

        Args:
            archive_path: Path to the archive file
            table_name: Target table name
            truncate_before_restore: Whether to truncate table before restore

        Returns:
            Tuple of (records_restored, errors_count)
        """
        from utils.services.timescale_manager import timescale_manager

        if not timescale_manager.is_available:
            return (0, 0)

        restored = 0
        errors = 0

        try:
            with timescale_manager.get_connection() as conn:
                with conn.cursor() as cur:
                    if truncate_before_restore:
                        cur.execute(f"TRUNCATE TABLE {table_name}")

                    if archive_path.suffix == '.gz':
                        import csv
                        import gzip

                        with gzip.open(archive_path, 'rt', newline='') as f:
                            reader = csv.reader(f)
                            columns = next(reader)

                            batch = []
                            for row in reader:
                                batch.append(row)

                                if len(batch) >= 1000:
                                    execute_values(
                                        cur,
                                        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s",
                                        batch
                                    )
                                    conn.commit()
                                    restored += len(batch)
                                    batch = []

                            if batch:
                                execute_values(
                                    cur,
                                    f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s",
                                    batch
                                )
                                restored += len(batch)
                                conn.commit()

                    else:
                        with open(archive_path, 'r') as f:
                            cur.copy_expert(
                                f"COPY {table_name} FROM STDIN WITH CSV HEADER",
                                f
                            )
                            conn.commit()

                    logger.info(f"Restored {restored} records from {archive_path}")
                    return (restored, errors)

        except (ValueError, KeyError, TypeError, DatabaseError, OperationalError) as e:
            logger.error(f"Failed to restore from archive: {e}")
            return (restored, errors)

    def list_local_archives(
        self,
        folder: Optional[Path] = None,
        table_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List available local archives."""
        if folder is None:
            folder = self.get_default_archive_folder()

        archives = []

        if not folder.exists():
            return archives

        for file_path in folder.glob('*.csv*'):
            if table_name and table_name not in file_path.name:
                continue

            stat = file_path.stat()
            archives.append({
                'filename': file_path.name,
                'path': str(file_path),
                'size_bytes': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'compressed': file_path.suffix == '.gz'
            })

        return sorted(archives, key=lambda x: x['modified'], reverse=True)

    def list_s3_archives(
        self,
        bucket: str,
        prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List archives in S3."""
        if not self.s3_client:
            return []

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix or ''
            )

            archives = []
            for obj in response.get('Contents', []):
                archives.append({
                    'key': obj['Key'],
                    'size_bytes': obj['Size'],
                    'modified': obj['LastModified'],
                    'url': f"s3://{bucket}/{obj['Key']}"
                })

            return sorted(archives, key=lambda x: x['modified'], reverse=True)

        except ClientError as e:
            logger.error(f"Failed to list S3 archives: {e}")
            return []

    def cleanup_local_archives(
        self,
        older_than_days: int = 30,
        folder: Optional[Path] = None
    ) -> int:
        """Delete local archive files older than specified days."""
        if folder is None:
            folder = self.get_default_archive_folder()

        if not folder.exists():
            return 0

        cutoff = datetime.now() - timedelta(days=older_than_days)
        deleted = 0

        for file_path in folder.glob('*.csv*'):
            if file_path.stat().st_mtime < cutoff.timestamp():
                file_path.unlink()
                deleted += 1

        logger.info(f"Cleaned up {deleted} old archive files from {folder}")
        return deleted

    def get_archive_stats(self) -> Dict[str, Any]:
        """Get statistics about archived data."""
        stats = {
            'total_archives': 0,
            'total_size_bytes': 0,
            'compressed_archives': 0,
            'oldest_archive': None,
            'newest_archive': None,
            's3_archives': 0
        }

        local_archives = self.list_local_archives()

        stats['total_archives'] = len(local_archives)
        stats['total_size_bytes'] = sum(a['size_bytes'] for a in local_archives)
        stats['compressed_archives'] = sum(1 for a in local_archives if a['compressed'])

        if local_archives:
            stats['oldest_archive'] = local_archives[-1]
            stats['newest_archive'] = local_archives[0]

        s3_bucket = getattr(settings, 'ARCHIVE_S3_BUCKET', None)
        if s3_bucket:
            s3_archives = self.list_s3_archives(s3_bucket)
            stats['s3_archives'] = len(s3_archives)

        return stats

    def run_automated_archive(
        self,
        table_name: str,
        archive_folder: Optional[Path] = None,
        s3_bucket: Optional[str] = None,
        retention_days: int = 365
    ) -> ArchiveResult:
        """
        Run automated archiving for a table.

        This is the main method to be called by scheduled tasks.
        """
        config = ArchiveConfig(
            table_name=table_name,
            archive_folder=str(archive_folder or self.get_default_archive_folder()),
            s3_bucket=s3_bucket or getattr(settings, 'ARCHIVE_S3_BUCKET', None),
            s3_prefix=getattr(settings, 'ARCHIVE_S3_PREFIX', 'archives'),
            compressed=True,
            batch_size=100000,
            retention_days=retention_days
        )

        return self.archive_table(config)


data_archiver = DataArchiver()
