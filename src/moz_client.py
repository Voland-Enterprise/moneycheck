import base64
import logging
import time
from typing import Dict, Optional

import requests
from requests import Response

from .config import MozConfig


log = logging.getLogger(__name__)


class MozClient:
    def __init__(self, config: MozConfig):
        self.config = config
        token = f"{config.access_id}:{config.secret_key}".encode()
        self.auth_header = base64.b64encode(token).decode()

    def _request_with_retry(self, payload: Dict[str, object]) -> Optional[Response]:
        delay = self.config.delay_seconds
        headers = {"Authorization": f"Basic {self.auth_header}"}

        for attempt in range(self.config.max_retries + 1):
            try:
                response = requests.post(
                    self.config.base_url,
                    json=payload,
                    headers=headers,
                    timeout=15,
                )
                if response.status_code == 429 or response.status_code >= 500:
                    log.warning(
                        "Moz temporary error (status %s): %s", response.status_code, response.text
                    )
                    if attempt < self.config.max_retries:
                        time.sleep(delay)
                        delay *= self.config.backoff_factor
                        continue
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                log.warning("Moz request failed: %s", exc)
                if attempt < self.config.max_retries:
                    time.sleep(delay)
                    delay *= self.config.backoff_factor
        return None

    def get_metrics(self, domain: str) -> Dict[str, Optional[float]]:
        payload = {"targets": [domain]}
        metrics = {"da": None, "pa": None}

        response = self._request_with_retry(payload)
        time.sleep(self.config.delay_seconds)
        if response is None:
            return metrics

        try:
            data = response.json()
            if isinstance(data, dict):
                results = data.get("results") or []
                if results:
                    first = results[0]
                    if "domain_authority" in first:
                        metrics["da"] = float(first.get("domain_authority"))
                    if "page_authority" in first:
                        metrics["pa"] = float(first.get("page_authority"))
        except Exception as exc:  # noqa: BLE001
            log.warning("Moz JSON parsing failed for %s: %s", domain, exc)

        return metrics
