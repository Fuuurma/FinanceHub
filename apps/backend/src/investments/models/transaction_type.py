from django.db import models


class TransactionType(models.Model):
    name = models.CharField(
        max_length=20, unique=True
    )  # Buy, Sell, Dividend, Split, etc.

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
