from django.contrib import admin

from investments.models.transaction import Transaction
from investments.models.transaction_type import TransactionType

admin.site.register(TransactionType)
admin.site.register(Transaction)
