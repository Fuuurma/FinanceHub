from decimal import Decimal
from django.db import models

from fundamentals.base import PeriodFundamental


class IncomeStatement(PeriodFundamental):
    """
    Income statement (statement of earnings) for a reporting period.
    Tracks revenue, expenses, and profitability.
    """

    class Meta(PeriodFundamental.Meta):
        db_table = "fundamentals_income_statement"
        verbose_name = "Income Statement"
        verbose_name_plural = "Income Statements"

    total_revenue = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total revenue in USD",
    )

    cost_of_revenue = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost of revenue in USD",
    )

    gross_profit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Gross profit in USD",
    )

    research_and_development = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="R&D expenses in USD",
    )

    selling_general_and_admin = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="SG&A expenses in USD",
    )

    operating_expenses = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total operating expenses in USD",
    )

    operating_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Operating income in USD",
    )

    interest_expense = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Interest expense in USD",
    )

    interest_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Interest income in USD",
    )

    net_interest_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net interest income in USD",
    )

    other_income_expense = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other income/expense in USD",
    )

    pre_tax_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Pre-tax income in USD",
    )

    income_tax_expense = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Income tax expense in USD",
    )

    income_tax_rate = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Effective income tax rate as decimal",
    )

    net_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net income in USD",
    )

    ebitda = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="EBITDA in USD",
    )

    ebit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="EBIT in USD",
    )

    basic_eps = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Basic earnings per share",
    )

    diluted_eps = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Diluted earnings per share",
    )

    basic_shares_outstanding = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Basic weighted average shares outstanding",
    )

    diluted_shares_outstanding = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="Diluted weighted average shares outstanding",
    )

    depreciation = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Depreciation expense in USD",
    )

    amortization = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amortization expense in USD",
    )

    stock_based_compensation = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Stock-based compensation in USD",
    )

    other_non_cash_items = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other non-cash items in USD",
    )

    change_in_working_capital = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Change in working capital in USD",
    )

    net_income_from_continuing_ops = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net income from continuing operations in USD",
    )

    net_income_from_discontinued_ops = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net income from discontinued operations in USD",
    )

    extraordinary_items = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Extraordinary items in USD",
    )

    minority_interest = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minority interest in USD",
    )

    preferred_dividends = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Preferred dividends in USD",
    )

    income_available_to_common = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Income available to common shareholders in USD",
    )


class BalanceSheet(PeriodFundamental):
    """
    Balance sheet for a reporting period.
    Tracks assets, liabilities, and equity.
    """

    class Meta(PeriodFundamental.Meta):
        db_table = "fundamentals_balance_sheet"
        verbose_name = "Balance Sheet"
        verbose_name_plural = "Balance Sheets"

    cash_and_equivalents = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cash and cash equivalents in USD",
    )

    short_term_investments = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Short-term investments in USD",
    )

    cash_and_short_term_investments = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cash and short-term investments in USD",
    )

    accounts_receivable = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Accounts receivable in USD",
    )

    inventory = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Inventory in USD",
    )

    prepaid_expenses = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Prepaid expenses in USD",
    )

    other_current_assets = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other current assets in USD",
    )

    total_current_assets = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total current assets in USD",
    )

    property_plant_equipment = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Property, plant, and equipment in USD",
    )

    goodwill = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Goodwill in USD",
    )

    intangible_assets = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Intangible assets in USD",
    )

    long_term_investments = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Long-term investments in USD",
    )

    other_long_term_assets = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other long-term assets in USD",
    )

    total_assets = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total assets in USD",
    )

    accounts_payable = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Accounts payable in USD",
    )

    accrued_expenses = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Accrued expenses in USD",
    )

    short_term_debt = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Short-term debt in USD",
    )

    current_portion_of_long_term_debt = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current portion of long-term debt in USD",
    )

    other_current_liabilities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other current liabilities in USD",
    )

    total_current_liabilities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total current liabilities in USD",
    )

    long_term_debt = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Long-term debt in USD",
    )

    deferred_tax_liabilities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Deferred tax liabilities in USD",
    )

    minority_interest = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minority interest in USD",
    )

    other_long_term_liabilities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other long-term liabilities in USD",
    )

    total_liabilities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total liabilities in USD",
    )

    common_stock = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Common stock in USD",
    )

    additional_paid_in_capital = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Additional paid-in capital in USD",
    )

    retained_earnings = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Retained earnings in USD",
    )

    treasury_stock = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Treasury stock in USD",
    )

    accumulated_other_comprehensive_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Accumulated other comprehensive income in USD",
    )

    total_stockholders_equity = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total stockholders' equity in USD",
    )

    total_equity = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total equity in USD",
    )

    total_liabilities_and_equity = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total liabilities and equity in USD",
    )


class CashFlowStatement(PeriodFundamental):
    """
    Statement of cash flows for a reporting period.
    Tracks operating, investing, and financing cash flows.
    """

    class Meta(PeriodFundamental.Meta):
        db_table = "fundamentals_cash_flow_statement"
        verbose_name = "Cash Flow Statement"
        verbose_name_plural = "Cash Flow Statements"

    net_income = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net income from income statement in USD",
    )

    depreciation = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Depreciation and amortization in USD",
    )

    stock_based_compensation = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Stock-based compensation in USD",
    )

    deferred_tax = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Deferred tax expense in USD",
    )

    change_in_working_capital = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Change in working capital in USD",
    )

    accounts_receivable_change = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Change in accounts receivable in USD",
    )

    inventory_change = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Change in inventory in USD",
    )

    accounts_payable_change = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Change in accounts payable in USD",
    )

    other_working_capital_changes = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other working capital changes in USD",
    )

    operating_cash_flow = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net cash from operating activities in USD",
    )

    capital_expenditures = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Capital expenditures (CapEx) in USD",
    )

    acquisition_of_businesses = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Acquisition of businesses in USD",
    )

    purchases_of_investments = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Purchases of investments in USD",
    )

    sales_of_investments = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Sales of investments in USD",
    )

    other_investing_activities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other investing activities in USD",
    )

    investing_cash_flow = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net cash from investing activities in USD",
    )

    debt_issued = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Debt issued in USD",
    )

    debt_repayment = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Debt repayment in USD",
    )

    common_stock_issued = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Common stock issued in USD",
    )

    common_stock_repurchased = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Common stock repurchased in USD",
    )

    dividends_paid = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Dividends paid in USD",
    )

    other_financing_activities = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Other financing activities in USD",
    )

    financing_cash_flow = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net cash from financing activities in USD",
    )

    effect_of_exchange_rate_changes = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Effect of exchange rate changes in USD",
    )

    net_change_in_cash = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Net change in cash in USD",
    )

    free_cash_flow = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Free cash flow in USD (Operating CF - CapEx)",
    )

    free_cash_flow_per_share = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Free cash flow per share",
    )

    free_cash_flow_yoy_growth = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Year-over-year free cash flow growth",
    )

    cash_at_beginning = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cash at beginning of period in USD",
    )

    cash_at_end = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cash at end of period in USD",
    )
