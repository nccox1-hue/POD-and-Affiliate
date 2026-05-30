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

## Current status (session: 2026-05-29)

### v0.3.0 COMPLETE ✓ — Last POD milestone
### v1.0.0-arb BLOCKED — eBay Finding API decommissioned, scanner needs replacement

### Completed this session (2026-05-29)
- **Finding API confirmed DEAD** — `findCompletedItems` decommissioned 5 Feb 2025. `errorId 10001` is a gateway block, not a quota. Waiting will never fix it.
- **Cost audit completed** — Avasam requires paid plan (£24.99+VAT/mo min) for API. BigBuy needs Pack Marketplaces (~£84/mo + €90 one-off). Monzo Pro £9/mo. **Manual check needed: confirm which are actively billing.**
- **Strategic review** — full income landscape researched. New focus: crypto/prediction market arb sandbox. Automotive SaaS, AI video agency, B2B lead gen all backlogged.
- **MCPs installed** (global `~/.claude/settings.json`) — `ccxt`, `funding-rates`, `prediction-markets`. Restart Claude Code to activate.

### Current state
Arbitrage bot pipeline fully built. Only the scanner input is broken. Two viable fixes:
- **Playwright MCP** — scrape Terapeak via eBay Seller Hub (free, no API cost)
- **Apify `harvestlab/ebay-scraper`** — paid replacement, ~$0.003/item

New focus: practice crypto funding rate arb + prediction market arb in sandbox before touching capital.

### Next actions
1. **Manual** — check Avasam, BigBuy, Monzo dashboards. Confirm what is billing. Cancel anything not justified.
2. **Restart Claude Code** — activates ccxt, funding-rates, prediction-markets MCPs.
3. **Sandbox session** — explore CCXT MCP (Binance testnet) and prediction-markets MCP (Polymarket). Learn mechanics before deploying capital.
4. **Scanner fix** — decide Playwright vs Apify once supplier billing picture is clear.

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
