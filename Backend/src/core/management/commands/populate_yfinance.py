"""
Django management command to populate database with Yahoo Finance data.

Usage:
    python manage.py populate_yfinance --phase setup
"""

import asyncio
from django.core.management.base import BaseCommand

from utils.services.yfinance_populator import run_phase_1_setup


class Command(BaseCommand):
    help = "Populate the database with Yahoo Finance data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--phase",
            type=str,
            choices=["setup"],
            default="setup",
            help="Which phase to run (default: setup)",
        )

    def handle(self, *args, **options):
        phase = options["phase"]

        self.stdout.write(f"Starting Yahoo Finance population - Phase: {phase}")

        if phase == "setup":
            asyncio.run(run_phase_1_setup())

        self.stdout.write(self.style.SUCCESS("Population complete!"))
