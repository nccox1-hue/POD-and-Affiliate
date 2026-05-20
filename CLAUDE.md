# POD-and-Affiliate — CLAUDE.md

Project context for Claude Code sessions. Keep this updated at the end of each session.

---

## Project overview

Fully automated Print-on-Demand business system. Runs on a 24h schedule:

1. Scrapes trending keywords (Etsy autocomplete, Google Trends, Pinterest Trends)
2. Uses Google Gemini Flash (free) to write an image generation prompt and full Etsy listing (title, description, 13 tags)
3. Generates a design image via Pollinations.ai (free, no API key)
4. Uploads design to Printful, creates a sync product
5. Creates a draft listing on Etsy with the image attached
6. Logs everything to SQLite, viewable on a FastAPI dashboard at port 8081

**Stack:** Python 3.13, FastAPI, APScheduler, SQLAlchemy (async), aiosqlite, httpx, aiohttp, google-genai, Pillow

---

## Branch rules

- `pod` — this branch. POD automation system only.
- `affiliate` — future niche content site (GitHub Pages). Never started.
- **These two branches never merge. There is no main branch.**

---

## Hard rules

- Never touch the stocks-scanner repo.
- `.env` is gitignored — never commit secrets.
- `pod` and `affiliate` branches never merge.
- Listings are created as **drafts** for review before publishing.

---

## Environment setup (Windows — Python 3.13)

Python is installed at:
```
C:\Users\nickc\AppData\Local\Python\python-3.13-64\python.exe
```

PATH fix applied (permanent, user-level) — restart terminal to pick up `python` and `pip` as bare commands.

### MSVCP140.dll fix
`greenlet` (required by SQLAlchemy async) needs `MSVCP140.dll` which isn't in System32 on this machine.
Fix applied: copied from Edge install:
```
C:\Program Files (x86)\Microsoft\Edge\Application\148.0.3967.70\msvcp140.dll
→ C:\Users\nickc\AppData\Local\Python\python-3.13-64\msvcp140.dll
```
**If running from a fresh terminal and greenlet fails, set PATH before running:**
```powershell
$env:PATH = "C:\Users\nickc\AppData\Local\Python\python-3.13-64;" + $env:PATH
```
After a full terminal restart this should be automatic.

### Running the bot
```powershell
$env:PATH = "C:\Users\nickc\AppData\Local\Python\python-3.13-64;" + $env:PATH
cd C:\Users\nickc\Documents\POD-and-Affiliate
python main.py
```
Dashboard: http://localhost:8081

---

## Current status (session: 2026-05-20)

### v0.1.0 COMPLETE ✓
- **Gemini + Pollinations pipeline verified end-to-end** via `test_v0_1_0.py`
- Gemini Flash successfully generates design prompts and Etsy listing copy
- Pollinations.ai successfully generates print-ready PNG designs (81KB test image confirmed)
- Rate-limit retry logic confirmed working (Gemini 429 handling, Pollinations 402 handling)
- Python 3.13 environment stable (Chocolatey Python 3.14 doesn't interfere)
- All core dependencies installed: uvicorn, google-genai, fastapi, SQLAlchemy, aiohttp, httpx, etc.

### Outstanding for v0.2.0 + live run
- Etsy seller account + developer registration
- Etsy OAuth token (run `setup_etsy_auth.py`)
- Etsy shop ID + shipping profile ID retrieval (run `get_shop_info.py`)
- Printful account + API key generation
- Fill `.env` with all credentials
- Fix scraper API blocks (Etsy returning 403, Pinterest returning 404) — may need different approach or throttling

---

## Next steps — v0.2.0 (Etsy API integration)

### 1. Set up Etsy seller + developer account
- Create Etsy seller account (if not already done): etsy.com
- Register as developer: etsy.com/developers
- Create an app to get `ETSY_API_KEY` and `ETSY_API_SECRET`
- Run `setup_etsy_auth.py` once to complete OAuth and get `ETSY_ACCESS_TOKEN`
- Run `get_shop_info.py` to fetch `ETSY_SHOP_ID` + `ETSY_SHIPPING_PROFILE_ID` automatically

### 2. Set up Printful account
- Create account: printful.com
- Dashboard → Stores → Connect a store (Etsy)
- API → Generate token → add as `PRINTFUL_API_KEY` in `.env`

### 3. Fill `.env` with all credentials
```
ETSY_API_KEY=<from developers.etsy.com>
ETSY_API_SECRET=<from developers.etsy.com>
ETSY_ACCESS_TOKEN=<auto-saved by setup_etsy_auth.py>
ETSY_SHOP_ID=<auto-saved by get_shop_info.py>
ETSY_SHIPPING_PROFILE_ID=<auto-saved by get_shop_info.py>
PRINTFUL_API_KEY=<from printful dashboard>
```

### 4. Debug scraper API blocks (interim)
- Etsy search returning 403, autocomplete returning 301
- Pinterest trends API returning 404 for both GB and US
- Google Trends hitting rate limits
- Options: (a) use static keyword list, (b) add rotating proxies, (c) use alternative trend sources

### 5. First Etsy draft listing creation
- Run test with fixed keywords (bypass scraper)
- Verify `publisher/publisher.py` can create Etsy draft listing with image
- Check Etsy shop for draft listing

### 6. First Printful sync (if step 5 succeeds)
- Verify Printful product created successfully
- Check mockup URLs are working

### 7. Business setup (parallel, not blocking)
- Proton Mail account ✓ (done)
- Starling Bank business account
- Bitwarden account ✓ (done — MCP server integration pending)
- Register as sole trader when ready to trade

---

## Key file locations

| File | Purpose |
|---|---|
| `main.py` | Entrypoint — FastAPI + uvicorn + scheduler |
| `config/settings.py` | All env var definitions |
| `config/themes.py` | Theme catalogue (12 themes defined, 6 active in `.env`) |
| `generator/listing_generator.py` | Gemini → Etsy listing copy |
| `generator/design_generator.py` | Gemini prompt builder + Pollinations image gen |
| `publisher/publisher.py` | Full pipeline orchestration |
| `publisher/etsy_client.py` | Etsy API client |
| `publisher/printful_client.py` | Printful API client |
| `scheduler/task_scheduler.py` | APScheduler wrapper |
| `dashboard/routes.py` | FastAPI dashboard routes |
| `database/models.py` | SQLAlchemy models (DesignJob) |

---

## Pricing

- Base cost assumption: £10 (Bella+Canvas 3001 from Printful)
- Price multiplier: 2.5x → ~£25 retail
- Configured in `.env` as `PRICE_MULTIPLIER=2.5`

## Versioning

Git tags only — no VERSION file, no CHANGELOG. Tag at milestones, not every session.

| Tag | Milestone |
|-----|-----------|
| `v0.1.0` | Pipeline verified end-to-end: Gemini returns content, Pollinations returns image |
| `v0.2.0` | First Etsy draft listing created successfully via API |
| `v0.3.0` | First Printful product synced |
| `v1.0.0` | Full live run: all credentials set, Printful + Etsy both working in one cycle |
| `v1.x.0` | Significant feature additions post-launch (Telegram alerts, A/B copy, etc.) |

Tag format: `git tag v0.x.0 -m "short description of milestone"`

---

## Business model

- Sole trader to start
- Convert to Ltd company when profit hits ~£25k/year
- All business income through Starling Bank business account
