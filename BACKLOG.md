# POD-and-Affiliate — Backlog

_Last updated: 2026-05-20_

---

## Immediate — must complete before first live run

- [ ] **Verify Gemini end-to-end** — start server, confirm logs show Gemini returning listing content (not fallback), check `data/designs/` for generated PNGs
- [ ] **Create Etsy seller account** — etsy.com → sell on Etsy
- [ ] **Register Etsy developer app** — etsy.com/developers → get `ETSY_API_KEY` + `ETSY_API_SECRET`
- [ ] **Run `setup_etsy_auth.py`** — completes OAuth, writes `ETSY_ACCESS_TOKEN` to `.env`
- [ ] **Create Printful account** — printful.com → Dashboard → Stores → Connect Etsy → API → Generate token
- [ ] **Fill `.env`** — all empty values: `ETSY_API_KEY`, `ETSY_API_SECRET`, `ETSY_ACCESS_TOKEN`, `ETSY_SHOP_ID`, `PRINTFUL_API_KEY`, `ETSY_SHIPPING_PROFILE_ID`
- [ ] **First full live run** — `python main.py`, check Printful dashboard + Etsy drafts

---

## Business setup (run in parallel with technical work)

- [ ] **Proton Mail** — separate business email address
- [ ] **Starling Bank business account** — all trading income/outgoings through here
- [ ] **Bitwarden** — password manager for all credentials
- [ ] **Register as sole trader** — HMRC, once trading begins (can do before first sale)
- [ ] **Decide business name** — needed for Etsy shop, sole trader registration, Starling

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

---

## Won't do

- Auto-publish without review during initial phase
- Merge `pod` and `affiliate` branches ever
- Commit `.env` to git
