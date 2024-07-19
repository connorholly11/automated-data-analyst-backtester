import requests

class PolygonDataHandler:
    BASE_URL = "https://api.polygon.io/v2"

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.params = {"apiKey": self.api_key}

    def _make_request(self, endpoint, params=None):
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_aggs(self, symbol, multiplier, timespan, from_date, to_date, limit=50000):
        endpoint = f"aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {"adjusted": "true", "sort": "asc", "limit": limit}
        return self._make_request(endpoint, params)['results']

    def get_daily_open_close(self, symbol, date):
        endpoint = f"open-close/{symbol}/{date}"
        return self._make_request(endpoint)

    def get_previous_close(self, symbol):
        endpoint = f"aggs/ticker/{symbol}/prev"
        return self._make_request(endpoint)['results'][0]