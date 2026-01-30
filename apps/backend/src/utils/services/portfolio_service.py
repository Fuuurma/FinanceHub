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
        holdings = portfolio.holdings.select_related("asset").filter(is_deleted=False)
        for holding in holdings:
            price = holding.asset.last_price
            if price:
                value += price * holding.quantity
        return value.quantize(Decimal("0.01"))
