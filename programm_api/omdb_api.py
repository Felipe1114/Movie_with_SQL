import requests

class OMDbAPI:
    def __init__(self, api_key: str):
        """
        Initialisiert die OMDbAPI-Klasse mit einem API-Schlüssel.
        :param api_key: Dein API-Schlüssel für die OMDb API.
        """
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"

    def fetch_movie_data(self, title: str):
        """
        Ruft Filmdaten von der OMDb API basierend auf dem Titel ab.
        :param title: Der Titel des Films.
        :return: Ein Dictionary mit den Filmdaten oder None bei Fehlern.
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
