# Sessions

### 2026-05-31: Major build session — streams A, B, C built and A/B live

**What changed:** Etsy digital downloads pipeline built and 3 listings live. Affiliate article auto-publisher built and 7+ articles live. Playwright eBay scanner built (200+ items/search). Excel template pipeline built (not yet confirmed). Crypto arb parked (UK FCA restriction + poor risk/reward). Dashboard updated for all streams. Git history cleaned of secrets (BW_SESSION, eBay App ID). CLAUDE.md updated with financial stress-test rule.
**Decisions:** Revenue target £1,000/month. Physical POD permanently shelved. Crypto parked. eBay price floor raised £8→£50. Avasam free tier has no API — upgrade deferred. Local MCPs confirmed non-functional in VS Code extension.
**Bugs fixed:** Etsy listing type field (`is_digital`→`type:"download"`), `when_made` enum value, 401 token auto-refresh. eBay hardcoded credentials removed from setup_ebay_auth.py.
**Config state:** MIN_EBAY_PRICE=50, MAX_EBAY_PRICE=300. Digital pipeline: 56h/3 listings. Affiliate: 24h/1 article.
**Next:** Debug Excel template listing creation. Amazon Associates bank details (Nick). Google Search Console (Nick). Monitor Etsy listings for views/sales.

### 2026-05-30: Agent setup + MCP fixes

**What changed:** Three MCP servers (ccxt, funding-rates, prediction-markets) debugged and fixed. Sub-agents (continuous-improvement, project-memory) created and seeded. Agent memory store initialised.
**Decisions:** See decisions.md — MCP fix approaches documented.
**Config state:** No threshold changes. settings.json updated with corrected MCP commands.
**MCPs/tools:** ccxt → global mcp-server-ccxt; funding-rates → patched cli.py async bug; prediction-markets → node explicit invocation.
**Next:** Restart Claude Code to pick up MCP changes. Verify all three load. If ccxt loads — explore funding rate data on Binance testnet.
