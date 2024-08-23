import requests
# Constants
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
FIXTURES_API_URL = "https://fantasy.premierleague.com/api/fixtures/"
class FPLDataFetcher:
    @staticmethod
    def fetch_data(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None
    

    @staticmethod
    def fetch_fpl_data():
        return FPLDataFetcher.fetch_data(FPL_API_URL)

    @staticmethod
    def fetch_fixtures():
        return FPLDataFetcher.fetch_data(FIXTURES_API_URL)
