from sqlalchemy.orm import Session
from programm_database.models import User, Movie, Director, UserToMovie


class DatabaseManager:
  def __init__(self, db: Session):
    """
    Initialisiert den DatabaseManager mit einer Datenbank-Session.
    :param db: SQLAlchemy-Session
    """
    self.db = db

  def list_movies_for_user(self, user_id: int):
    """
    Listet alle Filme eines Nutzers basierend auf der user_id.
    """
    try:
      user_movies = (
        self.db.query(Movie.title, Movie.release_date, UserToMovie.rating)
        .join(UserToMovie, Movie.id == UserToMovie.movie_id)
        .filter(UserToMovie.user_id == user_id)
        .all()
      )

      if not user_movies:
        print(f"Keine Filme für Nutzer mit ID {user_id} gefunden.")
        return []

      for movie in user_movies:
        print(f"Film: {movie.title}, Erscheinungsjahr: {movie.release_date}, Bewertung: {movie.rating}")

      return user_movies

    except Exception as e:
      print(f"Fehler beim Abrufen der Filme für Nutzer {user_id}: {e}")
      return []

  def add_movie_for_user(self, user_id: int, movie_title: str, release_date: int, director_id: int, rating: float):
    """
    Fügt einen neuen Film für einen Nutzer hinzu.
    """
    try:
      existing_movie = self.db.query(Movie).filter(Movie.title == movie_title).first()

      if not existing_movie:
        new_movie = Movie(title=movie_title, release_date=release_date, director_id=director_id)
        self.db.add(new_movie)
        self.db.commit()
        self.db.refresh(new_movie)
        print(f"Neuer Film hinzugefügt: {new_movie.title} (ID: {new_movie.id})")
      else:
        new_movie = existing_movie
        print(f"Film existiert bereits in der Datenbank: {new_movie.title} (ID: {new_movie.id})")

      user_to_movie = UserToMovie(user_id=user_id, movie_id=new_movie.id, rating=rating)
      self.db.add(user_to_movie)
      self.db.commit()

      print(f"Film '{new_movie.title}' wurde dem Nutzer mit ID {user_id} hinzugefügt.")

    except Exception as e:
      print(f"Fehler beim Hinzufügen des Films für Nutzer {user_id}: {e}")
      self.db.rollback()

  def delete_movie_for_user(self, user_id: int, movie_id: int):
    """
    Löscht die Verbindung zwischen einem Nutzer und einem Film.
    Wenn kein anderer Nutzer mehr mit dem Film verbunden ist, wird der Film ebenfalls aus der Datenbank gelöscht.
    """
    try:
      user_to_movie_entry = (
        self.db.query(UserToMovie)
        .filter(UserToMovie.user_id == user_id, UserToMovie.movie_id == movie_id)
        .first()
      )

      if not user_to_movie_entry:
        print(f"Keine Verbindung zwischen Nutzer {user_id} und Film {movie_id} gefunden.")
        return False

      self.db.delete(user_to_movie_entry)
      self.db.commit()
      print(f"Verbindung zwischen Nutzer {user_id} und Film {movie_id} wurde gelöscht.")

      remaining_connections = (
        self.db.query(UserToMovie)
        .filter(UserToMovie.movie_id == movie_id)
        .count()
      )

      if remaining_connections == 0:
        movie = self.db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
          self.db.delete(movie)
          self.db.commit()
          print(f"Film mit ID {movie_id} wurde aus der Datenbank gelöscht.")

      return True

    except Exception as e:
      print(f"Fehler beim Löschen des Films mit ID {movie_id} für Nutzer {user_id}: {e}")
      self.db.rollback()
      return False

  def update_movie_rating(self, user_id: int, movie_id: int, new_rating: float):
    """
    Aktualisiert das Rating eines Films für einen bestimmten Nutzer in der Tabelle user_to_movie.
    """
    try:
      user_to_movie_entry = (
        self.db.query(UserToMovie)
        .filter(UserToMovie.user_id == user_id, UserToMovie.movie_id == movie_id)
        .first()
      )

      if not user_to_movie_entry:
        print(f"Keine Bewertung für Nutzer {user_id} und Film {movie_id} gefunden.")
        return False

      user_to_movie_entry.rating = new_rating
      self.db.commit()
      print(f"Das Rating für Nutzer {user_id} und Film {movie_id} wurde auf {new_rating} aktualisiert.")
      return True

    except Exception as e:
      print(f"Fehler beim Aktualisieren des Ratings für Nutzer {user_id} und Film {movie_id}: {e}")
      self.db.rollback()
      return False
