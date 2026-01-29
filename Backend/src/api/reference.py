"""
Reference Data API - Sectors, Industries, and Timezones
"""

from typing import List, Optional
from ninja import Router, Query
from pydantic import BaseModel
from django.db.models import Q

from assets.models.sector import Sector
from assets.models.industry import Industry
from assets.models.timezone import Timezone

router = Router(tags=["Reference Data"])


class SectorOut(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    gics_code: Optional[int]
    industry_count: int = 0

    class Config:
        from_attributes = True


class IndustryOut(BaseModel):
    id: str
    code: str
    name: str
    sector_id: str
    sector_name: str
    sector_code: str
    gics_code: Optional[int]
    asset_count: int = 0

    class Config:
        from_attributes = True


class TimezoneOut(BaseModel):
    id: str
    name: str
    utc_offset: int
    utc_offset_str: str
    abbreviation: str
    is_dst_observed: bool

    class Config:
        from_attributes = True


class SectorDetailOut(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    gics_code: Optional[int]
    industries: List[IndustryOut] = []

    class Config:
        from_attributes = True


@router.get("/sectors", response=List[SectorOut])
def list_sectors(request, active_only: bool = True):
    """
    List all GICS sectors.

    Returns sector information including code, name, description, and industry count.
    """
    qs = Sector.objects.all()
    if active_only:
        qs = qs.filter(is_active=True)

    sectors = []
    for sector in qs.order_by("gics_code"):
        industry_count = sector.industries.filter(is_active=True).count()
        sectors.append(
            SectorOut(
                id=str(sector.id),
                code=sector.code,
                name=sector.name,
                description=sector.description,
                gics_code=sector.gics_code,
                industry_count=industry_count,
            )
        )

    return sectors


@router.get("/sectors/{sector_id}", response=SectorDetailOut)
def get_sector(request, sector_id: str):
    """
    Get detailed sector information with all industries.
    """
    sector = Sector.objects.prefetch_related("industries").get(id=sector_id)

    industries = []
    for industry in sector.industries.filter(is_active=True).order_by("name"):
        industries.append(
            IndustryOut(
                id=str(industry.id),
                code=industry.code,
                name=industry.name,
                sector_id=str(sector.id),
                sector_name=sector.name,
                sector_code=sector.code,
                gics_code=industry.gics_code,
            )
        )

    return SectorDetailOut(
        id=str(sector.id),
        code=sector.code,
        name=sector.name,
        description=sector.description,
        gics_code=sector.gics_code,
        industries=industries,
    )


@router.get("/industries", response=List[IndustryOut])
def list_industries(
    request,
    sector_code: Optional[str] = None,
    active_only: bool = True,
):
    """
    List all industries.

    Can filter by sector_code to get industries for a specific sector.
    """
    qs = Industry.objects.select_related("sector").all()

    if active_only:
        qs = qs.filter(is_active=True)

    if sector_code:
        qs = qs.filter(sector__code__iexact=sector_code)

    industries = []
    for industry in qs.order_by("sector__name", "name"):
        industries.append(
            IndustryOut(
                id=str(industry.id),
                code=industry.code,
                name=industry.name,
                sector_id=str(industry.sector.id),
                sector_name=industry.sector.name,
                sector_code=industry.sector.code,
                gics_code=industry.gics_code,
            )
        )

    return industries


@router.get("/industries/{industry_id}", response=IndustryOut)
def get_industry(request, industry_id: str):
    """
    Get detailed industry information.
    """
    industry = Industry.objects.select_related("sector").get(id=industry_id)

    return IndustryOut(
        id=str(industry.id),
        code=industry.code,
        name=industry.name,
        sector_id=str(industry.sector.id),
        sector_name=industry.sector.name,
        sector_code=industry.sector.code,
        gics_code=industry.gics_code,
    )


@router.get("/timezones", response=List[TimezoneOut])
def list_timezones(request, active_only: bool = True):
    """
    List all timezones.

    Returns timezone information including name, UTC offset, and abbreviation.
    """
    qs = Timezone.objects.all()
    if active_only:
        qs = qs.filter(is_active=True)

    return list(qs.order_by("utc_offset", "name"))


@router.get("/timezones/{timezone_id}", response=TimezoneOut)
def get_timezone(request, timezone_id: str):
    """
    Get detailed timezone information.
    """
    tz = Timezone.objects.get(id=timezone_id)
    return tz


@router.get("/sectors/search")
def search_sectors(request, q: str):
    """
    Search sectors by name or code.
    """
    sectors = Sector.objects.filter(
        Q(name__icontains=q) | Q(code__icontains=q), is_active=True
    )[:10]

    return [{"id": str(s.id), "code": s.code, "name": s.name} for s in sectors]


@router.get("/industries/search")
def search_industries(request, q: str, sector_code: Optional[str] = None):
    """
    Search industries by name or code.
    """
    qs = Industry.objects.filter(
        Q(name__icontains=q) | Q(code__icontains=q), is_active=True
    )

    if sector_code:
        qs = qs.filter(sector__code__iexact=sector_code)

    return [
        {
            "id": str(i.id),
            "code": i.code,
            "name": i.name,
            "sector_code": i.sector.code,
            "sector_name": i.sector.name,
        }
        for i in qs[:10]
    ]
