# C-014: Interactive Chart Drawing Tools

**Priority:** P1 - HIGH  
**Assigned to:** Frontend Coder  
**Estimated Time:** 12-16 hours  
**Dependencies:** C-005 (Frontend Completion)  
**Status:** ⏳ PENDING

---

## 🎯 OBJECTIVE

Implement interactive chart drawing tools including trendlines, support/resistance, and Fibonacci retracements.

---

## 📊 FEATURE DESCRIPTION

**From Features Specification (Section 2.2 - Charts & Visualization):**

- Drawing tools (trendlines, support/resistance)
- Fibonacci retracements
- Chart screenshots & sharing
- Full-screen chart mode

---

## ✅ CURRENT STATE

**What exists:**
- Basic price charts with TradingView widgets
- Chart component in `apps/frontend/src/components/charts/`

**What's missing:**
- Custom drawing tools
- Annotation persistence
- Screenshot functionality
- Sharing capabilities

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Chart Drawing Component** (5-6 hours)

**Create `apps/frontend/src/components/charts/ChartDrawings.tsx`:**

```typescript
import React, { useState, useRef, useEffect } from 'react';
import { useChartStore } from '@/stores/chartStore';

interface Drawing {
  id: string;
  type: 'trendline' | 'support' | 'resistance' | 'fibonacci';
  points: { x: number; y: number }[];
  color: string;
  timestamp: number;
}

export const ChartDrawings: React.FC = () => {
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [currentTool, setCurrentTool] = useState<string>('none');
  const [isDrawing, setIsDrawing] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const loadDrawings = useChartStore(state => state.loadDrawings);
  const saveDrawing = useChartStore(state => state.saveDrawing);
  
  useEffect(() => {
    // Load saved drawings from backend
    loadDrawings().then(setDrawings);
  }, []);
  
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (currentTool === 'none') return;
    
    const rect = canvasRef.current?.getBoundingClientRect();
    const x = e.clientX - (rect?.left || 0);
    const y = e.clientY - (rect?.top || 0);
    
    if (isDrawing) {
      // Complete drawing
      const newDrawing: Drawing = {
        id: Date.now().toString(),
        type: currentTool as any,
        points: [{ x, y }],
        color: getCurrentColor(),
        timestamp: Date.now()
      };
      
      setDrawings([...drawings, newDrawing]);
      saveDrawing(newDrawing);
      setIsDrawing(false);
    } else {
      // Start drawing
      setIsDrawing(true);
    }
  };
  
  const renderDrawings = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw all drawings
    drawings.forEach(drawing => {
      ctx.beginPath();
      ctx.strokeStyle = drawing.color;
      ctx.lineWidth = 2;
      
      if (drawing.type === 'trendline' || drawing.type === 'support' || drawing.type === 'resistance') {
        ctx.moveTo(drawing.points[0].x, drawing.points[0].y);
        ctx.lineTo(drawing.points[1]?.x || drawing.points[0].x, drawing.points[1]?.y || drawing.points[0].y);
      } else if (drawing.type === 'fibonacci') {
        // Draw Fibonacci levels
        const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
        levels.forEach(level => {
          const y = drawing.points[0].y + (drawing.points[1]?.y - drawing.points[0].y) * level;
          ctx.moveTo(0, y);
          ctx.lineTo(canvas.width, y);
        });
      }
      
      ctx.stroke();
    });
  };
  
  useEffect(() => {
    renderDrawings();
  }, [drawings]);
  
  return (
    <div className="chart-drawings">
      <div className="drawing-toolbar">
        <button onClick={() => setCurrentTool('trendline')}>Trendline</button>
        <button onClick={() => setCurrentTool('support')}>Support</button>
        <button onClick={() => setCurrentTool('resistance')}>Resistance</button>
        <button onClick={() => setCurrentTool('fibonacci')}>Fibonacci</button>
        <button onClick={() => setCurrentTool('none')}>Cursor</button>
        <button onClick={handleScreenshot}>Screenshot</button>
        <button onClick={handleShare}>Share</button>
      </div>
      
      <canvas
        ref={canvasRef}
        onClick={handleCanvasClick}
        width={800}
        height={400}
      />
    </div>
  );
};
```

---

### **Phase 2: Drawing Persistence** (3-4 hours)

**Create Zustand store `apps/frontend/src/stores/chartStore.ts`:**

