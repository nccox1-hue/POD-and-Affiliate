# POD-and-Affiliate — CLAUDE.md

Project context for Claude Code sessions. Keep this updated at the end of each session.

> **START EVERY SESSION HERE:** Open [PLAN.md](PLAN.md) first. Work the next unchecked item. Do not deviate until it is done.
> **Business context:** See [BUSINESS_PLAN.md](BUSINESS_PLAN.md) for full business plan, financials, and milestones.

---

## Project overview

**Pivoted to eBay Arbitrage Bot (session 2026-05-26).** The POD pipeline is fully replaced.

The bot runs on a 24h schedule:

1. Scans eBay sold listings (Finding API `findCompletedItems`) across target categories
2. For each sold item, searches Avasam (primary) then BigBuy (secondary) for a matching wholesale product
3. Runs margin check: profit ≥ £3 AND margin ≥ 25%
4. Claude writes eBay title + description from supplier product data + sold listing title
5. Creates eBay listing via Trading API
6. Every 12h: monitor checks supplier price/stock — pauses or ends listings if margin collapses or stock runs out
7. Every 2h: order poller checks for paid eBay orders — submits to supplier API for fulfilment, polls tracking, writes back to eBay via CompleteSale

Zero stock. Zero design work. Zero upfront cost. Proven sales signal.

**Stack:** Python 3.13, FastAPI, APScheduler, SQLAlchemy (async), aiosqlite, httpx, Anthropic Claude Haiku, Jinja2

---

## Branch rules

- `pod` — this branch. Arbitrage bot.
- `affiliate` — future niche content site (GitHub Pages). Not yet started.
- **These two branches never merge. There is no main branch.**

---

## Hard rules

- Never touch the stocks-scanner repo.
- `.env` is gitignored — never commit secrets.
- `pod` and `affiliate` branches never merge.

## Credentials policy

`.env` is the single store for **all** account credentials — API keys, secrets, tokens. This is intentional. `.env` is gitignored and backed up to Proton Drive. Never question storing credentials in `.env` for this project.

---

## Environment setup (Windows — Python 3.13)

Python is installed at:
```
C:\Users\nickc\AppData\Local\Python\python-3.13-64\python.exe
```

PATH fix applied (permanent, user-level) — restart terminal to pick up `python` and `pip` as bare commands.

### MSVCP140.dll fix
`greenlet` (required by SQLAlchemy async) needs `MSVCP140.dll`:
```
C:\Program Files (x86)\Microsoft\Edge\Application\148.0.3967.70\msvcp140.dll
→ C:\Users\nickc\AppData\Local\Python\python-3.13-64\msvcp140.dll
```
**If greenlet fails from a fresh terminal, set PATH first:**
```powershell
$env:PATH = "C:\Users\nickc\AppData\Local\Python\python-3.13-64;" + $env:PATH
```

### pip rule
**Always use `python -m pip install` to install into 3.13 — do not rely on bare `pip`.**

### Running the bot
```powershell
$env:PATH = "C:\Users\nickc\AppData\Local\Python\python-3.13-64;" + $env:PATH
cd C:\Users\nickc\Documents\POD-and-Affiliate
python main.py
```
Dashboard: http://localhost:8081

---

## Current status (session: 2026-05-27)

### v0.3.0 COMPLETE ✓ — Last POD milestone
### v1.0.0-arb IN PROGRESS — awaiting first live production scan

### Completed this session (2026-05-27)
- **Diagnosed eBay Finding API 500 errors** — was a rate limit (`errorId 10001`), not a parameter error. Parameters, App ID, and all 7 category IDs confirmed correct via sandbox.
- **Fixed scanner error handling** — logs full response body on non-200; exits cleanly on rate limit instead of retrying
- **Reduced scan volume** — default pages per category: 2 → 1 (7 API calls/scan instead of 14)
- **eBay sandbox mode** — `EBAY_APP_ID_SANDBOX=NickCox-NickPrin-SBX-f4e87e45f-a1d1ef3e`, `EBAY_USE_SANDBOX=True/False` toggle in settings + `.env`
- **Sandbox verified** — all 7 categories return HTTP 200, 0 results (expected — no real completed sales in sandbox)
- **Supplier keys confirmed live** — `AVASAM_CONSUMER_KEY` + `AVASAM_SECRET_KEY` + `BIGBUY_API_KEY_PROD` all in `.env`
- **PLAN.md rewritten** — replaced stale POD content with current arbitrage status and next actions

### Current state
Bot running in sandbox mode. All code and API calls confirmed correct. Production rate limit resets **~08:00 BST 2026-05-28**.

### Next action
1. At/after 08:00 BST 2026-05-28: set `EBAY_USE_SANDBOX=False` in `.env`
2. Run `python main.py`
3. Watch for `INFO eBay scanner: X sold items fetched` — confirms production scan working
4. Watch for supplier match + margin filter logs — confirms full pipeline working
5. First listing created automatically — confirm in eBay Seller Hub → tag `v1.0.0-arb`

---

## Next steps
See [PLAN.md](PLAN.md) — work top to bottom, one item at a time.

---

## Key file locations

| File | Purpose |
|---|---|
| `main.py` | Entrypoint — FastAPI + uvicorn + scheduler |
| `config/settings.py` | All env var definitions |
| `scanner/ebay_sold_scanner.py` | eBay Finding API — finds sold listings |
| `scanner/margin_calculator.py` | Fee calc, profit filter, scoring |
| `scanner/avasam_sourcer.py` | Avasam API client (stub until key set) |
| `scanner/bigbuy_sourcer.py` | BigBuy API client (stub until key set) |
| `arbitrage/pipeline.py` | Full cycle orchestration |
| `arbitrage/monitor.py` | 12h price/stock monitor |
| `generator/listing_generator.py` | Claude/Gemini eBay listing copy |
| `publisher/ebay_client.py` | eBay Trading API client |
| `publisher/ebay_order_poller.py` | Order detection + supplier fulfilment |
| `scheduler/task_scheduler.py` | APScheduler wrapper |
| `dashboard/routes.py` | FastAPI dashboard routes |
| `database/models.py` | SQLAlchemy models |

---

## Pricing / margins

- **Min profit threshold:** £3.00 (configurable via `MIN_PROFIT_GBP` in `.env`)
- **Min margin threshold:** 25% (configurable via `MIN_MARGIN_PCT` in `.env`)
- **End listing if margin drops below:** 15% (hardcoded in `arbitrage/monitor.py`)
- **eBay FVF:** 12.8% + £0.30 per transaction
- **Scan price range:** £8–£80 (configurable via `MIN_EBAY_PRICE` / `MAX_EBAY_PRICE`)

## Versioning

Git tags only — no VERSION file, no CHANGELOG.

| Tag | Milestone |
|-----|-----------|
| `v0.1.0` | POD pipeline end-to-end verified |
| `v0.2.0` | Etsy API live |
| `v0.3.0` | Printful + eBay pipeline confirmed |
| `v1.0.0-arb` | Arbitrage bot first live listing (needs supplier key) |
| `v1.x.0-arb` | Feature additions (Amazon benchmark, Telegram alerts, etc.) |
