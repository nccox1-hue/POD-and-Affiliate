# POD-and-Affiliate — Master Plan

> **START EVERY SESSION HERE.** Pick the stream you're working on and find the next unchecked item.
> **Business context:** See [BUSINESS_PLAN.md](BUSINESS_PLAN.md).

---

## Cost exposures

| Service | Cost | Status |
|---|---|---|
| **Avasam** | £0 now → £30/mo to unlock API | Free tier has NO inventory API access. Advanced (£24.92+VAT/mo, 2,500 sourcing credits) needed for Stream C. **Hold until Streams A/B generating revenue.** |
| **BigBuy** | ~£84/mo | Not subscribed — do not subscribe. Avasam first. |
| **Monzo Pro** | £9/mo | Accepted. Review Aug 2026 — downgrade if expense/accounting features unused |
| **Bybit** | £0 | Not open yet. Testnet free. No real cost until capital deposited |
| **GitHub Pages / Claude API** | £0 | Free / pennies |

---

## Revenue streams — current status

| Stream | Code built? | Running? | Next action |
|---|---|---|---|
| **A1** Etsy Wall Art (£2.49) | ✅ Built | ⏳ Running | Monitor Etsy Seller Hub |
| **A2** Etsy Excel Templates (£10–£30) | ✅ Built 2026-05-31 | ⏳ Needs vet | Nick: review generated files, then run |
| **B** Affiliate Site + Udemy course | ✅ Site built | 🔧 10 articles being generated | Apply for AdSense |
| **C** eBay Arbitrage (£50–£300 items) | ✅ Built | ⏳ Running | Upgrade Avasam when A/B earning |
| **E** Udemy Course | 📋 Planned | ❌ Not started | Claude preps curriculum + scripts |
| **D** Crypto Funding Arb | ⏸ Parked | — | Revisit if capital available |

---

## A — Etsy Digital Downloads

### Stage A1 — Build ✅ Complete

- [x] `pod_digital/etsy_bestseller_scanner.py` — queries Etsy API for bestselling digital listings, extracts themes ✅
- [x] `pod_digital/artwork_generator.py` — Pollinations.ai image gen, Pillow resize to 4 print sizes ✅
- [x] `pod_digital/listing_publisher.py` — creates digital listing, uploads files, uploads preview image, publishes ✅
- [x] `pod_digital/pipeline.py` — full orchestration, wired into APScheduler (every 56h) ✅

### Stage A2 — Test run

- [ ] **[Nick]** Run `python main.py` — check dashboard at http://localhost:8081
- [ ] **[Nick]** Confirm a digital listing appears in Etsy Seller Hub with attached download files
- [ ] **[Nick]** Review listing — title, image, description, tags. Confirm it looks right.

### Stage A3 — Scale

- [ ] **[Nick]** First digital download sale confirmed
- [ ] **[Claude]** Review view/conversion rates — tune keyword targeting if needed
- [ ] **[Claude]** Add second category (budget planners / finance trackers) once wall art stable

---

## B — Affiliate Site (Automation/Excel niche)

### Stage B1 — Accounts

