import asyncio
import dramatiq
from django.core.management.base import BaseCommand

from utils.helpers.logger.logger import get_logger
from utils.services.realtime_stream_manager import get_real_time_stream_manager
from utils.services.call_planner import get_call_planner

logger = get_logger(__name__)


class Command(BaseCommand):
    help = 'Start real-time streaming services (Binance, Finnhub WebSockets)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--binance',
            action='store_true',
            help='Start Binance WebSocket streams',
        )
        parser.add_argument(
            '--finnhub',
            action='store_true',
            help='Start Finnhub WebSocket streams',
        )
        parser.add_argument(
            '--call-planner',
            action='store_true',
            help='Start call planner workers',
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=3,
            help='Number of call planner workers',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Starting real-time streaming services...')
        
        if options.get('call_planner'):
            self.stdout.write('Starting call planner...')
            asyncio.run(self._start_call_planner(options.get('workers', 3)))
        
        asyncio.run(self._start_streams(
            binance=options.get('binance', True),
            finnhub=options.get('finnhub', True)
        ))
        
        self.stdout.write('Real-time streaming services started')
    
    async def _start_call_planner(self, num_workers: int):
        planner = get_call_planner()
        
        if not planner.running:
            await planner.start(num_workers=num_workers)
            self.stdout.write(f'Call planner started with {num_workers} workers')
        else:
            self.stdout.write('Call planner already running')
    
    async def _start_streams(self, binance: bool, finnhub: bool):
        stream_manager = get_real_time_stream_manager()
        
        if not stream_manager.running:
            await stream_manager.start()
            self.stdout.write('Real-time stream manager started')
        else:
            self.stdout.write('Real-time stream manager already running')
        
        status = stream_manager.get_status()
        self.stdout.write(f'Current status: {status}')
        
        self.stdout.write('Press Ctrl+C to stop...')
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write('\nStopping real-time streaming services...')
            await stream_manager.stop()
            self.stdout.write('Real-time streaming services stopped')
