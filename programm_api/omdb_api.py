import requests

class OMDbAPI:
    def __init__(self, api_key: str):
        """
        Initialice the OMDb-api-class with the api-key
        :param api_key: the api-key
        """
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"

    def fetch_movie_data(self, title: str):
        """
        calls movie data from the OMDb-api, based on movie titel.
        :param title: movie title
        :return: dictionary with movie datas || None if error
        """
        try:
            response = requests.get(self.base_url, params={"apikey": self.api_key, "t": title})
            response.raise_for_status()  # Hebt HTTP-Fehler hervor
            data = response.json()

            if data.get("Response") == "True":
                return data
            else:
                print(f"Fehler beim Abrufen der Daten: {data.get('Error')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
            return None
