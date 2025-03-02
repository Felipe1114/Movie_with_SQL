from programm_database.database_manager import DatabaseManager
from programm_api.omdb_api import OMDbAPI
from programm_api.validate_omdb_data import DataValidator


class MovieService:
  def __init__(self, db_manager: DatabaseManager, api_key: str):
    """
    Initialisiert den MovieService mit einem DatabaseManager und einem OMDbAPI-Client.
    :param db_manager: Instanz von DatabaseManager.
    :param api_key: API-Schlüssel für die OMDb API.
    """
    self.db_manager = db_manager
    self.omdb_api = OMDbAPI(api_key)

  def add_movie_from_api(self, user_id: int, movie_title: str):
    """
    Fügt einen Film aus der OMDb API für einen bestimmten Nutzer hinzu.
    """
    # Schritt 1: Filmdaten von der OMDb API abrufen
    movie_data = self.omdb_api.fetch_movie_data(movie_title)

    if not movie_data:
      return {"error": f"Filmdaten für '{movie_title}' konnten nicht abgerufen werden."}

    # Schritt 2: Daten validieren
    release_year = DataValidator.validate_release_year(movie_data.get("Year", ""))
    rating = DataValidator.validate_numeric_field(movie_data.get("imdbRating", ""), "IMDB Bewertung")

    director_name = movie_data.get("Director", "")
    if not director_name or director_name == "N/A":
      return {"error": f"Regisseur-Daten für '{movie_title}' fehlen."}

    # Annahme: Der Regisseur-Name ist im Format "Vorname Nachname"
    director_first_name, director_last_name = (director_name.split(" ", 1) + [""])[:2]

    # Schritt 3: Film in die Datenbank einfügen
    try:
      self.db_manager.add_movie_for_user(
        user_id=user_id,
        movie_title=movie_title,
        release_date=release_year,
        director_first_name=director_first_name,
        director_last_name=director_last_name,
        rating=rating,
      )
      return {"message": f"Film '{movie_title}' wurde erfolgreich hinzugefügt."}

    except Exception as e:
      return {"error": f"Fehler beim Hinzufügen des Films '{movie_title}': {e}"}
