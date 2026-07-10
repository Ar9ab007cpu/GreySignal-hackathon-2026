import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass(frozen=True)
class Settings:
    http_timeout_seconds: int = int(os.getenv("HTTP_TIMEOUT_SECONDS", "30"))
    world_bank_base_url: str = os.getenv("WORLD_BANK_BASE_URL", "")
    world_bank_docs_url: str = os.getenv("WORLD_BANK_DOCS_URL", "")
    gdelt_doc_url: str = os.getenv("GDELT_DOC_URL", "")
    open_meteo_forecast_url: str = os.getenv("OPEN_METEO_FORECAST_URL", "")
    open_meteo_geocoding_url: str = os.getenv("OPEN_METEO_GEOCODING_URL", "")
    exchange_rate_api_base_url: str = os.getenv("EXCHANGE_RATE_API_BASE_URL", "")
    exchange_rate_api_key: str = os.getenv("EXCHANGE_RATE_API_KEY", "")
    un_comtrade_url: str = os.getenv("UN_COMTRADE_URL", "")
    un_comtrade_api_key: str = os.getenv("UN_COMTRADE_API_KEY", "")
    groq_api_url: str = os.getenv("GROQ_API_URL", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    acled_api_url: str = os.getenv("ACLED_API_URL", "")


settings = Settings()
