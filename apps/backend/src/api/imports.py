import io
from typing import Optional
from ninja import Router, File
from ninja.files import UploadedFile
from django.http import HttpResponse
from django.db import transaction
from pydantic import BaseModel

router = Router()


class PreviewResponse(BaseModel):
    valid_count: int
    error_count: int
    rows: list
    errors: list


class ImportResponse(BaseModel):
    success: bool
    message: str
    imported_count: int
    transactions: list


@router.get("/import/template/{format_type}")
def download_csv_template(request, format_type: str):
    from utils.import_.csv_parser import CSVImportParser

    available_formats = [f["id"] for f in CSVImportParser.get_available_formats()]
    if format_type not in available_formats:
        format_type = "generic"

    template = CSVImportParser.get_template(format_type)

    response = HttpResponse(template, content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="portfolio_import_{format_type}.csv"'
    )
    return response


@router.get("/import/formats")
def get_available_formats(request):
    from ..utils.import_.csv_parser import CSVImportParser

    return CSVImportParser.get_available_formats()


@router.post("/import/preview", response=PreviewResponse)
def preview_import(
    request,
    csv_file: UploadedFile = File(...),
    format_type: str = "generic",
    portfolio_id: Optional[str] = None,
):
    from ..utils.import_.csv_parser import CSVImportParser
    from investments.models import Portfolio, Transaction

    content = csv_file.read().decode("utf-8")

    available_formats = [f["id"] for f in CSVImportParser.get_available_formats()]
    if format_type not in available_formats:
        format_type = "generic"

    parser = CSVImportParser(format_type)
    valid_rows, errors = parser.parse_csv(content)

    existing_transactions = set()
    if portfolio_id:
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
            existing = Transaction.objects.filter(portfolio=portfolio).values_list(
                "transaction_date", "asset__symbol", "transaction_type", "quantity"
            )
            existing_transactions = set(existing)

            duplicates = []
            for i, row in enumerate(valid_rows):
                key = (
                    row["transaction_date"],
                    row["asset_symbol"],
                    row["transaction_type"],
                    row["quantity"],
                )
                if key in existing_transactions:
                    duplicates.append(
                        {
                            "row": i + 2,
                            "message": f"Duplicate transaction: {row['asset_symbol']} {row['transaction_type']} {row['quantity']} on {row['transaction_date'].strftime('%Y-%m-%d')}",
                        }
                    )

            errors.extend(duplicates)
        except Portfolio.DoesNotExist:
            errors.append({"row": 0, "message": "Portfolio not found"})

    return PreviewResponse(
        valid_count=len(valid_rows),
        error_count=len(errors),
        rows=valid_rows,
        errors=errors,
    )


@router.post("/import/confirm", response=ImportResponse)
def confirm_import(
    request,
    csv_file: UploadedFile = File(...),
    format_type: str = "generic",
    portfolio_id: str = None,
):
    from ..utils.import_.csv_parser import CSVImportParser
    from investments.models import Portfolio, Transaction, Asset

    if not portfolio_id:
        return ImportResponse(
            success=False,
            message="Portfolio ID is required",
            imported_count=0,
            transactions=[],
        )

    content = csv_file.read().decode("utf-8")

    available_formats = [f["id"] for f in CSVImportParser.get_available_formats()]
    if format_type not in available_formats:
        format_type = "generic"

    parser = CSVImportParser(format_type)
    valid_rows, errors = parser.parse_csv(content)

    if errors:
        return ImportResponse(
            success=False,
            message=f"Cannot import with {len(errors)} errors",
            imported_count=0,
            transactions=[],
        )

    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return ImportResponse(
            success=False,
            message="Portfolio not found",
            imported_count=0,
            transactions=[],
        )

    with transaction.atomic():
        created_transactions = []
        created_assets = []

        for row_data in valid_rows:
            asset, asset_created = Asset.objects.get_or_create(
                symbol=row_data["asset_symbol"],
                defaults={"name": row_data["asset_symbol"], "asset_type": "stock"},
            )
            if asset_created:
                created_assets.append(asset.symbol)

            transaction_obj = Transaction.objects.create(
                portfolio=portfolio,
                asset=asset,
                transaction_type=row_data["transaction_type"],
                transaction_date=row_data["transaction_date"],
                quantity=row_data["quantity"],
                price_per_share=row_data["price_per_share"],
                total_value=row_data["total_value"],
                commission=row_data.get("commission", 0),
                notes=row_data.get("notes", ""),
            )
            created_transactions.append(transaction_obj.id)

    message = f"Successfully imported {len(created_transactions)} transactions"
    if created_assets:
        message += (
            f" (created {len(created_assets)} new assets: {', '.join(created_assets)})"
        )

    return ImportResponse(
        success=True,
        message=message,
        imported_count=len(created_transactions),
        transactions=created_transactions,
    )


@router.post("/import/holdings", response=ImportResponse)
def import_holdings_csv(
    request,
    csv_file: UploadedFile = File(...),
    format_type: str = "generic",
    portfolio_id: str = None,
):
    from ..utils.import_.csv_parser import CSVImportParser
    from investments.models import Portfolio, Asset, PortfolioPosition
    from django.utils import timezone

    if not portfolio_id:
        return ImportResponse(
            success=False,
            message="Portfolio ID is required",
            imported_count=0,
            transactions=[],
        )

    content = csv_file.read().decode("utf-8")

    available_formats = [f["id"] for f in CSVImportParser.get_available_formats()]
    if format_type not in available_formats:
        format_type = "generic"

    parser = CSVImportParser(format_type)
    valid_rows, errors = parser.parse_csv(content)

    if errors:
        return ImportResponse(
            success=False,
            message=f"Cannot import with {len(errors)} errors",
            imported_count=0,
            transactions=[],
        )

    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
    except Portfolio.DoesNotExist:
        return ImportResponse(
            success=False,
            message="Portfolio not found",
            imported_count=0,
            transactions=[],
        )

    with transaction.atomic():
        positions_created = []

        for row_data in valid_rows:
            asset, asset_created = Asset.objects.get_or_create(
                symbol=row_data["asset_symbol"],
                defaults={"name": row_data["asset_symbol"], "asset_type": "stock"},
            )

            position, created = PortfolioPosition.objects.update_or_create(
                portfolio=portfolio,
                asset=asset,
                defaults={
                    "quantity": row_data["quantity"],
                    "average_cost": row_data["price_per_share"],
                    "current_price": row_data["price_per_share"],
                    "market_value": row_data["quantity"] * row_data["price_per_share"],
                    "last_updated": timezone.now(),
                },
            )
            if created:
                positions_created.append(asset.symbol)

    message = f"Successfully imported {len(valid_rows)} holdings"
    if positions_created:
        message += f" (created {len(positions_created)} new positions)"

    return ImportResponse(
        success=True, message=message, imported_count=len(valid_rows), transactions=[]
    )
