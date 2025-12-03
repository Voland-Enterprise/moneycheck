import os
from dataclasses import dataclass
from typing import Optional


def _load_dotenv_if_present(path: str = ".env") -> None:
    if not os.path.exists(path):
        return

    try:
        with open(path, "r", encoding="utf-8") as env_file:
            for line in env_file:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                os.environ.setdefault(key, value)
    except OSError:
        return


_load_dotenv_if_present()


@dataclass
class AhrefsConfig:
    api_token: str
    base_url: str = "https://apiv2.ahrefs.com"
    delay_seconds: float = 0.5
    max_retries: int = 2
    backoff_factor: float = 1.5


@dataclass
class MozConfig:
    access_id: str
    secret_key: str
    base_url: str = "https://lsapi.seomoz.com/v2/url_metrics"
    delay_seconds: float = 0.5
    max_retries: int = 2
    backoff_factor: float = 1.5


@dataclass
class DomainConfig:
    strip_www: bool = True


@dataclass
class AppConfig:
    ahrefs: Optional[AhrefsConfig]
    moz: Optional[MozConfig]
    domain: DomainConfig = DomainConfig()


class MissingConfigError(RuntimeError):
    """Raised when required API configuration is absent."""


THRESHOLD_ENV_WARNING = (
    "Environment variables for Ahrefs or Moz are not fully set. "
    "Requests to the respective APIs will be skipped."
)


def load_config() -> AppConfig:
    ahrefs_token = os.getenv("AHREFS_API_TOKEN")
    moz_access_id = os.getenv("MOZ_ACCESS_ID")
    moz_secret_key = os.getenv("MOZ_SECRET_KEY")

    ahrefs_config = None
    moz_config = None

    if ahrefs_token:
        ahrefs_config = AhrefsConfig(api_token=ahrefs_token)

    if moz_access_id and moz_secret_key:
        moz_config = MozConfig(access_id=moz_access_id, secret_key=moz_secret_key)

    return AppConfig(ahrefs=ahrefs_config, moz=moz_config)
