# Quick Start: Migrating to uv

## What is uv?

**uv** is an extremely fast Python package installer and resolver, written in Rust. It's a drop-in replacement for pip that's **8-10x faster** for installation and **80-115x faster** for cached installs.

## Performance Comparison

| Operation | pip | uv | Speedup |
|-----------|-----|-----|---------|
| Fresh install | 60s | 6s | **10x** |
| Cached install | 30s | 0.3s | **100x** |
| Venv creation | 5s | 0.06s | **80x** |

## Migration Steps

### 1. Test Locally (5 minutes)

```bash
# Navigate to backend
cd apps/backend

# Test with current requirements
uv venv .venv-test
source .venv-test/bin/activate
uv pip install -r requirements.txt

# Verify it works
python manage.py check
deactivate
```

### 2. Update Dockerfile

**Replace:**
```dockerfile
RUN python -m venv /opt/venv
RUN pip install --no-cache-dir -r requirements.txt
```

**With:**
```dockerfile
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv venv /opt/venv
RUN uv pip install -r requirements.txt
```

### 3. Update Development Workflow

**Before (pip):**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**After (uv):**
```bash
uv venv
uv pip install -r requirements.txt
# Or just: uv pip install -r requirements.txt (creates venv automatically)
```

## Benefits

✅ **10x faster** dependency installation
✅ **100x faster** with cache
✅ **Automatic venv** management
✅ **Global cache** across projects
✅ **Drop-in replacement** for pip
✅ **Stand-alone binary** - no Python needed

## Rollback

If anything breaks:
```bash
# Just use pip instead
pip install -r requirements.txt
```

uv is fully compatible with pip's workflow.

## Learn More

- Docs: https://docs.astral.sh/uv/
- GitHub: https://github.com/astral-sh/uv
- Why uv?: https://astral.sh/blog/uv

---

**Next:** Run `bash /tmp/test_uv.sh` to test uv with your current setup!
