from django.contrib import admin

from investments.models.alert import Alert
from investments.models.benchmark import Benchmark
from investments.models.benchmark_price_history import BenchmarkPriceHistory
from investments.models.corporate_action import CorporateAction
from investments.models.currency import Currency
from investments.models.dividend import Dividend
from investments.models.exchange_rate import ExchangeRate
from investments.models.transaction import Transaction
from investments.models.transaction_type import TransactionType
from investments.models.watchlist import Watchlist

admin.site.register(TransactionType)
admin.site.register(Transaction)
admin.site.register(Currency)
admin.site.register(ExchangeRate)
admin.site.register(Dividend)
admin.site.register(CorporateAction)
admin.site.register(Benchmark)
admin.site.register(BenchmarkPriceHistory)
admin.site.register(Alert)
admin.site.register(Watchlist)
