from programm_database.database_manager import DatabaseManager
from programm_api.omdb_api import OMDbAPI
from programm_api.validate_omdb_data import DataValidator


class MovieDataImporter:
  def __init__(self, db_manager: DatabaseManager, omdb_api: OMDbAPI):
    """
    Initialisiert den MovieDataImporter mit einem DatabaseManager und einer OMDbAPI-Instanz.
    :param db_manager: Die Instanz des DatabaseManagers.
    :param omdb_api: Die Instanz der OMDbAPI-Klasse.
    """
    self.db_manager = db_manager
    self.omdb_api = omdb_api

  def import_movie(self, title: str, user_id: int):
    """
    Ruft Filmdaten von der API ab, validiert sie und fügt sie in die Datenbank ein.
    :param title: Der Titel des Films.
    :param user_id: Die ID des Nutzers, dem der Film hinzugefügt wird.
    """
    movie_data = self.omdb_api.fetch_movie_data(title)

    if not movie_data:
      print(f"Keine Daten für den Film '{title}' gefunden.")
      return

    # Validierung der Felder
    release_year = DataValidator.validate_release_year(movie_data.get("Year", ""))

    if not release_year:
      print(f"Erscheinungsjahr für '{title}' konnte nicht validiert werden.")
      return

    director_name = movie_data.get("Director", "Unknown")

    # Regisseur aufteilen in Vorname und Nachname (wenn möglich)
    director_first_name = director_name.split()[0] if director_name else "Unknown"
    director_last_name = " ".join(director_name.split()[1:]) if len(director_name.split()) > 1 else "Unknown"

    rating = DataValidator.validate_numeric_field(movie_data.get("imdbRating", 0), "IMDb Rating")

    # Film hinzufügen
    self.db_manager.add_movie_for_user(
      user_id=user_id,
      movie_title=movie_data.get("Title", "Unknown"),
      release_date=release_year,
      director_id=1,  # Beispielhaft; du könntest hier einen neuen Regisseur hinzufügen oder suchen
      rating=rating or 0.0,
    )
