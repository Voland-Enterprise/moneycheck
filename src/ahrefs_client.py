import logging
import time
from typing import Dict, Optional

import requests
from requests import Response

from .config import AhrefsConfig


log = logging.getLogger(__name__)


class AhrefsClient:
    def __init__(self, config: AhrefsConfig):
        self.config = config

    def _request_with_retry(self, params: Dict[str, str]) -> Optional[Response]:
        delay = self.config.delay_seconds
        for attempt in range(self.config.max_retries + 1):
            try:
                response = requests.get(self.config.base_url, params=params, timeout=15)
                if response.status_code == 429 or response.status_code >= 500:
                    log.warning(
                        "Ahrefs temporary error (status %s): %s", response.status_code, response.text
                    )
                    if attempt < self.config.max_retries:
                        time.sleep(delay)
                        delay *= self.config.backoff_factor
                        continue
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                log.warning("Ahrefs request failed: %s", exc)
                if attempt < self.config.max_retries:
                    time.sleep(delay)
                    delay *= self.config.backoff_factor
        return None

    def get_metrics(self, domain: str) -> Dict[str, Optional[float]]:
        """Return DR, UR (as PR surrogate) and organic keywords count for a domain."""
        params = {
            "token": self.config.api_token,
            "from": "domain_rating",
            "target": domain,
            "mode": "domain",
            "output": "json",
        }

        metrics = {"dr": None, "pr": None, "keywords": None}

        response = self._request_with_retry(params)
        time.sleep(self.config.delay_seconds)
        if response is None:
            return metrics

        try:
            payload = response.json()
            if payload.get("domain_rating") is not None:
                metrics["dr"] = float(payload["domain_rating"])
            if payload.get("url_rating") is not None:
                metrics["pr"] = float(payload["url_rating"])
        except Exception as exc:  # noqa: BLE001
            log.warning("Ahrefs JSON parsing failed for %s: %s", domain, exc)

        # fetch organic keywords count
        keywords_params = {
            "token": self.config.api_token,
            "from": "positions_metrics",
            "target": domain,
            "mode": "domain",
            "output": "json",
        }
        response_kw = self._request_with_retry(keywords_params)
        if response_kw is not None:
            try:
                payload = response_kw.json()
                if isinstance(payload, dict) and "organic_keywords" in payload:
                    metrics["keywords"] = int(payload["organic_keywords"])
            except Exception as exc:  # noqa: BLE001
                log.warning("Ahrefs keyword JSON parsing failed for %s: %s", domain, exc)

        return metrics