- [x] Amazon Associates UK — approved ✅
- [x] Awin — **declined** (site too new). Re-apply Aug 2026 once 30+ articles and traffic. ✅
- [x] Impact.com — **declined** (site too new). Re-apply Aug 2026. ✅
- [ ] **[Nick]** Rakuten Advertising — [rakutenadvertising.com](https://rakutenadvertising.com) — Udemy's programme lives here. Apply now.
- [ ] **[Nick]** Monday.com direct affiliate — [monday.com/affiliates](https://monday.com/affiliates) (PartnerStack — less strict than Awin)
- [ ] **[Nick]** Zapier direct affiliate — [zapier.com/partners/affiliate](https://zapier.com/partners/affiliate) (PartnerStack)
- [ ] **[Nick]** Make.com direct affiliate — [make.com/en/affiliate-program](https://make.com/en/affiliate-program)
- [ ] **[Nick]** Google Search Console — verify site at [search.google.com/search-console](https://search.google.com/search-console) — paste DNS record, tracks search rankings

### Stage B2 — Site and automation ✅ Complete

- [x] Jekyll site scaffolded and live at https://nccox1-hue.github.io/POD-and-Affiliate/ ✅
- [x] 2 seed articles published (Power Query merge tables, Power Automate approval workflow) ✅
- [x] `affiliate_writer/keyword_queue.py` — 30 seed keywords queued in `data/affiliate_keywords.json` ✅
- [x] `affiliate_writer/article_writer.py` — Claude Haiku writes 1,500–2,500 word Jekyll articles ✅
- [x] `affiliate_writer/git_publisher.py` — commits article to affiliate-site worktree, pushes to affiliate branch ✅
- [x] `affiliate_writer/pipeline.py` — wired into APScheduler (every 56h, ~3x/week) ✅

### Stage B3 — Grow

- [ ] **[Nick]** Submit sitemap to Google Search Console once verified: `https://nccox1-hue.github.io/POD-and-Affiliate/sitemap.xml`
- [ ] **[Nick]** Check Search Console monthly — which articles getting impressions
- [ ] **[Claude]** Re-apply to Awin + Impact Aug 2026 (automate this reminder)
- [ ] **[Claude]** Expand keyword queue when current 30 are exhausted

---

## C — eBay Zero-Stock Arbitrage

### Stage C1 — Scanner ✅ Complete

- [x] `scanner/ebay_sold_scanner.py` — Playwright-based, keyword searches, confirmed 200+ results per term ✅
- [x] Playwright + Chromium installed into Python 3.13 ✅

### Stage C2 — First live listing

- [ ] **[Nick]** Run `python main.py` — confirm `INFO eBay scanner: X sold items fetched` in logs
- [ ] **[Nick]** Confirm supplier match logs appear (`matched supplier product`)
- [ ] **[Nick]** Confirm first eBay listing created and live in eBay Seller Hub
- [ ] **[Claude]** Tag `v1.0.0-arb`

### Stage C3 — Tune

- [ ] **[Nick]** Check match rate — target ≥20%. Adjust `MIN_PROFIT_GBP` / `MIN_MARGIN_PCT` in `.env` if needed
- [ ] **[Claude]** Increase `LISTINGS_PER_CYCLE` 5 → 20 once first batch profitable
- [ ] **[Nick]** Consider eBay Basic Shop (£19.99/mo) at ≥8 sales/month — FVF drops 12.8% → 9.9%

---

## D — Crypto Funding Rate Arbitrage

**Current rates (checked 2026-05-31): BNB ~15% annualised, ETH ~6%, BTC ~5.5%**

### Stage D1 — Account setup (Nick's actions — blocks everything else)

- [ ] **[Nick]** Create [Bybit](https://www.bybit.com) account — FCA-registered, UK-legal
- [ ] **[Nick]** Complete KYC (passport/driving licence + selfie, ~10 min)
- [ ] **[Nick]** Enable Bybit Testnet at [testnet.bybit.com](https://testnet.bybit.com)
- [ ] **[Nick]** Generate testnet API keys — Read + Trade only, **never enable Withdraw**
- [ ] **[Nick]** Add to `.env`: `BYBIT_TESTNET_API_KEY` and `BYBIT_TESTNET_API_SECRET`

### Stage D2 — Build modules (Claude — can start once keys in .env)

- [ ] **[Claude]** `sandbox/funding_rate_scanner.py` — fetches funding rates across Bybit + Binance, ranks by annualised yield, logs to database
- [ ] **[Claude]** `sandbox/position_manager.py` — opens/closes delta-neutral pairs (spot long + perp short), tracks P&L
- [ ] **[Claude]** Wire into APScheduler and dashboard

### Stage D3 — Testnet run

- [ ] **[Nick]** Run bot on testnet for 1 week — confirm funding payments collected correctly
- [ ] **[Nick]** Review P&L dashboard — positions opening/closing as expected?

### Stage D4 — Go live

- [ ] **[Nick]** Generate live Bybit API keys (same permissions — no Withdraw)
- [ ] **[Nick]** Add to `.env`: `BYBIT_API_KEY` and `BYBIT_API_SECRET`
- [ ] **[Claude]** Set position limits: max 20% capital per pair, max 3 pairs
- [ ] **[Nick]** Deposit starting capital (your call — £500–£2,000 suggested)

---

## What's next — priority order

```
NICK — do these now (no code needed):
  1. python main.py — test the bot. All four pipelines run on first start.
  2. Bybit account + KYC — unblocks Stream D
  3. Rakuten, Monday.com, Zapier, Make.com affiliate signups
  4. Google Search Console — verify site, submit sitemap

CLAUDE — builds in order once Nick's actions are done:
  1. Stream D: funding rate scanner + position manager (needs Bybit keys)
  2. Fix any issues from the python main.py test run
  3. Keyword queue expansion (when 30 seeds are exhausted)
```

---

## Business rules

- `.env` is the single store for all credentials — gitignored, backed up to Proton Drive
- `pod` and `affiliate` branches never merge
- eBay: FVF 12.8% + £0.30. Min profit £3. Min margin 25%. End listing if margin drops below 15%
- Crypto: never enable Withdraw on API keys. Testnet before live capital
- Affiliate: every article must include ASA disclosure (legal requirement UK)
- Awin + Impact: re-apply August 2026 once 30+ articles live with search traffic

## Versioning

| Tag | Milestone |
|---|---|
| `v0.3.0` | Physical POD verified (archived) |
| `v1.0.0-arb` | First live eBay arbitrage listing |
| `v1.0.0-digital` | First Etsy digital download listing published by bot |
| `v1.0.0-affiliate` | Affiliate site with 10+ auto-published articles |
| `v1.0.0-funding` | First live funding rate position on Bybit |
