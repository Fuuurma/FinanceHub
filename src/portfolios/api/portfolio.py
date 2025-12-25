# apps/portfolios/api.py
from typing import List
from django.shortcuts import get_object_or_404
from ninja import Router
from portfolios.models.portfolio import Portfolio
from users.api.auth.helpers import AuthBearer

router = Router(tags=["Portfolios"], auth=AuthBearer())


@router.get("/", response=List[PortfolioOut])
def list_portfolios(request):
    return Portfolio.objects.filter(user=request.auth)


@router.post("/", response={201: PortfolioOut})
def create_portfolio(request, payload: PortfolioIn):
    portfolio = Portfolio.objects.create(user=request.auth, **payload.dict())
    return 201, portfolio
