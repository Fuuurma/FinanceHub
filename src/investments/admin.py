from django.contrib import admin

from investments.models.corporate_action import CorporateAction
from investments.models.currency import Currency
from investments.models.dividend import Dividend
from investments.models.exchange_rate import ExchangeRate
from investments.models.transaction import Transaction
from investments.models.transaction_type import TransactionType

admin.site.register(TransactionType)
admin.site.register(Transaction)
admin.site.register(Currency)
admin.site.register(ExchangeRate)
admin.site.register(Dividend)
admin.site.register(CorporateAction)
