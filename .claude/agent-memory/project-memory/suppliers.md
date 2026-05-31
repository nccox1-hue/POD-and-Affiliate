# Suppliers

### Avasam
- **Cost:** £24.99+VAT/month
- **Status:** Account exists, API stub built, no active key in use
- **Integration:** `scanner/avasam_sourcer.py` — stub awaiting key
- **Notes:** Primary sourcing option. UK-based dropship platform.

### BigBuy
- **Cost:** ~£84/month + €90 one-off setup
- **Status:** Not subscribed. Secondary option.
- **Integration:** `scanner/bigbuy_sourcer.py` — stub built
- **Notes:** European supplier. Higher cost. Only justified if Avasam coverage is thin.

### Decision (2026-05-29)
Both supplier subscriptions under review pending eBay scanner fix. No point paying if the pipeline can't source live opportunities. Review after Playwright/Apify decision.