```typescript
import { create } from 'zustand';
import api from '@/lib/api';

interface Drawing {
  id: string;
  type: string;
  points: { x: number; y: number }[];
  color: string;
  timestamp: number;
}

interface ChartStore {
  drawings: Drawing[];
  loadDrawings: () => Promise<Drawing[]>;
  saveDrawing: (drawing: Drawing) => Promise<void>;
  deleteDrawing: (id: string) => Promise<void>;
  clearAllDrawings: () => Promise<void>;
}

export const useChartStore = create<ChartStore>((set, get) => ({
  drawings: [],
  
  loadDrawings: async () => {
    try {
      const response = await api.get('/api/chart/drawings/');
      set({ drawings: response.data });
      return response.data;
    } catch (error) {
      console.error('Failed to load drawings:', error);
      return [];
    }
  },
  
  saveDrawing: async (drawing) => {
    try {
      await api.post('/api/chart/drawings/', drawing);
      const { drawings } = get();
      set({ drawings: [...drawings, drawing] });
    } catch (error) {
      console.error('Failed to save drawing:', error);
    }
  },
  
  deleteDrawing: async (id) => {
    try {
      await api.delete(`/api/chart/drawings/${id}/`);
      const { drawings } = get();
      set({ drawings: drawings.filter(d => d.id !== id) });
    } catch (error) {
      console.error('Failed to delete drawing:', error);
    }
  },
  
  clearAllDrawings: async () => {
    try {
      await api.delete('/api/chart/drawings/clear/');
      set({ drawings: [] });
    } catch (error) {
      console.error('Failed to clear drawings:', error);
    }
  }
}));
```

---

### **Phase 3: Screenshot Functionality** (2-3 hours)

**Add to ChartDrawings component:**

```typescript
const handleScreenshot = async () => {
  const canvas = canvasRef.current;
  if (!canvas) return;
  
  // Convert canvas to image
  const dataUrl = canvas.toDataURL('image/png');
  
  // Create download link
  const link = document.createElement('a');
  link.download = `chart-${Date.now()}.png`;
  link.href = dataUrl;
  link.click();
  
  // Optional: Upload to server for sharing
  try {
    const blob = await (await fetch(dataUrl)).blob();
    const formData = new FormData();
    formData.append('image', blob, 'chart.png');
    
    await api.post('/api/chart/screenshots/', formData);
  } catch (error) {
    console.error('Failed to upload screenshot:', error);
  }
};
```

---

### **Phase 4: Share Functionality** (2-3 hours)

**Add share handler:**

```typescript
const handleShare = async () => {
  const canvas = canvasRef.current;
  if (!canvas) return;
  
  // Generate shareable link
  const dataUrl = canvas.toDataURL('image/png');
  
  try {
    const response = await api.post('/api/chart/share/', {
      image: dataUrl,
      drawings: drawings
    });
    
    const shareUrl = `${window.location.origin}/chart/${response.data.shareId}`;
    
    // Copy to clipboard or show modal
    if (navigator.share) {
      await navigator.share({
        title: 'FinanceHub Chart',
        text: 'Check out this chart',
        url: shareUrl
      });
    } else {
      navigator.clipboard.writeText(shareUrl);
      alert('Share link copied to clipboard!');
    }
  } catch (error) {
    console.error('Failed to share:', error);
  }
};
```

---

### **Phase 5: Backend API** (2 hours)

**Backend: Create `apps/backend/src/api/chart_drawings.py`:**

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from investments.models import ChartDrawing

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chart_drawings(request):
    if request.method == 'GET':
        drawings = ChartDrawing.objects.filter(user=request.user)
        data = [{
            'id': d.id,
            'type': d.drawing_type,
            'points': d.points,
            'color': d.color,
            'timestamp': d.timestamp
        } for d in drawings]
        return Response(data)
    
    elif request.method == 'POST':
        drawing = ChartDrawing.objects.create(
            user=request.user,
            drawing_type=request.data['type'],
            points=request.data['points'],
            color=request.data['color']
        )
        return Response({'id': drawing.id}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_drawing(request, drawing_id):
    try:
        drawing = ChartDrawing.objects.get(id=drawing_id, user=request.user)
        drawing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ChartDrawing.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_chart(request):
    # Generate shareable link
    share_id = uuid.uuid4().hex[:8]
    # Save to cache or database
    return Response({'shareId': share_id, 'url': f'/chart/{share_id}'})
```

---

## 📋 DELIVERABLES

- [ ] ChartDrawings component with drawing tools
- [ ] Zustand store for persistence
- [ ] Screenshot functionality
- [ ] Share functionality
- [ ] Backend API endpoints
- [ ] Tests
- [ ] Documentation

---

## ✅ ACCEPTANCE CRITERIA

- [ ] 4 drawing tools working (trendline, support, resistance, fibonacci)
- [ ] Drawings persist across page reloads
- [ ] Screenshot downloads as PNG
- [ ] Share generates unique URL
- [ ] Drawings render correctly on canvas
- [ ] All tests passing

---

**Task created:** January 30, 2026  
**Task file:** tasks/coders/014-chart-drawing-tools.md
