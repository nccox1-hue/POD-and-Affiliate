from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    gemini_api_key: str = ""

    etsy_api_key: str = ""
    etsy_api_secret: str = ""
    etsy_access_token: str = ""
    etsy_refresh_token: str = ""
    etsy_shop_id: str = ""

    printful_api_key: str = ""
    printful_store_id: str = ""
    printful_api_store_key: str = ""
    printful_api_store_id: str = ""
    printful_ebay_store_id: str = ""
    stability_api_key: str = ""

    ebay_app_id: str = ""
    ebay_dev_id: str = ""
    ebay_cert_id: str = ""
    ebay_access_token: str = ""
    ebay_refresh_token: str = ""
    ebay_runame: str = "Nick_Cox-NickCox-NickPri-bzvqjfl"
    ebay_postal_code: str = ""

    log_level: str = "INFO"
    database_url: str = "sqlite+aiosqlite:///./data/pod_bot.db"
    scan_interval_hours: int = 24
    listings_per_cycle: int = 5
    product_ids: str = "71,19,358"
    themes: str = "funny,dogs,gym,motivational,nature,vintage"
    etsy_shipping_profile_id: str = ""
    price_multiplier: float = 2.5

    @property
    def theme_list(self) -> List[str]:
        return [t.strip().lower() for t in self.themes.split(",") if t.strip()]

    @property
    def product_id_list(self) -> List[int]:
        return [int(p.strip()) for p in self.product_ids.split(",") if p.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
