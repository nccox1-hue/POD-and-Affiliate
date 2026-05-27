# POD-and-Affiliate — Backlog

_Last updated: 2026-05-27 (session 5)_

---

## Immediate — before declaring v1.0.0-arb

- [ ] **First production scan** — flip `EBAY_USE_SANDBOX=False`, run bot after 08:00 BST 2026-05-28, confirm `X sold items fetched` in logs
- [ ] **Verify Avasam source matching** — confirm auth token exchange works and at least one product is matched from inventory
- [ ] **Verify BigBuy search** — confirm prod key works and returns products
- [ ] **First eBay listing created** — check Seller Hub, confirm listing is live and margin logged in DB
- [ ] **Tag v1.0.0-arb** — once first listing confirmed live

---

## Dev environment

- [x] Python 3.13 at `C:\Users\nickc\AppData\Local\Python\python-3.13-64\python.exe`
- [x] MSVCP140.dll fix applied (greenlet / SQLAlchemy async)
- [x] All supplier API credentials in `.env`
- [x] eBay sandbox mode working

---

## Business setup

- [x] Monzo Business Pro — approved, funded
- [x] Proton Mail — shop.2026.uk@proton.me
- [ ] **Register as sole trader** — Nick Cox Digital, SIC 74100, HMRC — trigger: first sale received
- [ ] **Amazon Associates UK** — amazon.co.uk/associates (free, ~1-3 days). Also unlocks PA API for price benchmarking.

---

## Short-term improvements (post first-listing)

- [ ] **Tune match threshold** — review Avasam match rate after first cycle. `MATCH_THRESHOLD=2` may need adjusting up (fewer false positives) or down (more matches)
- [ ] **Dashboard — scanned items panel** — add "match found?" indicator per ScannedItem so it's easy to spot what's matching vs falling through
- [ ] **Telegram alerts** — notify on new listing created and on paid order received
- [ ] **Email notifications** — Proton SMTP alert when pipeline errors (no listings created despite items scanned)
- [ ] **Seller Hub sanity check** — after first 24h, review listing quality: title, description, price vs competitors

---

## Scaling (once first batch profitable)

- [ ] Increase `LISTINGS_PER_CYCLE` from 5 → 20–50
- [ ] Add more eBay target categories if match rate is low
- [ ] Amazon PA API price benchmarking — once Associates approved; compare our eBay price vs Amazon to confirm we're competitive
- [ ] eBay Basic Shop subscription (£19.99/mo) — break-even ~8 sales/month; reduces FVF ~9.9% vs 12.8%
- [ ] A/B listing copy — generate two Claude variants per item, track which converts better

---

## Financial tracking

- [ ] Transaction log in SQLite — `transactions` table: date, type (sale/fee/payout), amount, source, reference ID
- [ ] Monzo API integration — pull business account transactions, cross-reference with eBay payouts, calculate net margin
  - Auth: OAuth2 — developers.monzo.com. Business Pro accounts may need manual API access approval — verify first.
- [ ] Monthly P&L summary — gross sales, eBay fees, supplier costs, net profit
- [ ] Self-assessment export — annual CSV for HMRC

---

## Affiliate workstream (separate `affiliate` branch — not started)

- [ ] Sign up for Amazon Associates UK (same account: PA API + affiliate)
- [ ] Sign up for ClickUp affiliate (20% recurring)
- [ ] Sign up for Make (Integromat) affiliate (20% recurring)
- [ ] Scaffold Jekyll site on `affiliate` branch — homepage, about, article template, disclosure
- [ ] Draft first 3 articles — roundup, comparison, how-to
- [ ] Connect Google Search Console

---

## Decisions log

| Date | Decision | Reason |
|------|----------|--------|
| 2026-05-19 | Python 3.13 on Windows | Current machine setup |
| 2026-05-21 | Bank: Monzo Business Pro | Tax pots, familiar app |
| 2026-05-21 | Sole trader name: Nick Cox Digital | Broad enough for POD, trading, automation |
| 2026-05-22 | `.env` backed up to Proton Drive via rclone | Automated, E2E encrypted |
| 2026-05-23 | eBay Trading API (Auth'n'Auth) over REST/Inventory API | Production OAuth requires HTTPS redirect — localhost rejected. Auth'n'Auth works immediately. |
| 2026-05-23 | eBay account: cox333 / 333 Trading | Existing 790-feedback account — strong starting position |
| 2026-05-24 | eBay XML must escape strings | URLs with `&` break raw XML. Fixed with `xml.sax.saxutils.escape` |
| 2026-05-26 | Pivot from POD to eBay arbitrage | POD text designs had no competitive signal. Arbitrage uses proven sales data. |
| 2026-05-26 | Avasam (primary) + BigBuy (secondary) suppliers | UK wholesale, eBay-policy compliant, dropship API. Amazon→eBay dropship is explicitly prohibited by eBay. |
| 2026-05-26 | Avasam two-step auth | POST `consumer_key + secret_key` → `access_token`. Not a simple Bearer key. Auth URL: `https://app.avasam.com/api/auth/request-token` |
| 2026-05-26 | BigBuy prod + test environments | Both keys in `.env`. `BIGBUY_USE_SANDBOX=False` for prod by default. |
| 2026-05-27 | eBay Finding API rate limit is per-day | `findCompletedItems` quota exhausted from repeated test runs. Resets midnight PT (~08:00 BST). Use sandbox (`svcs.sandbox.ebay.com`) for dev testing. |
| 2026-05-27 | Scanner pages reduced 2→1 per category | Halves daily API call budget (14→7 per full scan). Sandbox confirmed all 7 category IDs valid. |

---

## Won't do

- Amazon→eBay dropship fulfilment — explicitly prohibited by eBay policy
- AliExpress sourcing — 2-4 week delivery, excluded (Nick's preference)
- Argos sourcing — no API, requires manual collection
- Merge `pod` and `affiliate` branches
- Commit `.env` to git
