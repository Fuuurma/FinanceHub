import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from django.utils.dateparse import parse_date


class CSVImportParser:
    """Parse and validate CSV imports for portfolios"""

    FORMAT_TEMPLATES = {
        "generic": {
            "required_columns": ["date", "symbol", "type", "quantity", "price"],
            "optional_columns": ["notes", "commission"],
            "column_mapping": {
                "date": "transaction_date",
                "symbol": "asset_symbol",
                "type": "transaction_type",
                "quantity": "quantity",
                "price": "price_per_share",
                "notes": "notes",
                "commission": "commission",
            },
        },
        "schwab": {
            "required_columns": ["Date", "Action", "Symbol", "Quantity", "Price"],
            "optional_columns": ["Description", "Commission"],
            "column_mapping": {
                "Date": "transaction_date",
                "Action": "transaction_type",
                "Symbol": "asset_symbol",
                "Quantity": "quantity",
                "Price": "price_per_share",
                "Description": "notes",
                "Commission": "commission",
            },
        },
        "fidelity": {
            "required_columns": ["Run Date", "Action", "Symbol", "Quantity", "Price"],
            "optional_columns": ["Description", "Commission"],
            "column_mapping": {
                "Run Date": "transaction_date",
                "Action": "transaction_type",
                "Symbol": "asset_symbol",
                "Quantity": "quantity",
                "Price": "price_per_share",
                "Description": "notes",
                "Commission": "commission",
            },
        },
        "etrade": {
            "required_columns": [
                "Date",
                "Transaction Type",
                "Symbol",
                "Quantity",
                "Price",
            ],
            "optional_columns": ["Description", "Commission"],
            "column_mapping": {
                "Date": "transaction_date",
                "Transaction Type": "transaction_type",
                "Symbol": "asset_symbol",
                "Quantity": "quantity",
                "Price": "price_per_share",
                "Description": "notes",
                "Commission": "commission",
            },
        },
        "robinhood": {
            "required_columns": ["Date", "Side", "Symbol", "Quantity", "Price"],
            "optional_columns": ["Result", "Notes"],
            "column_mapping": {
                "Date": "transaction_date",
                "Side": "transaction_type",
                "Symbol": "asset_symbol",
                "Quantity": "quantity",
                "Price": "price_per_share",
                "Notes": "notes",
            },
        },
        "vanguard": {
            "required_columns": [
                "Trade Date",
                "Transaction Type",
                "Ticker",
                "Quantity",
                "Price",
            ],
            "optional_columns": ["Commission", "Description"],
            "column_mapping": {
                "Trade Date": "transaction_date",
                "Transaction Type": "transaction_type",
                "Ticker": "asset_symbol",
                "Quantity": "quantity",
                "Price": "price_per_share",
                "Commission": "commission",
                "Description": "notes",
            },
        },
        "interactive_brokers": {
            "required_columns": ["DateTime", "Action", "Symbol", "Quantity", "Price"],
            "optional_columns": ["T. Price", "Comm", "Description"],
            "column_mapping": {
                "DateTime": "transaction_date",
                "Action": "transaction_type",
                "Symbol": "asset_symbol",
                "Quantity": "quantity",
                "Price": "price_per_share",
                "T. Price": "price_per_share",
                "Comm": "commission",
                "Description": "notes",
            },
        },
    }

    def __init__(self, format_type: str = "generic"):
        self.format_type = format_type
        self.template = self.FORMAT_TEMPLATES.get(
            format_type, self.FORMAT_TEMPLATES["generic"]
        )

    def parse_csv(
        self, csv_content: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        reader = csv.DictReader(csv_content.splitlines())
        valid_rows = []
        errors = []

        missing_cols = set(self.template["required_columns"]) - set(
            reader.fieldnames or []
        )
        if missing_cols:
            errors.append(
                {
                    "row": 0,
                    "message": f"Missing required columns: {', '.join(missing_cols)}",
                }
            )
            return valid_rows, errors

        for row_num, row in enumerate(reader, start=2):
            try:
                parsed_row = self._parse_row(row)
                validation_errors = self._validate_row(parsed_row)

                if validation_errors:
                    errors.extend(
                        [
                            {"row": row_num, "message": error}
                            for error in validation_errors
                        ]
                    )
                else:
                    valid_rows.append(parsed_row)

            except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
                errors.append({"row": row_num, "message": f"Parse error: {str(e)}"})

        return valid_rows, errors

    def _parse_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        parsed = {}

        for csv_col, db_field in self.template["column_mapping"].items():
            value = row.get(csv_col, "").strip()

            if not value and csv_col in self.template["required_columns"]:
                raise ValueError(f"Missing required value: {csv_col}")

            if db_field == "transaction_date":
                parsed[db_field] = self._parse_date(value)
            elif db_field in ["quantity", "price_per_share", "commission"]:
                parsed[db_field] = float(value) if value else 0.0
            elif db_field == "transaction_type":
                parsed[db_field] = self._normalize_transaction_type(value)
            else:
                parsed[db_field] = value

        parsed["total_value"] = parsed["quantity"] * parsed["price_per_share"]

        return parsed

    def _parse_date(self, date_str: str) -> datetime:
        if not date_str:
            raise ValueError("Date is required")

        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%Y%m%d",
            "%m-%d-%Y",
            "%d-%m-%Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d %b %Y",
            "%d %B %Y",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        parsed = parse_date(date_str)
        if not parsed:
            raise ValueError(f"Invalid date format: {date_str}")
        return datetime.combine(parsed, datetime.min.time())

    def _normalize_transaction_type(self, type_str: str) -> str:
        type_mapping = {
            "buy": "buy",
            "purchase": "buy",
            "bought": "buy",
            "order placed to buy": "buy",
            "sell": "sell",
            "sale": "sell",
            "sold": "sell",
            "order placed to sell": "sell",
            "dividend": "dividend",
            "div": "dividend",
            "dividend received": "dividend",
            "split": "split",
            "stock split": "split",
            "reinvest": "dividend_reinvest",
            "drip": "dividend_reinvest",
            "dividend reinvestment": "dividend_reinvest",
            "deposit": "deposit",
            "withdrawal": "withdrawal",
            "fee": "fee",
            "tax": "tax",
            "transfer": "transfer",
            "transfer in": "transfer",
            "transfer out": "transfer",
        }

        normalized = type_str.lower().strip()
        return type_mapping.get(normalized, normalized)

    def _validate_row(self, row: Dict[str, Any]) -> List[str]:
        errors = []

        if row["transaction_date"] > datetime.now():
            errors.append("Transaction date cannot be in the future")

        if row["quantity"] <= 0:
            errors.append("Quantity must be positive")

        tx_type = row["transaction_type"]
        if tx_type in ["buy", "sell"]:
            if row["price_per_share"] <= 0:
                errors.append("Price must be positive for buy/sell transactions")

        valid_types = [
            "buy",
            "sell",
            "dividend",
            "dividend_reinvest",
            "split",
            "deposit",
            "withdrawal",
            "fee",
            "tax",
            "transfer",
        ]
        if tx_type not in valid_types:
            errors.append(f"Invalid transaction type: {tx_type}")

        if row.get("asset_symbol") and len(row["asset_symbol"]) > 10:
            errors.append("Symbol too long (max 10 characters)")

        return errors

    @classmethod
    def get_template(cls, format_type: str = "generic") -> str:
        template = cls.FORMAT_TEMPLATES.get(
            format_type, cls.FORMAT_TEMPLATES["generic"]
        )

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[*template["required_columns"], *template["optional_columns"]],
        )
        writer.writeheader()

        examples = [
            {
                "date": "2024-01-15",
                "symbol": "AAPL",
                "type": "buy",
                "quantity": "100",
                "price": "150.25",
                "notes": "Initial investment",
                "commission": "9.99",
            },
            {
                "date": "2024-02-01",
                "symbol": "MSFT",
                "type": "buy",
                "quantity": "50",
                "price": "380.50",
                "notes": "",
                "commission": "7.99",
            },
            {
                "date": "2024-03-15",
                "symbol": "GOOGL",
                "type": "sell",
                "quantity": "25",
                "price": "175.00",
                "notes": "Take profit",
                "commission": "4.99",
            },
            {
                "date": "2024-04-01",
                "symbol": "AAPL",
                "type": "dividend",
                "quantity": "100",
                "price": "0.24",
                "notes": "Quarterly dividend",
                "commission": "0",
            },
        ]

        if format_type == "schwab":
            examples = [
                {
                    "Date": "01/15/2024",
                    "Action": "Buy",
                    "Symbol": "AAPL",
                    "Quantity": "100",
                    "Price": "150.25",
                    "Description": "Initial investment",
                    "Commission": "9.99",
                },
                {
                    "Date": "02/01/2024",
                    "Action": "Buy",
                    "Symbol": "MSFT",
                    "Quantity": "50",
                    "Price": "380.50",
                    "Description": "",
                    "Commission": "7.99",
                },
            ]
        elif format_type == "fidelity":
            examples = [
                {
                    "Run Date": "01/15/2024",
                    "Action": "Buy",
                    "Symbol": "AAPL",
                    "Quantity": "100",
                    "Price": "150.25",
                    "Description": "Initial investment",
                    "Commission": "9.99",
                },
                {
                    "Run Date": "02/01/2024",
                    "Action": "Buy",
                    "Symbol": "MSFT",
                    "Quantity": "50",
                    "Price": "380.50",
                    "Description": "",
                    "Commission": "7.99",
                },
            ]

        for example in examples:
            filtered_example = {
                k: v
                for k, v in example.items()
                if k in [*template["required_columns"], *template["optional_columns"]]
            }
            writer.writerow(filtered_example)

        return output.getvalue()

    @classmethod
    def get_available_formats(cls) -> List[Dict[str, str]]:
        return [
            {
                "id": "generic",
                "name": "Generic Format",
                "description": "Standard format with basic columns",
            },
            {
                "id": "schwab",
                "name": "Charles Schwab",
                "description": "Schwab brokerage export format",
            },
            {
                "id": "fidelity",
                "name": "Fidelity",
                "description": "Fidelity brokerage export format",
            },
            {
                "id": "etrade",
                "name": "E*TRADE",
                "description": "E*TRADE brokerage export format",
            },
            {
                "id": "robinhood",
                "name": "Robinhood",
                "description": "Robinhood app export format",
            },
            {
                "id": "vanguard",
                "name": "Vanguard",
                "description": "Vanguard brokerage export format",
            },
            {
                "id": "interactive_brokers",
                "name": "Interactive Brokers",
                "description": "IBKR export format",
            },
        ]
