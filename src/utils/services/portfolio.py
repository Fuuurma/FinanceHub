# investments/services.py
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from portfolios.models.portfolio import Portfolio
from utils.helpers.error_handler.exceptions import ValidationException


class PortfolioService:
    @staticmethod
    @transaction.atomic
    def create_portfolio(user, data: dict) -> Portfolio:
        return Portfolio.objects.create(user=user, **data)

    @staticmethod
    def get_user_portfolios(user):
        return Portfolio.objects.filter(user=user).prefetch_related("holdings__asset")

    @staticmethod
    def calculate_portfolio_value(portfolio: Portfolio) -> Decimal:
        value = Decimal("0")
        for holding in portfolio.holdings.all():
            latest_price = holding.asset.prices.order_by("-date").first()
            if latest_price:
                value += latest_price.close * holding.quantity
        return value.quantize(Decimal("0.01"))
