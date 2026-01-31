from ninja import Router, Schema
from typing import List, Optional
from pydantic import BaseModel
from django.contrib.auth.models import User
from investments.models.screener_preset import ScreenerPreset
from django.db import IntegrityError

router = Router()


class ScreenerPresetCreate(BaseModel):
    name: str
    filters: dict


class ScreenerPresetUpdate(BaseModel):
    name: Optional[str] = None
    filters: Optional[dict] = None


class ScreenerPresetResponse(BaseModel):
    id: str
    name: str
    filters: dict
    is_public: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/presets", response=List[ScreenerPresetResponse])
def list_presets(request):
    """List all presets for current user"""
    if not request.user.is_authenticated:
        return []

    presets = ScreenerPreset.objects.filter(user=request.user)
    return [
        ScreenerPresetResponse(
            id=str(p.id),
            name=p.name,
            filters=p.filters,
            is_public=p.is_public,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
        )
        for p in presets
    ]


@router.post("/presets", response=ScreenerPresetResponse)
def create_preset(request, preset_data: ScreenerPresetCreate):
    """Save a new screener preset"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        preset = ScreenerPreset.objects.create(
            user=request.user, name=preset_data.name, filters=preset_data.filters
        )
        return ScreenerPresetResponse(
            id=str(preset.id),
            name=preset.name,
            filters=preset.filters,
            is_public=preset.is_public,
            created_at=preset.created_at.isoformat(),
            updated_at=preset.updated_at.isoformat(),
        )
    except IntegrityError:
        return {"error": "A preset with this name already exists"}, 400


@router.get("/presets/{preset_id}", response=ScreenerPresetResponse)
def get_preset(request, preset_id: str):
    """Get a specific preset"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        preset = ScreenerPreset.objects.get(id=preset_id, user=request.user)
        return ScreenerPresetResponse(
            id=str(preset.id),
            name=preset.name,
            filters=preset.filters,
            is_public=preset.is_public,
            created_at=preset.created_at.isoformat(),
            updated_at=preset.updated_at.isoformat(),
        )
    except ScreenerPreset.DoesNotExist:
        return {"error": "Preset not found"}, 404


@router.put("/presets/{preset_id}", response=ScreenerPresetResponse)
def update_preset(request, preset_id: str, preset_data: ScreenerPresetUpdate):
    """Update a preset (rename or update filters)"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        preset = ScreenerPreset.objects.get(id=preset_id, user=request.user)

        if preset_data.name:
            preset.name = preset_data.name
        if preset_data.filters is not None:
            preset.filters = preset_data.filters

        preset.save()

        return ScreenerPresetResponse(
            id=str(preset.id),
            name=preset.name,
            filters=preset.filters,
            is_public=preset.is_public,
            created_at=preset.created_at.isoformat(),
            updated_at=preset.updated_at.isoformat(),
        )
    except ScreenerPreset.DoesNotExist:
        return {"error": "Preset not found"}, 404
    except IntegrityError:
        return {"error": "A preset with this name already exists"}, 400


@router.delete("/presets/{preset_id}")
def delete_preset(request, preset_id: str):
    """Delete a preset"""
    if not request.user.is_authenticated:
        return {"error": "Authentication required"}, 401

    try:
        preset = ScreenerPreset.objects.get(id=preset_id, user=request.user)
        preset.delete()
        return {"success": True}
    except ScreenerPreset.DoesNotExist:
        return {"error": "Preset not found"}, 404
