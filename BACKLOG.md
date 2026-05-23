# POD-and-Affiliate — Backlog

_Last updated: 2026-05-23 (session 2)_

---

## Immediate — must complete before first live run

- [x] **Verify Gemini end-to-end** — confirmed working (hits free tier daily quota limit quickly; falls back to generic copy when exhausted)
- [x] **Create Etsy seller account** — done, NickPrintCo live with 3 active listings and full shop profile
- [x] **Register Etsy developer app** — first attempt denied, resubmitted 2026-05-23 with stronger description. Awaiting approval.
- [x] **Run `setup_etsy_auth.py`** — done, tokens in .env
- [x] **Create Printful account** — done, Etsy store connected, `PRINTFUL_API_KEY` + `PRINTFUL_STORE_ID` in `.env`, verified via API
- [x] **Fill `.env`** — all Etsy values populated: `ETSY_ACCESS_TOKEN`, `ETSY_REFRESH_TOKEN`, `ETSY_SHOP_ID=66128682`, `ETSY_SHIPPING_PROFILE_ID=306841979260`
- [ ] **Register eBay developer account** — done, awaiting 1 business day approval. Account: cox333, business name: 333 Trading, 790 feedback.
- [ ] **Build `ebay_client.py`** — eBay Inventory API parallel publisher. Build once API keys arrive.
- [ ] **Connect Printful to eBay** — Printful natively supports eBay; set up once eBay API credentials confirmed
- [ ] **Set `should_auto_renew: false` on all bot-created listings** — Etsy auto-renew costs £0.25/relist. Add to `create_draft_listing` payload in `etsy_client.py`
- [ ] **Investigate Printful sync product for Etsy-integrated stores** — `/store/products` endpoint only works for Manual Order / API platform stores. NickPrintCo store (18218316) is Etsy-integrated. Find correct endpoint. Blocks v0.3.0.
- [ ] **Replace Google autocomplete in `etsy_scraper.py` with Etsy API** — now unblocked since Etsy API is approved
- [ ] **Run `test_pipeline.py` clean end-to-end** — wait for Gemini daily quota reset, run once to confirm AI copy + image both attach correctly
- [ ] **First full live run** — `python main.py`, check Printful dashboard + Etsy listings

---

## Dev environment — outstanding

- [ ] **Install Node.js** — download LTS `.msi` from nodejs.org (do NOT use Chocolatey). Required for Bitwarden MCP server
- [x] **Python 3.14 conflict resolved** — Python 3.14 uninstalled. Python 3.13 Scripts added to PATH. `pip` now correctly resolves to 3.13
- [ ] **Install Bitwarden MCP server** — after Node.js: `npm install -g @bitwarden/mcp-server` + `npm install -g @bitwarden/cli`, then configure in Claude Code settings
- [x] **Create Proton Mail account** — shop.2026.uk@proton.me (display name: Shop 2026)
- [x] **Create Bitwarden account** — done (MCP integration abandoned, use web vault)

---

## Business setup (run in parallel with technical work)

- [x] **Proton Mail** — shop.2026.uk@proton.me
- [x] **Monzo Business Pro** — approved, funded with £10
- [x] **Bitwarden** — done (MCP integration abandoned)
- [ ] **Register as sole trader** — Nick Cox Digital, SIC 74100, HMRC — do before first sale
- [x] **Decide business name** — Nick Cox Digital (sole trader), NickPrintCo (Etsy shop)

---

## Short-term improvements (post-first-run)

- [ ] **Review first listing quality** — check Gemini-generated titles, descriptions, tags against real Etsy search behaviour. Tune prompt in `generator/listing_generator.py` if needed
- [ ] **Add SEO check step** — validate tags hit high-traffic low-competition keywords (could use Etsy autocomplete data we already scrape)
- [ ] **Add Printful shipping profile auto-fetch** — currently manual; could query Printful API on first run and write to `.env`
- [ ] **Dashboard polish** — add per-listing detail view, image preview, status filter
- [ ] **Error alerting** — basic email or Telegram notification when the pipeline fails
- [ ] **Add more product types** — mugs (19), tote bags, phone cases. Already have IDs in `.env.example`
- [ ] **Review pricing logic** — flat 2.5x multiplier; consider per-product-type margins, shipping costs, Etsy fees (~6.5% + listing fee)

