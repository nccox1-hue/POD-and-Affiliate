# POD-and-Affiliate — CLAUDE.md

Project context for Claude Code sessions. Keep this updated at the end of each session.

> **START EVERY SESSION HERE:** Open [PLAN.md](PLAN.md) first. Work the next unchecked item. Do not deviate until it is done.
> **Business context:** See [BUSINESS_PLAN.md](BUSINESS_PLAN.md) for full business plan, financials, and milestones.

---

## Financial stress-test rule — MANDATORY before building any revenue stream

**Never propose, build, or deploy a revenue stream without completing this analysis first. No exceptions.**

Before any new stream is discussed or built, explicitly state:

1. **The maths** — show actual numbers at low/mid/high scenarios. Not headlines. E.g. "at 5% sell-through on 150 listings × £5 profit = £37.50/month". Show the working.
2. **Capital required** — what real money is at risk, including monthly costs.
3. **Time to first revenue** — realistic (not optimistic). State the assumption.
4. **Time to £200/month target** — the minimum income bar for any stream in this project.
5. **Worst case** — what is the maximum possible loss? State it plainly before recommending.
6. **Risk/reward verdict** — does this actually make sense given the goal? If not, say so before building.

**Why this rule exists:** Crypto funding rate arb was proposed, built, and deployed before the numbers were stress-tested against the £200/month goal. It doesn't meet the goal without £15,000+ capital and carries exchange insolvency risk. This should have been identified before a line of code was written. The physical POD stream was similarly built before confirming demand signal viability. Two streams parked after build = wasted sessions.

**The standard is:** if you cannot show a credible path to £200/month with acceptable risk BEFORE building, do not build it. Raise the concern first, get agreement, then build.

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

## Current status (session: 2026-05-31)

### Active revenue streams (all running — bot started with `python main.py`)

**Stream A1 — Etsy Digital Wall Art** ✅ LIVE
- 3 listings published and live on Etsy Seller Hub (confirmed this session)
- Pipeline: Etsy bestseller scanner → Pollinations.ai artwork → digital listing publisher
- Runs every 56h, 3 listings/cycle at £2.49 each
- Key fixes applied: `type:"download"` (not `is_digital`), `when_made:"2020_2026"`, auto token refresh on 401

**Stream A2 — Etsy Excel Templates** ⚠️ BUILT, NOT YET CONFIRMED
- `pod_digital/template_generator.py` (openpyxl) — budget tracker, project tracker generated
- `pod_digital/template_pipeline.py` — publishes on 48h schedule at £10-£30
- Template listing creation still failing (separate issue — needs debug next session)

**Stream B — Affiliate Site (Automation/Excel)** ✅ LIVE
- Site live: https://nccox1-hue.github.io/POD-and-Affiliate/
- 7+ articles published automatically via Claude Haiku → git commit → GitHub Pages
- Runs daily (24h schedule), 1 article/cycle
- 28 keywords remaining in queue (`data/affiliate_keywords.json`)

**Stream C — eBay Arbitrage** ⚠️ SCANNER WORKING, SUPPLIER BLOCKED
- Playwright scanner confirmed: 200+ sold items per search, price floor £50-£300
- Avasam free tier has NO inventory API access → 0 eBay listings created
- Upgrade to Avasam Advanced (£24.92+VAT/mo) needed to unblock → defer until A/B earning

**Stream D — Crypto Funding Rate Arb** ⏸ PARKED
- UK FCA bans retail perp trading — Bybit correctly blocks UK accounts
- Code retained in `sandbox/` but scheduler jobs removed
- Not viable without large capital AND regulatory exemption

### MCP status
Local MCPs (ccxt, funding-rates, prediction-markets) do NOT load in VS Code extension — confirmed limitation of the extension vs CLI. Cloud MCPs (Higgsfield, Google Calendar) work fine. Not worth further debugging.

### Key decisions this session
- Revenue target: **£1,000/month** combined across all streams
- Physical POD (t-shirts): permanently shelved — no demand signal
- Crypto arb: parked — UK FCA restriction + poor risk/reward at retail capital levels
- eBay price floor: raised £8 → **£50** for better margin per sale
- `.claude/settings.json` now gitignored (contained BW_SESSION token)
- `setup_ebay_auth.py` hardcoded credentials replaced with env vars

### Nick's pending manual actions
See `C:\Users\nickc\.claude\projects\c--Users-nickc-Documents-POD-and-Affiliate\memory\nick_actions.md`
Key remaining: Amazon Associates bank details, Rakuten/PartnerStack approvals, Google Search Console, Avasam upgrade decision, Bybit (parked).

### Next actions
1. **Nick** — Add bank details to Amazon Associates (required to receive any commissions)
2. **Nick** — Google Search Console: verify site and submit sitemap
3. **Claude** — Debug Excel template pipeline (template listing creation failing — different error from wall art fix)
4. **Claude** — Add Udemy course to plan (Stream E) — curriculum and scripts to be written by Claude
5. **Both** — Monitor Etsy Seller Hub: are digital listings getting views? Any sales?

---

## Next steps
See [PLAN.md](PLAN.md) — work top to bottom, one item at a time.

---

## Key file locations

| File | Purpose |
|---|---|
| `main.py` | Entrypoint — FastAPI + uvicorn + scheduler |
| `config/settings.py` | All env var definitions |
| `scanner/ebay_sold_scanner.py` | Playwright-based sold listing scanner (replaces dead Finding API) |
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
- **Scan price range:** £50–£300 (raised this session for better margin per sale)

## Versioning

Git tags only — no VERSION file, no CHANGELOG.

| Tag | Milestone |
|-----|-----------|
| `v0.1.0` | POD pipeline end-to-end verified |
| `v0.2.0` | Etsy API live |
| `v0.3.0` | Printful + eBay pipeline confirmed |
| `v1.0.0-arb` | Arbitrage bot first live listing (needs supplier key) |
| `v1.x.0-arb` | Feature additions (Amazon benchmark, Telegram alerts, etc.) |
