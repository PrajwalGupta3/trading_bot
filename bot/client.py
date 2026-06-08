"""Thin Binance Futures Testnet (USDT-M) REST client.

Uses direct signed REST calls via `requests` so there are no heavy
dependencies. Every request, response, and error is logged.
"""

import hashlib
import hmac
import time
from urllib.parse import urlencode

import requests

from .logging_config import setup_logger

logger = setup_logger()

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""


class BinanceClient:
    """Minimal signed client for the Binance Futures Testnet."""

    def __init__(self, api_key: str, api_secret: str, base_url: str = TESTNET_BASE_URL):
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required.")
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: dict) -> str:
        query = urlencode(params)
        return hmac.new(
            self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def _signed_request(self, method: str, path: str, params: dict) -> dict:
        params = dict(params)
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = 5000
        params["signature"] = self._sign(params)

        url = f"{self.base_url}{path}"
        logger.info("API request: %s %s params=%s", method, path, _redact(params))

        try:
            response = self.session.request(method, url, params=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            logger.error("Network error on %s %s: %s", method, path, exc)
            raise BinanceAPIError(f"Network error: {exc}") from exc

        try:
            data = response.json()
        except ValueError:
            logger.error("Non-JSON response (%s): %s", response.status_code, response.text)
            raise BinanceAPIError(f"Unexpected response: {response.text}")

        if response.status_code != 200:
            logger.error("API error (%s): %s", response.status_code, data)
            msg = data.get("msg", str(data)) if isinstance(data, dict) else str(data)
            raise BinanceAPIError(f"Binance API error {response.status_code}: {msg}")

        logger.info("API response: %s", data)
        return data

    def place_order(self, params: dict) -> dict:
        """Send a new order to /fapi/v1/order."""
        return self._signed_request("POST", "/fapi/v1/order", params)

    def get_server_time(self) -> dict:
        """Public endpoint, useful as a connectivity check."""
        url = f"{self.base_url}/fapi/v1/time"
        logger.info("API request: GET /fapi/v1/time")
        response = self.session.get(url, timeout=10)
        data = response.json()
        logger.info("API response: %s", data)
        return data


def _redact(params: dict) -> dict:
    """Hide the signature in logs."""
    safe = dict(params)
    if "signature" in safe:
        safe["signature"] = "***"
    return safe
