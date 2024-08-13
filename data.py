import requests
import json
# Constants
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
FIXTURES_API_URL = "https://fantasy.premierleague.com/api/fixtures/"


class FPLDataFetcher:
    @staticmethod
    def fetch_data(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            print(response.status)
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None

    @staticmethod
    def fetch_fpl_data():

        with open('response.json', 'r') as file:
            return json.load(file)


        return FPLDataFetcher.fetch_data(FPL_API_URL)

    @staticmethod
    def fetch_fixtures():
        with open('fixtures.json', 'r') as file:
            return json.load(file)
        


        return FPLDataFetcher.fetch_data(FIXTURES_API_URL)
