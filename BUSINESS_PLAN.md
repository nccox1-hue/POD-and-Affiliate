# Business Plan — Nick Cox Digital
### Trading as NickPrintCo
**Prepared:** May 2026 | **Review date:** November 2026

---

## 1. Business Summary

Nick Cox Digital is a sole trader business operating an automated Print-on-Demand (POD) retail operation under the brand **NickPrintCo**. The business uses AI-assisted automation to generate trending product designs, list them on Etsy, and fulfil orders globally via Printful — with no manual intervention per order.

The core value proposition is low operational overhead: the system runs on a 24-hour automated cycle, sourcing trends, generating designs, and publishing listings without manual input. Revenue scales with catalogue size, not time invested.

---

## 2. Owner

| Detail | Info |
|---|---|
| Name | Nick Cox |
| Location | England, UK |
| Legal structure | Sole trader |
| Business name | Nick Cox Digital |
| Trading name | NickPrintCo |
| Business email | shop.2026.uk@proton.me |
| Business bank | Monzo Business Pro — £9/month (2 months free) |
| SIC code | 74100 — Specialised Design Activities |

---

## 3. The Problem We Solve

Etsy buyers search daily for personalised, novelty, and trending gift products — particularly t-shirts, mugs, and accessories. Most small sellers cannot keep up with trend velocity manually. NickPrintCo uses automation to publish designs aligned with real-time search trends faster than manual competitors, giving it first-mover advantage on emerging keywords.

---

## 4. Products

All products are printed and fulfilled by **Printful** on a per-order basis. No stock is held.

| Product | Printful ID | Base Cost | Sell Price | Margin |
|---|---|---|---|---|
| Unisex T-Shirt (Bella+Canvas 3001) | 71 | ~£9 | £25 | ~£16 |
| Mug 11oz | 19 | ~£6 | £15 | ~£9 |
| Canvas Tote Bag | 358 | ~£8 | £20 | ~£12 |

**Design themes:** funny, dogs, gym, motivational, nature, vintage

**Future products (backlog):** hoodies, sweatshirts, kids tees, phone cases

---

## 5. Supplier

**Primary supplier: Printful**

- Founded 2013, established and financially stable
- Fulfilment centres in USA, UK, Europe, Australia, Japan
- No minimum order — truly print on demand
- Free to use — cost per fulfilled order only
- Native Etsy integration
- Handles printing, packing, shipping, and returns

**Dependency risk:** Single supplier. Printify and Printbase are identified alternatives if needed.

---

## 6. Sales Channel

**Primary: Etsy (etsy.com/shop/NickPrintCo)**

Etsy provides built-in buyer traffic, payment processing, and marketplace trust. No marketing spend required at launch. Etsy charges approximately 6.5% transaction fee plus listing fees (~$0.20 per listing).

**Future channel (Year 2+):** Shopify standalone store once catalogue and sales volume justify it. Own domain, lower fees, full brand control.

---

## 7. Target Market

| Market | Priority | Notes |
|---|---|---|
| United States | Primary | ~60-70% of Etsy traffic, largest POD buyer base |
| United Kingdom | Secondary | Home market, strong gift purchase behaviour |
| Canada | Third | English-speaking, high Etsy usage |
| Australia | Fourth | Similar profile to Canada |

**Customer profile:** Gift buyers, novelty seekers, pet owners, fitness enthusiasts, people buying for occasions (birthdays, Christmas, Mother's Day, Valentine's Day).

**Design language:** US English spelling and cultural references used in designs for maximum reach. UK English used in legal/business communications.

---

## 8. Technology & Automation

The business is powered by a custom-built Python automation pipeline:

| Component | Technology | Purpose |
|---|---|---|
| Trend scraping | Google Trends API | Identifies high-volume search keywords |
| Content generation | Google Gemini Flash (free tier) | Writes design prompts + Etsy listing copy |
| Image generation | Pollinations.ai (free, no API key) | Generates print-ready PNG designs |
| Product creation | Printful API | Creates and syncs products |
| Listing creation | Etsy API | Publishes draft listings to shop |
| Scheduling | APScheduler | Runs full cycle every 24 hours |
| Logging | SQLite + FastAPI dashboard | Tracks all jobs, trends, sales |

**Operating cost of the pipeline: £0/month** — all AI services used are free tier.

---

## 9. Revenue Model

Revenue is generated on each Etsy sale. Printful fulfils the order and deducts their base cost. The remainder is the gross margin.

