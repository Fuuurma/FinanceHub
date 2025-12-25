# investments/schemas.py
from pydantic import BaseModel, Field, Decimal
from typing import Optional, List, Literal
from datetime import date, datetime
from decimal import Decimal


class AssetOut(BaseModel):
    id: str
    ticker: str
    name: str
    asset_class: str
    asset_type: str
    currency: str
    market: Optional[str]
    country: Optional[str]

    class Config:
        from_attributes = True


class PriceOut(BaseModel):
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Optional[int]


class PriceCreate(BaseModel):
    date: date
    open: Decimal = Field(..., gt=0)
    high: Decimal = Field(..., gt=0)
    low: Decimal = Field(..., gt=0)
    close: Decimal = Field(..., gt=0)
    volume: Optional[int] = None


class PortfolioOut(BaseModel):
    id: str
    name: str
    description: Optional[str]
    base_currency: str
    is_public: bool
    current_value: Optional[Decimal] = None  # Computed
    total_return_pct: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    base_currency: str = Field("USD", max_length=3)
    is_public: bool = False


class HoldingOut(BaseModel):
    id: str
    asset: AssetOut
    quantity: Decimal
    average_buy_price: Optional[Decimal]
    current_price: Optional[Decimal]
    current_value: Optional[Decimal]
    unrealized_pnl: Optional[Decimal]


class HoldingCreate(BaseModel):
    asset_id: str
    quantity: Decimal = Field(..., gt=0)


class TransactionType(str):
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    SPLIT = "split"


class TransactionOut(BaseModel):
    id: str
    transaction_type: str
    asset: AssetOut
    quantity: Optional[Decimal]
    price_per_share: Decimal
    total_amount: Decimal
    fees: Decimal
    date: datetime
    notes: Optional[str]


class TransactionCreate(BaseModel):
    transaction_type: Literal["buy", "sell", "dividend"]
    asset_id: str
    quantity: Optional[Decimal] = Field(None, gt=0)
    price_per_share: Decimal = Field(..., gt=0)
    fees: Decimal = Field(0, ge=0)
    date: datetime
    notes: Optional[str] = None

    def validate(self):
        if self.transaction_type in ["buy", "sell"] and self.quantity is None:
            raise ValueError("Quantity required for buy/sell")
