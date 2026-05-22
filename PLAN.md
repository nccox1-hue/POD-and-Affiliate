# POD Business — Master Plan

> **This is the single source of truth for what to work on next.**
> Open this first at the start of every session. Work top-to-bottom. Do not skip ahead.

---

## Naming rules
> Use real name (Nick Cox) anywhere that touches money or tax: Etsy billing/payouts, Printful, Starling, HMRC.
> Use brand/pseudonym everywhere public-facing: Etsy shop name, display name, Proton Mail.
> Proton Mail display name: **Shop 2026**
> **Etsy shop name: NickPrintCo**

---

## Stage 1 — Accounts & Credentials
> Status: **IN PROGRESS — current blocker**

- [x] **[Nick]** Create Etsy seller account at etsy.com — approved ✓
- [x] **[Nick]** Register Etsy developer app at etsy.com/developers → get `ETSY_API_KEY` + `ETSY_API_SECRET` (app: nickprintco — Pending Personal Approval)
- [ ] **[Nick]** Run `setup_etsy_auth.py` → auto-saves `ETSY_ACCESS_TOKEN` + `ETSY_REFRESH_TOKEN`
- [ ] **[Nick]** Run `get_shop_info.py` → auto-saves `ETSY_SHOP_ID` + `ETSY_SHIPPING_PROFILE_ID`
- [ ] **[Nick]** Create Printful account at printful.com → connect Etsy store → generate `PRINTFUL_API_KEY`
- [ ] **[Claude]** Add credentials to `.env` and tick off checklist as each is provided

---

## Stage 2 — v0.2.0: First Draft Listing
> Status: **Blocked on Stage 1**

- [ ] **[Claude]** Run pipeline with a hardcoded keyword (bypass scraper)
- [ ] **[Nick]** Confirm draft listing appears in Etsy shop
- [ ] **[Claude]** Tag `v0.2.0`

---

## Stage 3 — v0.3.0: First Printful Sync
> Status: **Blocked on Stage 2**

- [ ] **[Nick]** Confirm Printful product created + mockup URLs working
- [ ] **[Claude]** Tag `v0.3.0`

---

## Stage 4 — Fix Scrapers
> Status: **Blocked on Stage 3** (pipeline can run without scrapers using fixed keywords)

- [ ] **[Claude]** Fix Etsy autocomplete (currently returning 403)
- [ ] **[Claude]** Fix Pinterest trends (currently returning 404)
- [ ] **[Claude]** Fix Google Trends rate limiting

---

## Stage 5 — v1.0.0: Full Live Run
> Status: **Blocked on Stages 1–4**

- [ ] **[Nick]** Confirm all credentials are live in `.env`
- [ ] **[Claude]** Verify full 24h cycle runs unattended: scrape → generate → publish
- [ ] **[Claude]** Tag `v1.0.0`

---

## Stage 6 — Business Setup
> Status: **Parallel — non-blocking, do alongside Stages 1–5**

- [x] **[Nick]** Proton Mail — shop.2026.uk@proton.me
- [x] **[Nick]** Bitwarden account
- [x] **[Nick]** Monzo Business Pro account — approved, funded with £10
- [ ] **[Nick]** Register as sole trader (when ready to trade)

---

## Backlog
> Do not touch until v1.0.0 is tagged

- Telegram alerts for new listings / sales
- A/B copy testing (multiple Gemini variants per keyword)
- Bitwarden MCP server retry (previously failed to load in Claude Code)
- Email notifications via Proton SMTP
