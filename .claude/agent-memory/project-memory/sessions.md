# Sessions

### 2026-05-30: Agent setup + MCP fixes

**What changed:** Three MCP servers (ccxt, funding-rates, prediction-markets) debugged and fixed. Sub-agents (continuous-improvement, project-memory) created and seeded. Agent memory store initialised.
**Decisions:** See decisions.md — MCP fix approaches documented.
**Config state:** No threshold changes. settings.json updated with corrected MCP commands.
**MCPs/tools:** ccxt → global mcp-server-ccxt; funding-rates → patched cli.py async bug; prediction-markets → node explicit invocation.
**Next:** Restart Claude Code to pick up MCP changes. Verify all three load. If ccxt loads — explore funding rate data on Binance testnet.
