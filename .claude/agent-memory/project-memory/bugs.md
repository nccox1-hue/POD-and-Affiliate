# Bugs

### 2026-05-30: funding-rates-mcp crash on Windows

**Symptom:** `TypeError: 'generator' object does not support the asynchronous context manager protocol`
**Root cause:** `app_lifespan` in `cli.py` was a sync generator (`def` + `yield`). FastMCP expects `async with lifespan(app)` — needs an async context manager.
**Fix:** Added `from contextlib import asynccontextmanager`, decorated `app_lifespan` with `@asynccontextmanager`, changed to `async def`.
**File patched:** `C:\Users\nickc\AppData\Local\uv\cache\archive-v0\drtR_AsakkWNRbdO\Lib\site-packages\funding_rates_mcp\cli.py`
**Caveat:** Patch is in uvx cache — may be overwritten if uvx reinstalls the package.

---

### 2026-05-30: prediction-markets-mcp Windows Script Host error

**Symptom:** WSH popup — "Syntax error / 800A03EA / Microsoft JScript compilation error"
**Root cause:** The npm `.cmd` launcher called the `.js` file directly without `node`, so Windows file association (WSH) intercepted it.
**Fix:** Changed MCP config in `~/.claude/settings.json` to `"command": "node"` with explicit path to `index.js`.
