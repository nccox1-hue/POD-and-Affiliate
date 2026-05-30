# POD-and-Affiliate — Backlog

_Last updated: 2026-05-29 (session 6)_

---

## Immediate — unblock arbitrage bot

- [ ] **Manual: check billing** — log into Avasam, BigBuy, Monzo. Confirm what is actively billing. Cancel/pause subscriptions not generating value. BigBuy: did you pay the €90 registration fee?
- [ ] **Fix scanner** — Finding API (`findCompletedItems`) was decommissioned 5 Feb 2025. Choose fix:
  - Option A: Playwright MCP scrapes Terapeak (eBay Seller Hub) — free, requires Playwright MCP installed
  - Option B: Apify `harvestlab/ebay-scraper` — ~$0.003/item, direct drop-in replacement
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
| 2026-05-29 | eBay Finding API confirmed decommissioned | `findCompletedItems` shut down 5 Feb 2025. errorId 10001 is a gateway block, not a quota. Playwright MCP or Apify scraper required as replacement. |
| 2026-05-29 | New income focus: crypto/prediction market arb sandbox | eBay arbitrage stalled on scanner fix + supplier billing uncertainty. Sandbox crypto funding rate arb and prediction market arb while arbitrage bot is unblocked. No capital deployed until mechanics proven. |
| 2026-05-29 | MCPs installed: ccxt, funding-rates, prediction-markets | Global `~/.claude/settings.json`. CCXT uses `@mcpfun/mcp-server-ccxt`. Funding rates via `uvx funding-rates-mcp`. Prediction markets via `npx prediction-markets-mcp`. Require Claude Code restart. |
| 2026-05-29 | Automotive SaaS backlogged | Strong domain advantage (30yr technical) but direction unclear. Parked until focused thinking session. |

---

## Income diversification backlog (parked — revisit after arbitrage bot generating revenue)

### Active focus (sandbox first, no capital)
- [ ] **Crypto funding rate arb** — explore via `funding-rates` MCP + CCXT MCP. Binance testnet. Delta-neutral (spot long + perp short). Understand mechanics before deploying any capital.
- [ ] **Prediction market arb** — explore via `prediction-markets` MCP (Polymarket/Kalshi). Identify cross-platform pricing discrepancies. Paper trade first.
- [ ] **CCXT MCP sandbox** — connect to Binance testnet, run market data queries, understand order placement API before live trading.

### Backlogged income ideas
- [ ] **AI video agency (Higgsfield)** — highest ceiling (£400/day with 8 clients), but client acquisition is the bottleneck. Revisit when capacity exists.
- [ ] **B2B lead generation** — automated LinkedIn/contact enrichment service. Parked: GDPR complexity and commoditisation risk.
- [ ] **Automotive SaaS** — building a tool/SaaS for dealers, workshops, or OEMs. Strong domain advantage (30yr automotive technical). Direction TBD — revisit with fresh thinking.
- [ ] **Affiliate site** — EV/automotive niche on `affiliate` branch. Expert-led, author-attributed content. 12+ month horizon.
- [ ] **Sell the arbitrage bot** — package on Lemon Squeezy (£149–£249). Once bot is proven working, document and list. Low effort, recovers dev investment.
- [ ] **Adobe Stock AI video** — batch Higgsfield clips to Adobe Stock. Side stream. Low effort once pipeline built.
- [ ] **Freqtrade bot** — Python crypto bot on Bybit. 2–3 year compounding horizon. Set up after funding rate arb is understood.

### MCPs to install when needed
- Playwright MCP (`@playwright/mcp`) — fixes eBay scanner via Terapeak scraping
- Apify MCP (`@apify/actors-mcp-server`) — needs `APIFY_TOKEN`
- Alpha Vantage MCP — needs free API key
- FRED economic data MCP — needs free API key
- Alpaca MCP — needs brokerage account
- eBay MCP (325 tools) — needs eBay credentials
- Firecrawl MCP — needs free API key
- Freqtrade MCP — needs running Freqtrade instance
- Prediction market execution (PMXT) — needs Kalshi/Polymarket account

---

## Won't do

- Amazon→eBay dropship fulfilment — explicitly prohibited by eBay policy
- AliExpress sourcing — 2-4 week delivery, excluded (Nick's preference)
- Argos sourcing — no API, requires manual collection
- Merge `pod` and `affiliate` branches
- Commit `.env` to git
