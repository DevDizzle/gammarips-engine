import logging, time, requests
from datetime import date, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential

class _RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls, self.period = max_calls, period
        self._ts = []

    def acquire(self):
        now = time.time()
        self._ts = [t for t in self._ts if now - t < self.period]
        if len(self._ts) >= self.max_calls:
            sleep_for = (self._ts[0] + self.period) - now
            if sleep_for > 0:
                time.sleep(sleep_for)
        self._ts.append(time.time())

class PolygonClient:
    BASE = "https://api.polygon.io"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("POLYGON_API_KEY is required")
        self.api_key = api_key
        self._rl = _RateLimiter(max_calls=5, period=60.0)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def _get(self, url: str, params: dict | None = None) -> dict:
        self._rl.acquire()
        params = dict(params or {})
        params["apiKey"] = self.api_key
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def _map_result(self, r: dict) -> dict:
        # This function is for options_chain and is not used by news_fetcher
        pass

    def fetch_options_chain(self, ticker: str, max_days: int = 90) -> list[dict]:
        # This function is for options_chain and is not used by news_fetcher
        pass

    def fetch_news(self, ticker: str | None = None, from_date: str | None = None, to_date: str | None = None, limit_per_page: int = 1000, paginate: bool = True, topics_str: str | None = None) -> list[dict]:
        """
        Fetch Benzinga news articles (paged).
        """
        url = f"{self.BASE}/benzinga/v1/news"
        params = {"limit": limit_per_page, "sort": "published.desc"}
        if ticker:
            params["tickers"] = ticker
        if from_date:
            params["published.gte"] = from_date
        if to_date:
            params["published.lte"] = to_date
        if topics_str:
            params["topics"] = topics_str
        out: list[dict] = []

        while True:
            j = self._get(url, params)
            out.extend(j.get("results") or [])
            if not paginate:
                break
            next_url = j.get("next_url")
            if not next_url:
                break
            url, params = next_url, {}
        return out