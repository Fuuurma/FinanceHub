# 🎯 TASK C-010: Custom Screener Save/Load System

**Created:** January 30, 2026
**Assigned To:** Frontend Coder
**Priority:** P1 - HIGH
**Estimated Time:** 6-8 hours
**Status:** ⏳ PENDING

---

## 📋 OVERVIEW

Implement custom screener save/load functionality, allowing users to:
- Save custom screening criteria as presets
- Load previously saved screeners
- Delete saved screeners
- Share screener presets (optional)
- Rename saved screeners

**User Value:** High - Saves time for recurring screening queries
**Complexity:** Medium
**Dependencies:** Screener page exists (confirmed in FEEDBACK_EXCELLENT_WORK.md)

---

## 🎯 SUCCESS CRITERIA

- [x] User can save current screener filters as a named preset
- [x] User can load a saved screener preset
- [x] User can delete saved presets
- [x] User can rename saved presets
- [x] Presets persist across sessions (backend storage)
- [x] UI shows list of saved presets
- [x] Presets display summary (filter count, last modified)

---

## 📁 FILES TO CREATE/MODIFY

### Frontend Files:

**1. Create Screener Presets Types**
```typescript
// apps/frontend/src/types/screener.ts
export interface ScreenerPreset {
  id: string;
  name: string;
  filters: ScreenerFilters;
  created_at: string;
  updated_at: string;
  is_public?: boolean; // Future feature
}

export interface ScreenerFilters {
  marketCap?: { min: number; max: number };
  sector?: string[];
  peRatio?: { min: number; max: number };
  dividendYield?: { min: number; max: number };
  volume?: { min: number };
  technicalIndicators?: {
    rsi?: { min: number; max: number };
    macd?: string;
  };
  regions?: string[];
  // Add other filter types
}
```

**2. Create Screener Preset Store**
```typescript
// apps/frontend/src/stores/screenerPresets.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ScreenerPresetsStore {
  presets: ScreenerPreset[];
  addPreset: (name: string, filters: ScreenerFilters) => Promise<void>;
  loadPreset: (id: string) => Promise<ScreenerFilters>;
  deletePreset: (id: string) => Promise<void>;
  renamePreset: (id: string, newName: string) => Promise<void>;
}

export const useScreenerPresets = create<ScreenerPresetsStore>()(
  persist(
    (set, get) => ({
      presets: [],
      addPreset: async (name, filters) => {
        // API call to save preset
      },
      loadPreset: async (id) => {
        // API call to load preset
      },
      deletePreset: async (id) => {
        // API call to delete preset
      },
      renamePreset: async (id, newName) => {
        // API call to rename preset
      },
    }),
    { name: 'screener-presets' }
  )
);
```

**3. Update Screener Page**
```typescript
// apps/frontend/src/app/(dashboard)/screener/page.tsx

// Add Save/Load UI components
// Add preset dropdown/list
// Add preset management (rename, delete)
```

**4. Create Preset Management Components**
```typescript
// apps/frontend/src/components/screener/PresetList.tsx
// - List saved presets
// - Show preset summary (name, filter count, date)
// - Load button
// - Delete button
// - Rename button

// apps/frontend/src/components/screener/SavePresetDialog.tsx
// - Input for preset name
// - Save button
// - Cancel button

// apps/frontend/src/components/screener/RenamePresetDialog.tsx
// - Input for new name
// - Save button
// - Cancel button
```

### Backend Files:

**5. Create Screener Preset Model**
```python
# apps/backend/src/investments/models/screener_preset.py
from django.db import models
from django.contrib.auth.models import User

class ScreenerPreset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='screener_presets')
    name = models.CharField(max_length=255)
    filters = models.JSONField()  # Store filter criteria
    is_public = models.BooleanField(default=False)  # For future sharing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']  # User can't have duplicate names

    def __str__(self):
        return f"{self.user.username}'s {self.name}"
```

**6. Create Screener Preset API**
```python
# apps/backend/src/api/screener_presets.py
from ninja import Router
from django.contrib.auth.models import User
from .models.screener_preset import ScreenerPreset

router = Router()

@router.get("/presets")
def list_presets(request):
    """List all presets for current user"""
    presets = ScreenerPreset.objects.filter(user=request.auth)
    return [{"id": p.id, "name": p.name, "filters": p.filters, 
             "created_at": p.created_at, "updated_at": p.updated_at} 
            for p in presets]

@router.post("/presets")
def create_preset(request, name: str, filters: dict):
    """Save a new screener preset"""
    preset = ScreenerPreset.objects.create(
        user=request.auth,
        name=name,
        filters=filters
    )
    return {"id": preset.id, "name": preset.name, "success": True}

@router.get("/presets/{preset_id}")
def get_preset(request, preset_id: str):
    """Get a specific preset"""
    preset = ScreenerPreset.objects.get(id=preset_id, user=request.auth)
    return {"id": preset.id, "name": preset.name, "filters": preset.filters}

@router.put("/presets/{preset_id}")
def update_preset(request, preset_id: str, name: str = None, filters: dict = None):
    """Update a preset (rename)"""
    preset = ScreenerPreset.objects.get(id=preset_id, user=request.auth)
    if name:
        preset.name = name
    if filters:
        preset.filters = filters
    preset.save()
    return {"success": True}

@router.delete("/presets/{preset_id}")
def delete_preset(request, preset_id: str):
    """Delete a preset"""
    preset = ScreenerPreset.objects.get(id=preset_id, user=request.auth)
    preset.delete()
    return {"success": True}
```

