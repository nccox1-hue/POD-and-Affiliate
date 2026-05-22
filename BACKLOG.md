# POD-and-Affiliate — Backlog

_Last updated: 2026-05-22_

---

## Immediate — must complete before first live run

- [ ] **Verify Gemini end-to-end** — start server, confirm logs show Gemini returning listing content (not fallback), check `data/designs/` for generated PNGs
- [ ] **Create Etsy seller account** — etsy.com → sell on Etsy
- [ ] **Register Etsy developer app** — etsy.com/developers → get `ETSY_API_KEY` + `ETSY_API_SECRET`
- [ ] **Run `setup_etsy_auth.py`** — completes OAuth, writes `ETSY_ACCESS_TOKEN` to `.env`
- [x] **Create Printful account** — done, Etsy store connected, `PRINTFUL_API_KEY` + `PRINTFUL_STORE_ID` in `.env`, verified via API
- [ ] **Fill `.env`** — remaining empty values: `ETSY_ACCESS_TOKEN`, `ETSY_REFRESH_TOKEN`, `ETSY_SHOP_ID`, `ETSY_SHIPPING_PROFILE_ID` (blocked on Etsy app approval)
- [ ] **First full live run** — `python main.py`, check Printful dashboard + Etsy drafts

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
- [ ] **Monzo API integration** — pull business account transactions via Monzo API, cross-reference with Etsy payouts
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

---

## Won't do

- Auto-publish without review during initial phase
- Merge `pod` and `affiliate` branches ever
- Commit `.env` to git
