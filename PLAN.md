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
> Status: **COMPLETE ✓**

- [x] **[Nick]** Create Etsy seller account at etsy.com — approved ✓
- [x] **[Nick]** Register Etsy developer app → `ETSY_API_KEY` + `ETSY_API_SECRET` confirmed working
- [x] **[Nick]** Run `setup_etsy_auth.py` → `ETSY_ACCESS_TOKEN` + `ETSY_REFRESH_TOKEN` saved
- [x] **[Nick]** Run `get_shop_info.py` → `ETSY_SHOP_ID=66128682`, `ETSY_SHIPPING_PROFILE_ID=306841979260` saved
- [x] **[Nick]** Create Printful account → Etsy store connected → `PRINTFUL_API_KEY` + `PRINTFUL_STORE_ID` in `.env`

---

## Stage 2 — v0.2.0: First Draft Listing
> Status: **COMPLETE ✓**

- [x] **[Claude]** Run pipeline with a hardcoded keyword (bypass scraper)
- [x] **[Nick]** Confirm draft listing appears in Etsy shop — listing id 4510329894 confirmed
- [ ] **[Claude]** Tag `v0.2.0`

---

## Stage 3 — v0.3.0: First Printful Sync
> Status: **Blocked — Printful `/store/products` endpoint only works for Manual Order / API stores. NickPrintCo store is Etsy-integrated. Correct API approach TBD.**

- [ ] **[Claude]** Investigate correct Printful API endpoint for Etsy-integrated stores
- [ ] **[Nick]** Confirm Printful product created + mockup URLs working
- [ ] **[Claude]** Tag `v0.3.0`

---

## Stage 3b — eBay Channel (parallel to Stage 3)
> Status: **In progress — developer account registered 2026-05-23, awaiting approval**
> Runs in parallel with Stage 3. Does not depend on Printful being resolved.
> Existing account: username `cox333`, business name `333 Trading`, 790 feedback — strong starting position.

- [ ] **[Nick]** eBay developer account approved → collect App ID, Dev ID, Cert ID, OAuth credentials
- [ ] **[Nick]** Add eBay credentials to `.env`: `EBAY_APP_ID`, `EBAY_DEV_ID`, `EBAY_CERT_ID`, `EBAY_ACCESS_TOKEN`
- [ ] **[Claude]** Build `publisher/ebay_client.py` — eBay Inventory API, create draft listing, upload image
- [ ] **[Claude]** Wire eBay into `publisher/publisher.py` alongside `etsy_client.py` — both publish from same pipeline run
- [ ] **[Nick]** Connect Printful to eBay account (Printful dashboard → Stores → Add store → eBay)
- [ ] **[Nick]** Confirm first eBay draft listing appears in Seller Hub

---

## Stage 4 — Fix Scrapers
> Status: **Blocked on Stage 3** (pipeline can run without scrapers using fixed keywords)

- [x] **[Claude]** Etsy autocomplete (403) — interim fix: Google autocomplete in place as bridge
- [x] **[Claude]** Pinterest trends (404) — interim fix: Google autocomplete with discovery/gift context queries
- [x] **[Claude]** Google Trends — working, no fix needed
- [ ] **[Claude]** Replace `etsy_scraper.py` Google autocomplete with proper Etsy API calls — do this immediately after Etsy API credentials are confirmed working (Stage 1/2)
- [ ] **[Claude]** Decide whether to add Pinterest v5 OAuth API — only if keyword quality proves a bottleneck post-launch

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
- [ ] **[Nick]** Register as sole trader with HMRC for Self Assessment — trigger: cumulative Etsy turnover reaches £800 (£1,000 allowance cliff, register before crossing it)

---

## Business rules (operational constraints)

- **Relisting cost**: £0.25 per relist on Etsy. **Never auto-relist non-performing listings.** Let them expire. Create a fresh listing instead. The scheduler and any auto-renew logic must respect this.

---

## Backlog
> Do not touch until v1.0.0 is tagged

- Telegram alerts for new listings / sales
- A/B copy testing (multiple Gemini variants per keyword)
- Bitwarden MCP server retry (previously failed to load in Claude Code)
- Email notifications via Proton SMTP
