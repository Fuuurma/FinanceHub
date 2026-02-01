#  src/data/data_fetcher/command.py

"""Django management command to run data jobs"""
import asyncio
from django.core.management.base import BaseCommand

from data.data_fetcher.manager import JobManager


class Command(BaseCommand):
    help = "Run data fetching jobs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--job",
            type=str,
            required=True,
            choices=["daily", "weekly", "quarterly", "initial", "backfill"],
            help="Job type to run",
        )
        parser.add_argument(
            "--symbols",
            type=str,
            help="Comma-separated list of symbols for initial setup",
        )

    def handle(self, *args, **options):
        job_type = options["job"]
        manager = JobManager()

        # chage to constants.. and know how and when to execute which one ¿?
        async def run():
            if job_type == "daily":
                await manager.run_daily_jobs()
            elif job_type == "weekly":
                await manager.run_weekly_jobs()
            elif job_type == "quarterly":
                await manager.run_quarterly_jobs()
            elif job_type == "initial":
                symbols = options.get("symbols", "").split(",")
                if not symbols or not symbols[0]:
                    self.stdout.write(self.style.ERROR("Please provide --symbols"))
                    return
                await manager.run_initial_setup(symbols)
            elif job_type == "backfill":
                await manager.run_historical_backfill()

        try:
            asyncio.run(run())
            self.stdout.write(self.style.SUCCESS(f"✓ {job_type.title()} job completed"))
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            self.stdout.write(self.style.ERROR(f"✗ Error: {str(e)}"))
