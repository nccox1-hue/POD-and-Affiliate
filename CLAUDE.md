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

### pip rule
Python 3.14 was uninstalled (was silently intercepting pip installs).
**Always use `python -m pip install` to install into 3.13 — do not rely on bare `pip`.**

### Running the bot
```powershell
$env:PATH = "C:\Users\nickc\AppData\Local\Python\python-3.13-64;" + $env:PATH
cd C:\Users\nickc\Documents\POD-and-Affiliate
python main.py
```
Dashboard: http://localhost:8081

---

## Current status (session: 2026-05-23)

### v0.1.0 COMPLETE ✓
### v0.2.0 COMPLETE ✓ — First Etsy draft listing created via API (listing id: 4510329894)

### Completed this session
- **Etsy API approved** — `ETSY_API_KEY` + `ETSY_API_SECRET` confirmed live
- **OAuth flow complete** — `setup_etsy_auth.py` run, `ETSY_ACCESS_TOKEN` + `ETSY_REFRESH_TOKEN` saved to `.env`
- **Shop credentials fetched** — `ETSY_SHOP_ID=66128682`, `ETSY_SHIPPING_PROFILE_ID=306841979260` (Evri) saved
- **Etsy API quirks fixed** — `x-api-key` must be `key:secret` combined; `readiness_state_id` is a shop-specific UUID (1488409015052, not a generic int); `taxonomy_id` is `559` for T-shirts
- **Token refresh race condition fixed** — `upload_listing_image` now uses `self._access_token` (updated on refresh) not `settings.etsy_access_token`
- **Printful file upload fixed** — switched from base64 to passing Pollinations URL directly via `source_url` param
- **First draft listing confirmed live** — id `4510329894`, "funny cat mum gift", draft visible in Etsy shop manager
- **Business rule locked in** — no auto-relist; £0.25 per relist on Etsy. Let listings expire. Create new ones.

### Current blockers
- **Printful sync product** — `/store/products` returns "Manual Order / API platform only". NickPrintCo Printful store is Etsy-integrated, not standalone API. Need to find the correct endpoint or workflow for Etsy-integrated stores. This blocks v0.3.0.
- **Gemini daily quota** — free tier exhausts after a few calls per day. Resets daily. Fallback copy works. Not a code issue.
- **Image not attached to first test listing** — token refresh happened mid-run on first successful test; fixed in code. Will work on next clean run.

### Outstanding for v0.3.0
- Investigate Printful API for Etsy-connected stores — correct endpoint for sync product creation
- Run `test_pipeline.py` once Gemini quota resets for a fully clean run with AI copy + image attached
- Set `should_auto_renew: false` on all listings created via API (Etsy auto-renew = £0.25 relist fee)

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