---

## Financial tracking (automate later)

- [ ] **Transaction log in SQLite** — add a `transactions` table to the existing database: date, type (sale/fee/payout), amount, currency, source (Etsy/Printful/Monzo), reference ID
- [ ] **Etsy payout reconciliation** — pull Etsy Payments ledger via API, match against orders, log net margin per sale after all fees
- [ ] **Monzo API integration** — pull business account transactions via Monzo API (`api.monzo.com`), cross-reference with Etsy payouts
  - Auth: OAuth2 — register app at developers.monzo.com, get client ID + secret, run OAuth flow, store tokens in `.env`
  - Key endpoints: `GET /transactions` (full ledger), `GET /balance` (current balance + total spent), `GET /accounts` (account ID needed for all calls)
  - Use case 1: auto-reconcile Etsy payouts — match Monzo credit entries against expected Etsy payout amounts, flag discrepancies
  - Use case 2: running P&L — pull all debits (Printful charges, Etsy fees, subscriptions) and credits (Etsy payouts), calculate net per month
  - Use case 3: tax pot logic — on each Etsy payout credit, calculate 20% and log it as "reserved for self-assessment" (Monzo Pots API can move money automatically if Business Pro supports it)
  - **Caveat:** Monzo Business Pro API access requires contacting Monzo developer support — personal OAuth works out of the box but business accounts may need manual approval. Verify this before building.
- [ ] **Monthly P&L summary** — auto-generate: gross sales, Etsy fees, Printful costs, net profit, VAT headroom vs £90k threshold
- [ ] **Self-assessment prep export** — annual CSV of all income and allowable expenses, ready for HMRC submission
- [ ] **Tax pot automation** — flag 20% of each Etsy payout as reserved for self-assessment (could use Monzo pot via API)

---

## Medium-term ideas

