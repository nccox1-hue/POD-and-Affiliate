# Decisions

### 2026-05-26: Pivot from POD to eBay Arbitrage

Abandoned the POD (print-on-demand) pipeline entirely. Replaced with zero-stock eBay arbitrage bot.

**Rationale:** POD required upfront design effort and had no proven demand signal. Arbitrage uses eBay sold listings as demand proof — only list what has already sold. Zero inventory, zero upfront cost.

**Stack:** Python 3.13, FastAPI, APScheduler, SQLAlchemy async, aiosqlite, httpx, Claude Haiku (listing copy), Jinja2.

---

### 2026-05-29: eBay Finding API confirmed decommissioned

`findCompletedItems` was decommissioned 5 February 2025. The scanner input is permanently broken.

**Impact:** v1.0.0-arb is blocked. Cannot scan eBay sold listings without a replacement source.

**Options identified:** Playwright scraping (free, fragile), Apify actor (paid, reliable). Decision deferred pending supplier billing review.

---

### 2026-05-29: Strategic pivot to crypto/prediction market sandbox

With the eBay scanner broken and supplier costs (Avasam £24.99+VAT/mo, BigBuy ~£84/mo) hard to justify without live listings, focus shifted to a crypto funding rate arb + prediction market arb sandbox.

**Rationale:** Zero cost to explore (Binance testnet), no supplier dependency, validates the bot architecture on a different arb type.

**MCPs installed:** ccxt (funding rates/spot-perp spreads), funding-rates-mcp, prediction-markets-mcp. All three had Windows startup issues fixed 2026-05-30.

---

### 2026-05-30: MCP startup fixes

Three MCPs failed to start on Windows:

- **ccxt**: Changed from `npx -y` to global `mcp-server-ccxt` command (avoids npx startup delay)
- **funding-rates**: Patched uvx cache `cli.py` — `app_lifespan` was a sync generator, needed `@asynccontextmanager` + `async def`
- **prediction-markets**: `.cmd` launcher called `.js` directly, triggering Windows Script Host. Fixed by invoking `node index.js` explicitly in settings.json

---

### 2026-05-30: Agent memory system initialized

Sub-agents (`continuous-improvement`, `project-memory`) added to `.claude/agents/`. Mirror of the stocks-scanner agent setup, adapted for the arbitrage bot context.
