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

## Current status (session: 2026-05-19)

### What's done
- Full pipeline code written and committed (initial commit)
- Migrated from Anthropic Claude → **Google Gemini** (`google-genai` SDK, model `gemini-2.0-flash`)
- All dependencies installed for Python 3.13
- `requirements.txt` fixed: pinned versions loosened for Python 3.13 compatibility, `aiohttp` version corrected, `google-genai>=1.0.0` added
- `GEMINI_API_KEY` confirmed loading from `.env`
- Server starts successfully — pipeline runs, scheduler fires, Gemini calls reach the API
- Gemini model corrected: `gemini-1.5-flash` (deprecated/not found on free tier) → `gemini-2.0-flash`
- `.gitignore` created

### What still needs verifying
- Gemini `gemini-2.0-flash` call successfully returns content (was fixed mid-session, not yet re-tested)
- Pollinations.ai image generation confirmed working in code — not yet visually confirmed on a live run
- Dashboard at port 8081 — not yet opened and checked

---

## Next steps (in order)

### 1. Verify Gemini + image generation works end-to-end
- Restart server with correct PATH
- Watch logs — confirm Gemini returns a listing (not fallback) and Pollinations returns an image
- Check `data/designs/` for generated PNG files

### 2. Set up Etsy seller + developer account
- Create Etsy seller account (if not already done): etsy.com
- Register as developer: etsy.com/developers
- Create an app to get `ETSY_API_KEY` and `ETSY_API_SECRET`
- Run `setup_etsy_auth.py` once to complete OAuth and get `ETSY_ACCESS_TOKEN`
- Add `ETSY_SHOP_ID` from your shop URL
- Add `ETSY_SHIPPING_PROFILE_ID` after first Etsy setup (query via API or dashboard)

### 3. Set up Printful account
- Create account: printful.com
- Dashboard → Stores → Connect a store (Etsy)
- API → Generate token → add as `PRINTFUL_API_KEY` in `.env`

### 4. Fill remaining `.env` values
```
ETSY_API_KEY=
ETSY_API_SECRET=
ETSY_ACCESS_TOKEN=
ETSY_SHOP_ID=
ETSY_SHIPPING_PROFILE_ID=
PRINTFUL_API_KEY=
```

### 5. First full live run
- `python main.py` with all credentials set
- Check Printful dashboard for sync product
- Check Etsy shop for draft listing
- Review listing quality — adjust Gemini prompt in `generator/listing_generator.py` if needed

### 6. Business setup (parallel)
- Proton Mail account for business email separation
- Starling Bank business account
- Bitwarden for password management
- Register as sole trader when ready to start trading

### 7. Affiliate branch (future)
- Niche content site on GitHub Pages (zero hosting cost)
- Not started — separate branch, never merge with `pod`

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

## Business model

- Sole trader to start
- Convert to Ltd company when profit hits ~£25k/year
- All business income through Starling Bank business account