- [ ] **A/B test listing copy** — generate two variants per keyword, track which converts better via Etsy stats
- [ ] **Auto-publish toggle** — add `AUTO_PUBLISH=false` env var; when true, skip draft review step. Keep false by default
- [ ] **Trend velocity scoring** — weight keywords by how fast they're growing, not just volume
- [ ] **Pinterest trend integration** — already in scope per pipeline design; verify it's actually firing
- [ ] **Seasonal / event calendar** — inject upcoming holidays/events into trend context (Christmas, Valentine's, etc.)
- [ ] **Competitor analysis scrape** — Etsy bestseller data for validated niches
- [ ] **Design variation** — per keyword, generate 2–3 image variants using different prompt styles; pick best
- [ ] **Telegram bot** — daily summary: listings created, impressions, views, orders
- [ ] **Multi-shop support** — separate Etsy shops per theme niche (dogs, gym, funny). Shared backend
- [ ] **Printful product expansion** — auto-create all three product types (T-shirt, sweatshirt, hoodie) per design, not just one

---

## Long-term / future

- [ ] **Affiliate branch** — niche content site on GitHub Pages. Zero hosting cost. SEO-driven traffic to Etsy. **Never merge into `pod`**
- [ ] **Etsy ads integration** — auto-promote listings that get early views; kill ones that don't
- [ ] **Sales analytics pipeline** — pull Etsy order data, calculate true margin per product, feed back into theme selection
- [ ] **Keyword performance feedback loop** — track which trends converted to sales, weight future scraping accordingly
- [ ] **Convert to Ltd company** — when profit ~£25k/year. Starling → Ltd business account, accountant
- [ ] **Explore other marketplaces** — Redbubble, Merch by Amazon, TeePublic. Share designs across platforms
- [ ] **Custom image model fine-tuning** — fine-tune a small diffusion model on your best-performing designs

---

## Decisions log

| Date | Decision | Reason |
|------|----------|--------|
| 2026-05-19 | Migrated AI from Anthropic Claude → Google Gemini Flash | Free tier, no billing needed to start |
| 2026-05-19 | Image gen via Pollinations.ai | Completely free, no API key, adequate quality |
| 2026-05-19 | Listings created as drafts | Review before publish — avoids live mistakes during setup |
| 2026-05-19 | Pricing at 2.5x Printful base | ~50% margin after Etsy fees on £25 retail |
| 2026-05-19 | Python 3.13 on Windows | Current machine setup |
| 2026-05-21 | Sole trader name: Nick Cox Digital | Broad enough to cover POD, trading, automation |
| 2026-05-21 | Etsy shop name: NickPrintCo | Personal brand, available on Etsy |
| 2026-05-21 | Bank: Monzo Business Pro £9/month | Tax pots on paid tier, familiar app |
| 2026-05-21 | SIC code: 74100 | Specialised Design Activities — covers AI/POD work |
| 2026-05-21 | Abandoned Starling in favour of Monzo | Already banking with Monzo personally |
| 2026-05-21 | PLAN.md as session anchor | Prevent tangents — open first every session |
| 2026-05-22 | rclone + Proton Drive for .env backup | Automated, E2E encrypted, runs on every Stop hook |
| 2026-05-22 | Etsy listing currency set to GBP | Avoids 2.5% currency conversion fee on every sale |
| 2026-05-22 | Offsite Ads opted out | Optional below ~$10k/year; adds 12-15% cost if enabled |
| 2026-05-22 | Etsy/Pinterest scrapers → Google autocomplete (interim) | Both original endpoints dead/blocked (DataDome + 404). Official Etsy API replaces this once approved |
| 2026-05-22 | playwright removed → curl_cffi | playwright unused and heavyweight; curl_cffi needed for Cloudflare bypass attempts |
| 2026-05-22 | HMRC sole trader registration trigger: £800 cumulative Etsy turnover | £1,000 trading allowance is a cliff — register before crossing it |
| 2026-05-22 | Python 3.14 uninstalled | Was silently intercepting pip installs, causing wrong-version package installs |
| 2026-05-23 | eBay added as parallel marketplace channel | Etsy developer app denied first time; eBay has open API access, Printful integration, and existing 790-feedback account (cox333 / 333 Trading) |
| 2026-05-23 | Cross-platform brand name: 333 Trading | Generic enough to cover POD, tools, and car parts on same eBay account |
| 2026-05-23 | Etsy app resubmitted referencing API Terms Section 4 | Explicitly permits selling own products — strengthens case vs vague first application |
| 2026-05-23 | Etsy x-api-key header must be `keystring:sharedsecret` | Etsy API v3 quirk — not documented clearly; discovered by trial and error |
| 2026-05-23 | `readiness_state_id` is a shop-specific UUID | Not a generic int (1/2/3). Must be queried from an existing listing. NickPrintCo value: 1488409015052 |
| 2026-05-23 | Printful file upload uses URL not base64 | Base64 of a 1080px PNG causes payload rejection. Pass Pollinations URL directly via `url` field instead |
| 2026-05-23 | No auto-relist on Etsy | £0.25 per relist. Let non-performers expire. Create new listings instead. `should_auto_renew: false` on all bot listings |
| 2026-05-23 | Printful `/store/products` does not work for Etsy-integrated stores | Endpoint is "Manual Order / API platform only". NickPrintCo store is Etsy-integrated. Correct approach for v0.3.0 TBD |

---

## Won't do

- Auto-publish without review during initial phase
- Merge `pod` and `affiliate` branches ever
- Commit `.env` to git
