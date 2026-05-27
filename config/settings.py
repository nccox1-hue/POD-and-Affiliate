from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    gemini_api_key: str = ""

    ebay_app_id: str = ""
    ebay_app_id_sandbox: str = ""
    ebay_use_sandbox: bool = False
    ebay_dev_id: str = ""
    ebay_cert_id: str = ""
    ebay_access_token: str = ""
    ebay_refresh_token: str = ""
    ebay_runame: str = "Nick_Cox-NickCox-NickPri-bzvqjfl"
    ebay_postal_code: str = ""

    # Avasam — two-step auth: consumer_key + secret_key → access_token at runtime
    # Find both in Avasam dashboard: Settings → User Management → API Keys
    avasam_consumer_key: str = ""
    avasam_secret_key: str = ""

    # BigBuy — prod and test keys (test env uses api.sandbox.bigbuy.eu)
    bigbuy_api_key_prod: str = ""
    bigbuy_api_key_test: str = ""
    bigbuy_use_sandbox: bool = False  # set True in .env to hit test environment

    # Amazon PA API — price benchmarking + affiliate (once Associates approved)
    amazon_access_key: str = ""
    amazon_secret_key: str = ""
    amazon_associate_tag: str = ""

    # Arbitrage thresholds
    min_profit_gbp: float = 3.00
    min_margin_pct: float = 25.0
    max_ebay_price: float = 80.00
    min_ebay_price: float = 8.00
    min_sold_count: int = 3

    log_level: str = "INFO"
    database_url: str = "sqlite+aiosqlite:///./data/pod_bot.db"
    scan_interval_hours: int = 24
    listings_per_cycle: int = 5

    owner_email: str = ""
    owner_email_password: str = ""

    account_number: str = ""
    sort_code: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
