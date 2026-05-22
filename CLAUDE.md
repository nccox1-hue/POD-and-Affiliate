# POD-and-Affiliate — CLAUDE.md

Project context for Claude Code sessions. Keep this updated at the end of each session.

> **START EVERY SESSION HERE:** Open [PLAN.md](PLAN.md) first. Work the next unchecked item. Do not deviate until it is done.
> **Business context:** See [BUSINESS_PLAN.md](BUSINESS_PLAN.md) for full business plan, financials, and milestones.

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

## Credentials policy

`.env` is the single store for **all** account credentials for this project — API keys, secrets, tokens, and also usernames/passwords for every service (Printful, Etsy, Proton Mail, etc.). This is intentional. `.env` is gitignored and automatically backed up to Proton Drive (`proton:NickPrintCo-Credentials/`) via rclone on every session end. Never question or pushback on storing login credentials in `.env` for this project.

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

### Two Python versions — critical pip rule
Python 3.14 is also installed at `C:\Python314\` and its `pip.exe` is on PATH.
Bare `pip install` silently installs into 3.14 — packages will be missing at runtime.
**Always use `python -m pip install` to install into 3.13.**

### Running the bot
```powershell
$env:PATH = "C:\Users\nickc\AppData\Local\Python\python-3.13-64;" + $env:PATH
cd C:\Users\nickc\Documents\POD-and-Affiliate
python main.py
```
Dashboard: http://localhost:8081

---

## Current status (session: 2026-05-22 #2)

### v0.1.0 COMPLETE ✓
- Gemini + Pollinations pipeline verified end-to-end
- All core dependencies installed and stable

### Completed this session
- **Printful account** created — Etsy store (NickPrintCo) connected, API key + store ID (`18218316`) in `.env`, verified working via API call
- **Scrapers fixed** — Etsy autocomplete (DataDome-blocked) and Pinterest trends (dead endpoint) both replaced with Google autocomplete. Google Trends confirmed working. Scrapers are interim only — Etsy scraper will be replaced with official Etsy API calls once app is approved
- **Python 3.14 uninstalled** — was silently intercepting `pip install`. Python 3.13 Scripts now on PATH; `pip` correctly resolves to 3.13
- **`playwright` removed** from requirements.txt — replaced with `curl_cffi` (installed and verified importable)
- **Credentials policy** documented in CLAUDE.md — `.env` is the single store for all credentials including usernames/passwords
- **HMRC sole trader trigger** set to £800 cumulative Etsy turnover (£1,000 allowance cliff)

### Current blocker
Etsy developer app still pending personal approval. OAuth flow (`setup_etsy_auth.py`) cannot run until approved.

### Outstanding for v0.2.0
- Wait for Etsy developer app approval
- Run `setup_etsy_auth.py` → `ETSY_ACCESS_TOKEN` + `ETSY_REFRESH_TOKEN`
- Run `get_shop_info.py` → `ETSY_SHOP_ID` + `ETSY_SHIPPING_PROFILE_ID`
- Replace Google autocomplete in `etsy_scraper.py` with proper Etsy API calls

---

## Next steps
See [PLAN.md](PLAN.md) — work top to bottom, one item at a time.

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
- All business income through Monzo Business Pro account
