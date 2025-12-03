import re
from urllib.parse import urlparse

from .config import DomainConfig


DOMAIN_PATTERN = re.compile(r"^[a-z0-9.-]+$")


def normalize_domain(raw: str, config: DomainConfig) -> str:
    """Normalize a domain string for consistent API calls."""
    if not raw:
        return ""

    candidate = raw.strip().lower()

    if "//" in candidate:
        parsed = urlparse(candidate)
        candidate = parsed.netloc or parsed.path
    else:
        # Prepend scheme for parsing paths correctly
        parsed = urlparse(f"//{candidate}", scheme="http")
        candidate = parsed.netloc

    candidate = candidate.split("/")[0]

    if config.strip_www and candidate.startswith("www."):
        candidate = candidate[4:]

    candidate = candidate.split(":")[0]

    if not DOMAIN_PATTERN.match(candidate):
        return ""

    return candidate
