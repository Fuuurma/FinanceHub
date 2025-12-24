from django.contrib import admin

from portfolios.models.holdings import Holding
from portfolios.models.portfolio import Portfolio
from portfolios.models.snapshot import PortfolioSnapshot

admin.site.register(Holding)
admin.site.register(Portfolio)
admin.site.register(PortfolioSnapshot)
