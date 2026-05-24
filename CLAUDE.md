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

## Current status (session: 2026-05-24)

### v0.1.0 COMPLETE ✓
### v0.2.0 COMPLETE ✓ — First Etsy draft listing created via API (listing id: 4510329894)
### v0.3.0 COMPLETE ✓ — Printful product creation working, full pipeline confirmed end-to-end

### Completed this session
- **eBay channel live** — `publisher/ebay_client.py` built (Trading API, XML, Auth'n'Auth token, UK site ID 3). First live listing: ItemID 278017629043. Pipeline now publishes to both Etsy and eBay in one run.
- **Printful blocker resolved** — created a second Printful store "NickPrintCo API" (Manual/API type, ID 18226038). Product creation (`/store/products`) now works via this store. File uploads still use the Etsy-integrated store (ID 18218316).
- **Dual Printful store wiring** — `config/settings.py` has `printful_api_store_key` + `printful_api_store_id`. `printful_client.py` uses API store headers for `create_sync_product` and `get_mockup_url`; Etsy store headers for `upload_design_file`.
- **Negative text prompt strengthened** — Pollinations prompt now has six explicit no-text instructions + `&nologo=true` to reduce garbled text in generated images.
- **eBay XML escaping fixed** — Pollinations URLs contain `&` chars which broke raw XML. Fixed with `xml.sax.saxutils.escape`.
- **Full pipeline test passed** — `test_pipeline.py` ran end-to-end: design generated, Printful product created (id 434781336), Etsy draft listing created (id 4510564932), eBay live listing created (ItemID 278017749827). Gemini still quota-exhausted so fallback copy used — full AI copy will run when quota resets.
- **AFFILIATE_PLAN.md created** — full affiliate site plan: niche = Automation/AI/Productivity, platform = Jekyll on GitHub Pages (`affiliate` branch), programmes = Amazon Associates → ClickUp → Make → Jasper → HubSpot.
- **v0.3.0 tagged**

### Current blockers
- **Gemini daily quota** — exhausts quickly on free tier. Resets daily. Fallback copy works. Not a code issue.

### Notes on test listings
- Test Etsy draft `4510564932` and Printful product `434781336` created during this session's pipeline test — delete from dashboards manually.

### Outstanding actions for Nick
- Connect Printful to eBay account (Printful dashboard → Stores → Add store → eBay)
- Sign up for affiliate programmes: Amazon Associates, ClickUp, Make

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