**7. Update URLs**
```python
# apps/backend/src/api/urls.py
from .screener_presets import router as screener_presets_router

api.add_router("/screener", screener_presets_router)
```

---

## 🔧 IMPLEMENTATION STEPS

### Phase 1: Backend API (2-3 hours)
1. Create `ScreenerPreset` model
2. Run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Create API endpoints (CRUD operations)
4. Test API with curl/Postman

### Phase 2: Frontend Store (1 hour)
1. Create TypeScript types for presets
2. Create Zustand store with persistence
3. Add API integration to store actions
4. Test store with manual API calls

### Phase 3: UI Components (2-3 hours)
1. Create `PresetList` component
2. Create `SavePresetDialog` component
3. Create `RenamePresetDialog` component
4. Add components to screener page
5. Style components (match existing design)

### Phase 4: Integration & Testing (1-2 hours)
1. Connect filters state to preset save/load
2. Test saving preset with various filter combinations
3. Test loading preset restores filters correctly
4. Test delete and rename operations
5. Test persistence across page refreshes
6. Test with different users (isolation)

---

## 🧪 TESTING CHECKLIST

### API Tests:
- [ ] POST /api/screener/presets - Create preset
- [ ] GET /api/screener/presets - List user's presets
- [ ] GET /api/screener/presets/{id} - Get specific preset
- [ ] PUT /api/screener/presets/{id} - Rename preset
- [ ] DELETE /api/screener/presets/{id} - Delete preset
- [ ] Verify user cannot access another user's presets
- [ ] Verify duplicate names prevented for same user

### Frontend Tests:
- [ ] Save button creates preset
- [ ] Preset appears in list after saving
- [ ] Load button restores filters correctly
- [ ] Delete button removes preset from list
- [ ] Rename button updates preset name
- [ ] Presets persist across page refresh
- [ ] Presets persist across browser sessions (zustand persist)
- [ ] Empty state shown when no presets saved
- [ ] Loading states shown during API calls
- [ ] Error handling for API failures

### E2E Tests:
- [ ] User saves screener with complex filters
- [ ] User refreshes page, loads saved preset
- [ ] User modifies loaded preset and saves as new preset
- [ ] User deletes preset, it disappears from list
- [ ] Multiple users each have their own presets

---

## 📊 API SPECIFICATION

### POST /api/screener/presets
**Request:**
```json
{
  "name": "Tech Growth Stocks",
  "filters": {
    "sector": ["Technology", "Software"],
    "marketCap": { "min": 1000000000 },
    "peRatio": { "max": 30 },
    "dividendYield": { "min": 0 }
  }
}
```
**Response:**
```json
{
  "id": "uuid-here",
  "name": "Tech Growth Stocks",
  "success": true
}
```

### GET /api/screener/presets
**Response:**
```json
[
  {
    "id": "uuid-here",
    "name": "Tech Growth Stocks",
    "filters": { ... },
    "created_at": "2026-01-30T10:00:00Z",
    "updated_at": "2026-01-30T10:00:00Z"
  }
]
```

---

## 🎨 UI DESIGN

### Preset List (Sidebar):
```
┌─────────────────────────────┐
│ Saved Screeners          [+] │
├─────────────────────────────┤
│ Tech Growth Stocks         │
│ 5 filters • 2 hours ago    │
│ [Load] [Rename] [Delete]   │
├─────────────────────────────┤
│ Dividend Aristocrats       │
│ 3 filters • Yesterday      │
│ [Load] [Rename] [Delete]   │
├─────────────────────────────┤
│ Value Stocks               │
│ 4 filters • 3 days ago     │
│ [Load] [Rename] [Delete]   │
└─────────────────────────────┘
```

### Save Preset Dialog:
```
┌─────────────────────────────┐
│ Save Screener Preset        │
├─────────────────────────────┤
│ Name: [Tech Growth Stocks]  │
│                             │
│ [Cancel]        [Save]      │
└─────────────────────────────┘
```

---

## 🚀 FUTURE ENHANCEMENTS

**Phase 2 (Optional):**
- Share presets with other users
- Community preset library
- Import/export presets (JSON)
- Preset categories/tags
- Preset search
- Preset analytics (most used, etc.)

---

## 📚 REFERENCES

- Existing screener page: `apps/frontend/src/app/(dashboard)/screener/page.tsx`
- Zustand docs: https://docs.pmnd.rs/zustand
- Django Ninja: https://django-ninja.rest-framework.com

---

## 🎯 PRIORITY RATIONALE

**Why P1 (HIGH):**
- High user value (saves time)
- Low implementation complexity
- Builds on existing screener functionality
- No external dependencies
- Quick win (6-8 hours)

**User Impact:** 9/10 - Frequently requested feature
**Dev Effort:** 4/10 - Straightforward CRUD
**Risk:** 2/10 - Low risk, well-defined scope

---

**Task created by GAUDÍ (Architect)**
**Ready for assignment to Frontend Coder**
**Part of Screener Enhancement Suite**
