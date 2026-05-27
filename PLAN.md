# POD-and-Affiliate — Master Plan

> **START EVERY SESSION HERE.** Work the next unchecked item. Do not skip ahead.
> **Business context:** See [BUSINESS_PLAN.md](BUSINESS_PLAN.md).

---

## Project status

**Pivoted to eBay Arbitrage Bot (2026-05-26).** POD pipeline is fully replaced and archived.
Bot stack: Python 3.13, FastAPI, APScheduler, SQLAlchemy async, httpx, Claude Haiku.

Pipeline (fully built):
1. Scan eBay sold listings → 2. Match supplier (Avasam / BigBuy) → 3. Margin check →
4. Create eBay listing → 5. Monitor price/stock → 6. Fulfil paid orders

---

## Stage 1 — Accounts ✓

- [x] eBay developer account — App ID, Dev ID, Cert ID, Access Token in `.env`
- [x] Avasam developer account — `AVASAM_CONSUMER_KEY` + `AVASAM_SECRET_KEY` in `.env`
- [x] BigBuy account — `BIGBUY_API_KEY_PROD` + `BIGBUY_API_KEY_TEST` in `.env`
- [ ] **[Nick]** Amazon Associates UK — amazon.co.uk/associates (free, ~1-3 days). Unlocks PA API (price benchmarking) + affiliate programme.

---

## Stage 2 — Bot live ✓ (scanner blocked on rate limit reset)

All code complete. Bot runs. Three issues resolved as of 2026-05-27:

- [x] eBay Finding API parameters correct — confirmed via diagnostic
- [x] Rate limit hit from test runs — **resets ~07:00 UTC 2026-05-28**. Scanner will work after that.
- [x] Avasam two-step auth — `consumer_key + secret_key → access_token` — built correctly
- [x] BigBuy prod/test environments — both keys in `.env`, `BIGBUY_USE_SANDBOX=False`

**After rate limit resets (tomorrow morning):**
- [ ] **[Nick]** Run `python main.py` — pipeline will attempt first scan. Check dashboard at http://localhost:8081.
- [ ] **[Nick]** Confirm scanner logs show sold items being found (check `INFO eBay scanner: X sold items fetched`)
- [ ] **[Nick]** Confirm Avasam/BigBuy source matching logs (check for `matched supplier product`)
- [ ] **[Nick]** Confirm first eBay listing is created (check Active Listings panel in dashboard)

---

## Stage 3 — First live listing (v1.0.0-arb)

- [ ] **[Nick]** First listing created and confirmed live in eBay Seller Hub
- [ ] **[Claude]** Tag `v1.0.0-arb`

---

## Stage 4 — Tune thresholds

After first cycle completes, review:

- [ ] **[Nick]** Check match rate — what % of scanned items find a supplier match? Target: ≥20%
  - If low: increase `MATCH_THRESHOLD` leniency, or expand categories in `ebay_sold_scanner.py`
- [ ] **[Nick]** Check margin filter — are good-margin items passing? Review `MIN_PROFIT_GBP` / `MIN_MARGIN_PCT` in `.env`
- [ ] **[Nick]** Check `LISTINGS_PER_CYCLE` (default 5) — increase once first batch confirmed working

---

## Stage 5 — Monitor + fulfilment live

- [ ] **[Nick]** Wait for a paid eBay order to arrive
- [ ] **[Nick]** Confirm order poller picks it up and submits to Avasam/BigBuy
- [ ] **[Nick]** Confirm tracking number written back to eBay

---

## Stage 6 — Scale

- [ ] Increase `LISTINGS_PER_CYCLE` to 20–50 once first batch confirmed profitable
- [ ] Add Amazon PA API price benchmarking (once Associates approved)
- [ ] Telegram alerts for new sales
- [ ] Consider eBay Basic Shop (£19.99/mo) once ≥8 sales/month — reduces FVF ~9.9% vs 12.8%

---

## Affiliate workstream (separate `affiliate` branch — not started)

- [ ] **[Nick]** Sign up for Amazon Associates UK (same account unlocks both PA API + affiliate)
- [ ] **[Nick]** Sign up for ClickUp affiliate programme
- [ ] **[Nick]** Sign up for Make (Integromat) affiliate programme
- [ ] **[Claude]** Scaffold Jekyll site on `affiliate` branch
- [ ] **[Claude]** Draft first 3 articles

---

## Business rules

- eBay FVF: 12.8% + £0.30. Net = `sell_price × 0.872 − 0.30`
- Min profit: £3.00 (`MIN_PROFIT_GBP`). Min margin: 25% (`MIN_MARGIN_PCT`).
- End listing if margin drops below 15% (hardcoded in `arbitrage/monitor.py`)
- Finding API call budget: 7 categories × 1 page = 7 calls/scan. Resets daily midnight PT.
- `.env` is gitignored — never commit secrets. Single source for all credentials.
- `pod` and `affiliate` branches never merge.

---

## Versioning

| Tag | Milestone |
|-----|-----------|
| `v0.3.0` | Last POD milestone — Printful + eBay pipeline confirmed |
| `v1.0.0-arb` | First live arbitrage listing (pending) |
| `v1.x.0-arb` | Feature additions |
