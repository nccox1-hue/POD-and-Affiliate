# Config State

Current live configuration as of 2026-05-30. No credentials stored here.

### Margin thresholds
- `MIN_PROFIT_GBP`: £3.00
- `MIN_MARGIN_PCT`: 25%
- End listing if margin drops below: 15%
- eBay FVF: 12.8% + £0.30

### Scan price range
- `MIN_EBAY_PRICE`: £8
- `MAX_EBAY_PRICE`: £80

### Scheduling
- Full pipeline scan: every 24h
- Price/stock monitor: every 12h
- Order poller: every 2h

### Status
- eBay scanner: BLOCKED (Finding API decommissioned Feb 2025)
- Suppliers: Avasam (stub, no key), BigBuy (stub, no key)
- Active focus: crypto/prediction market arb sandbox via MCPs
