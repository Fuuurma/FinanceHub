from decimal import Decimal, InvalidOperation
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from trading.services.paper_trading_service import PaperTradingService


class PaperTradingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = PaperTradingService()

    def list(self, request):
        account = self.service.get_or_create_account(request.user)
        summary = self.service.get_portfolio_summary(request.user)

        return Response(
            {
                "account": {
                    "cash_balance": float(account.cash_balance),
                    "starting_balance": float(account.starting_balance),
                    "total_trades": account.total_trades,
                    "win_rate": account.win_rate,
                    "reset_count": account.reset_count,
                },
                "summary": summary,
            }
        )

    @action(detail=False, methods=["post"])
    def buy(self, request):
        asset_symbol = request.data.get("asset")
        quantity = request.data.get("quantity")

        if not asset_symbol or not quantity:
            return Response(
                {"error": "asset and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = Decimal(str(quantity))
        except (InvalidOperation, ValueError):
            return Response(
                {"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST
            )

        result = self.service.execute_buy_order(request.user, asset_symbol, quantity)

        if not result.get("success"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)

    @action(detail=False, methods=["post"])
    def sell(self, request):
        asset_symbol = request.data.get("asset")
        quantity = request.data.get("quantity")

        if not asset_symbol or not quantity:
            return Response(
                {"error": "asset and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = Decimal(str(quantity))
        except (InvalidOperation, ValueError):
            return Response(
                {"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST
            )

        result = self.service.execute_sell_order(request.user, asset_symbol, quantity)

        if not result.get("success"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result)

    @action(detail=False, methods=["post"])
    def reset(self, request):
        account = self.service.get_or_create_account(request.user)
        account.reset_account()

        return Response(
            {
                "success": True,
                "message": "Account reset successfully",
                "new_balance": float(account.cash_balance),
            }
        )

    @action(detail=False, methods=["get"])
    def history(self, request):
        limit = int(request.query_params.get("limit", 100))
        trades = self.service.get_trade_history(request.user, limit)

        return Response({"trades": trades})

    @action(detail=False, methods=["get"])
    def performance(self, request):
        summary = self.service.get_portfolio_summary(request.user)

        return Response(
            {
                "total_return": summary["total_return"],
                "win_rate": summary["win_rate"],
                "total_trades": summary["total_trades"],
                "winning_trades": summary["winning_trades"],
                "losing_trades": summary["losing_trades"],
            }
        )
