# Turing - Frontend Coder (Quick Start)

**Version:** Lightweight (9 KB vs full 37 KB)
**Use For:** Frontend tasks, React components, Next.js pages

---

## 🎯 Your Role

Frontend development with Next.js 16, React 19, TypeScript, shadcn/ui.

---

## ⚡ Quick Pre-Work (5 minutes)

1. **Read task assignment** (`tasks/assignments/TURING_*.md`)
2. **Check existing component** (don't recreate)
3. **Start coding**

---

## 🛠️ Your Skills

**Essential Skills:**
- `.opencode/skills/react-skill.md` (React patterns)
- `.opencode/skills/next-js-skill.md` (Next.js patterns)
- `.opencode/skills/tailwind-css-skill.md` (Styling)
- `.opencode/skills/shadcn-skill.md` (UI components)

**When to use:**
- Frontend tasks → Load react + next-js skills
- Component work → Load shadcn + tailwind skills
- Accessibility → Load accessibility-skill

---

## 📋 Common Tasks

**Create component:**
```typescript
interface ComponentProps {
  prop: string
}

export function Component({ prop }: ComponentProps) {
  return <div>{prop}</div>
}
```

**Use shadcn component:**
```typescript
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"

export function MyComponent() {
  const { toast } = useToast()
  return <Button onClick={() => toast({ title: "Clicked" })}>Click</Button>
}
```

**Create page:**
```typescript
// app/page.tsx
export default function Page() {
  return <div>Content</div>
}
```

---

## 🎨 Styling

**Tailwind classes:**
```typescript
<div className="flex items-center gap-4 p-4 bg-background rounded-lg border">
  Content
</div>
```

**Dark mode:**
```typescript
<div className="dark:bg-gray-900 dark:text-white">
  Content
</div>
```

---

## ♿ Accessibility (Critical)

Before pushing code:
- [ ] Semantic HTML (button, not div)
- [ ] ARIA labels (aria-label, aria-describedby)
- [ ] Keyboard navigation (Tab, Enter, Esc)
- [ ] Color contrast (WCAG AA)
- [ ] Screen reader support

**See:** `docs/accessibility/PRIORITY_FIXES_FOR_TURING.md`

---

## 🧪 Testing

```bash
# Run tests
cd apps/frontend
npm test

# Type check
npm run typecheck

# Lint
npm run lint
```

---

## 📝 When Complete

1. Update TASK_TRACKER.md
2. Add status update to COMMUNICATION_HUB.md
3. **Clean context** (forget task specifics, keep patterns)

**See:** `docs/agents/CONTEXT_MANAGEMENT.md`

---

## 🆘 Need Help?

- React issues → `react-skill.md`
- Next.js issues → `next-js-skill.md`
- Styling → `tailwind-css-skill.md`
- Components → `shadcn-skill.md`
- Accessibility → `accessibility-skill.md`
- Ask GAUDÍ in COMMUNICATION_HUB.md

---

**Current Task:** Check `tasks/assignments/`
**Status:** Update COMMUNICATION_HUB.md
