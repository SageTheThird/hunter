import os
import time
import json
import random
import requests
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)

CACHE_FILE = "data/webshare_proxies_cache.json"
API_URL = "https://proxy.webshare.io/api/v2/proxy/list/?page=1&page_size=20&mode=direct"


class ProxyManager:
    def __init__(self, api_key: str | None):
        """
        Initializes the ProxyManager.
        If no api_key is provided, it operates in a disabled state.
        """
        self.api_key = api_key
        self.proxies = []
        if self.api_key:
            # Ensure the cache directory exists
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            self.proxies = self._load_cached_proxies()
        else:
            log.info("ProxyManager initialized in disabled state (no API key found).")

    def _load_cached_proxies(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                # Cache is valid for 1 hour (3600 seconds)
                if time.time() - data.get("timestamp", 0) < 3600:
                    log.info("Using cached proxy list.")
                    return data["proxies"]

        return self._fetch_and_cache_proxies()

    def _fetch_and_cache_proxies(self):
        if not self.api_key:
            return []

        log.info("Fetching fresh proxy list from Webshare...")
        headers = {"Authorization": f"Token {self.api_key}"}
        try:
            res = requests.get(API_URL, headers=headers)
            res.raise_for_status()
            raw = res.json().get("results", [])

            proxies = [
                {
                    # This is the format Playwright's 'proxy' option prefers
                    "playwright_format": {
                        "server": f"http://{p['proxy_address']}:{p['port']}",
                        "username": p["username"],
                        "password": p["password"],
                    },
                    "location": f'{p["country_code"]} - {p.get("city_name", "N/A")}',
                }
                for p in raw
                if p.get("valid")
            ]

            with open(CACHE_FILE, "w") as f:
                json.dump({"timestamp": time.time(), "proxies": proxies}, f)
            log.info(f"Successfully fetched and cached {len(proxies)} valid proxies.")
            return proxies
        except requests.exceptions.RequestException as e:
            log.error(f"Failed to fetch proxies: {e}")
            return []

    def get_random_proxy(self) -> dict | None:
        if not self.proxies:
            return None
        return random.choice(self.proxies)