**Per-unit economics (t-shirt example at £25 sell price):**

| Item | Amount | Notes |
|---|---|---|
| Sell price | £25.00 | |
| Printful base cost | −£9.00 | Bella+Canvas 3001 |
| Listing fee | −£0.16 | $0.20 USD per listing (on creation, not per sale) |
| Transaction fee | −£1.63 | 6.5% of order total |
| Payment processing fee | −£1.20 | 4% of order total + £0.20 |
| Regulatory Operating fee | −£0.08 | 0.32% of order total |
| **Gross margin per sale** | **~£12.93** | Assumes GBP listing currency |

**Fee notes:**
- **Set listing currency to GBP** — avoids the 2.5% currency conversion fee
- **Offsite Ads: opt out** — optional for most sellers; mandatory only above ~$10k/year sales. Adds 12-15% cost if enabled
- **One-time setup fee: £14** — paid on account creation, sunk cost
- Listing fee is charged per listing created/renewed, not per sale — amortised above assuming one sale per listing minimum

**Additional revenue streams (planned):**

| Stream | Timeline | Notes |
|---|---|---|
| Affiliate content site | Year 1-2 | GitHub Pages niche site with affiliate links |
| Shopify direct store | Year 2+ | Higher margins, own audience |
| Trading automation | Separate project | Stocks scanner — separate income stream |

---

## 10. Financial Projections

### Year 1 (Conservative / Realistic range)

| Period | Listings Live | Est. Monthly Sales | Est. Monthly Revenue |
|---|---|---|---|
| Months 1-3 | 0-50 | 0-2 | £0-30 |
| Months 4-6 | 50-200 | 5-15 | £75-215 |
| Months 7-9 | 200-400 | 15-40 | £215-570 |
| Months 10-12 | 400-600 | 40-80 | £570-1,140 |

| Scenario | Year 1 Total |
|---|---|
| Low | £500 |
| Mid | £2,000 |
| High | £4,500 |

### Key thresholds

| Threshold | Target |
|---|---|
| VAT registration | £90,000/year turnover — not expected Year 1 |
| Convert to Ltd company | ~£25,000/year profit |
| Self-assessment required | Any profit above personal allowance (£12,570) |

---

## 11. Costs

| Item | Cost |
|---|---|
| Printful (per order) | Deducted from sale — no upfront cost |
| Etsy one-time setup fee | £14.00 (paid) |
| Etsy listing fee | ~£0.16 per listing ($0.20 USD) |
| Etsy transaction fee | 6.5% per sale |
| Etsy payment processing | 4% + £0.20 per sale |
| Etsy regulatory fee | 0.32% per sale |
| Pipeline hosting | £0 (runs locally) |
| AI services | £0 (Gemini free tier, Pollinations free) |
| Business bank account | £9/month Monzo Business Pro (free months 1-2) |
| **Monthly fixed cost** | **£0** |

The business has no fixed monthly costs until it reaches a scale requiring paid hosting or upgraded API tiers.

---

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Etsy algorithm changes | Medium | High | Diversify to Shopify (Year 2) |
| Printful price increases | Low-Medium | Medium | Monitor; Printify as backup |
| Scraper API blocks | High (current) | Low | Fixed keyword bypass already built |
| Low early sales | High | Low | Expected — catalogue builds over time |
| Single supplier dependency | Low | High | Printify identified as alternative |
| HMRC compliance gap | Low | High | Register sole trader before first sale |

---

## 13. Milestones

| Milestone | Target | Status |
|---|---|---|
| v0.1.0 — Pipeline verified end-to-end | May 2026 | ✅ Complete |
| v0.2.0 — First Etsy draft listing created | Jun 2026 | ⏳ In progress |
| v0.3.0 — First Printful product synced | Jun 2026 | ⏳ Blocked on v0.2.0 |
| v1.0.0 — Full live automated run | Jul 2026 | ⏳ Blocked on credentials |
| Sole trader registration | Before first sale | ⏳ Pending |
| Starling Business account open | Jun 2026 | ⏳ Pending |
| 100 listings live | Aug 2026 | ⏳ |
| First sale | Aug-Sep 2026 | ⏳ |
| 500 listings live | Nov 2026 | ⏳ |

---

## 14. Next Actions

See [PLAN.md](PLAN.md) for the current working task list. Business plan review scheduled for November 2026.
