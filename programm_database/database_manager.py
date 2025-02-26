from quopri import ESCAPE

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from programm_database.models import User, Movie, Director, UserToMovie



class DatabaseManager:
  def __init__(self, db: Session):
    """
    Initialisiert den DatabaseManager mit einer Datenbank-Session.
    :param db: SQLAlchemy-Session
    """
    self.db = db

  def get_user_id(self, user_name: str):
    """
    gibt die user_id eines bestimmten users zurück
    """
    try:
      user_id = (
        self.db.query(User.name).
        filter(User.name == user_name).
        first()
      )

      if not user_id:
        print(f"keinen nutzer mit dem namen: {user_name} gefunden")

      return user_id

    except Exception:
      print("Fehler beim abrufen der user_id")


  def add_user(self, user_name: str):
    """
    fügt einen neuen user in die datenbank ein
    """
    try:
      existing_user = self.db.query(User.name).filter(User.name == user_name).first()

      if not existing_user:
        new_user = User(user_name=user_name)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user) # jetzt hat new_user auch eine id

        print(f"Neuer user hinzugefügt: name:{new_user.name}, id: {new_user.id}")

      else:
        new_user = existing_user
        print(f"Es existiert bereits ein User mit diesem Namen: name:{new_user.name}, id: {new_user.id}")

    except Exception:
      print("fehler beim einfügen des neuen users")
      self.db.rollback()


  def delete_user(self, user_id: int):
    """
    Entfernt einen user aus der datenbank und alle weiteren daten, die mit dem user in verbindung stehen
    """
    try:
      removable_user = self.db.query(User).filter(User.id == user_id).one()

      if removable_user:
        user_related_data = self.db.query(UserToMovie).filter(UserToMovie.user_id == user_id).all()

        for entry in user_related_data:
          self.db.delete(entry)

        self.db.commit()

        self.db.delete(removable_user)
        self.db.commit()

        print(f"User mit dem namen: {removable_user.name}; und der ID: {removable_user.id}; wurde, mit all seien verknüpften daten, gelöscht")

    except NoResultFound as e:
      print(f"User mit der ID: {user_id}, wurde nicht gefunden: {e}")
      self.db.rollback()

    except Exception as e:
      print(f"Fehler beim Löschen des Users: {e}")
      self.db.rollback()


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

      #TODO muss etwas geprintet werden?
      for movie in user_movies:
        print(f"Film: {movie.title}, Erscheinungsjahr: {movie.release_date}, Bewertung: {movie.rating}")

      return user_movies

    except Exception as e:
      print(f"Fehler beim Abrufen der Filme für Nutzer {user_id}: {e}")
      return []

  def add_movie_for_user(self, user_id: int, movie_title: str, release_date: int, director_first_name: str, director_last_name: str, rating: float):
    """
    Fügt einen neuen Film für einen Nutzer hinzu und verknüpft ihn mit allen verinkten tables
    """
    try:
      # abfrage, ob director bereits in datenbank existiert
      existing_director = self.db.query(Director).filter(Director.first_name == director_first_name, Director.last_name == director_last_name).one_or_none()

      # wenn der director noch nicht existiert
      if not existing_director:
        new_director = self.add_director(director_first_name, director_last_name)

      else:
        new_director = existing_director

      # abfrage, ob film bereits in datenbank existiert
      existing_movie = self.db.query(Movie).filter(Movie.title == movie_title).first()

      if not existing_movie:
        new_movie = Movie(title=movie_title, release_date=release_date, director_id=new_director.id)
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

  # TODO metode überprüfen
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

  # TODO metode überprüfen
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


  def add_director(self, director_first_name: str, director_last_name: str):
    """
    adds a new director to the database
    """
    try:
      existing_director = self.db.query(Director).filter(Director.first_name == director_first_name, Director.last_name == director_last_name).one_or_none()

      if not existing_director:
        new_director = Director(first_name=director_first_name, last_name=director_last_name)
        self.db.add(new_director)
        self.db.commit()
        self.db.refresh(new_director)

        print(f"Ein neuer director: {new_director.first_name} {new_director.last_name} (ID:{new_director.id}), wurde in die Datenbank hinzugefügt")
      else:
        new_director = existing_director
        print(f"Director: {new_director.first_name} {new_director.last_name}, ID: {new_director.id}, existiert bereits ")

      return new_director

    except Exception:
      print(f"Fehler beim hinzufügen des directors {director_first_name} {director_last_name}, in die datenbank.")


  def get_director(self, director_id: int):
    """
    gibt den director auf basis seiner ID zurück
    """
    try:
      existing_director = self.db.query(Director).filter(Director.id == director_id).one_or_none()

      if existing_director:
        return existing_director

      else:
        print(f"Es existiert kein Director mit der id: {director_id}")
        return None

    except Exception:
      print(f"Es gab einen Fehler beim zugriff auf die datenbank")


  def delete_director(self, director_id: int):
    """
    Entfernt einen director aus der Datenbank, auf basis seiner ID
    """
    try:
      existing_director = self.db.query(Director).filter(Director.id == director_id).one_or_none()


      if existing_director:
        connected_movies = self.db.query(Movie).filter(Movie.director_id == director_id).all()

        if connected_movies:
          for movie in connected_movies:

            # alle verbindungen zu 'movie'
            to_movie_connected_data = self.db.query(UserToMovie).filter(UserToMovie.movie_id == movie.id).all()

            # existieren verbindungen zu diesem film
            if to_movie_connected_data:

              # alle daten, die mit den zu löschenden filmen verbunden sind, löschen
              for data in to_movie_connected_data:
                self.db.delete(data)
                self.db.commit()

                print(f"die Zeile {data.user_id}, {data.movie_id}, wurde gelöscht")

          # alle film verbindungen wurden gelöscht, jetzt werden alle filme gelöscht
          for movie in connected_movies:
            self.db.delete(movie)
            self.db.commit()

            print(f"Der Film: {movie.title}, Director: {movie.director}, Rating: {movie.rating}, ID: {movie.id}, wurde gelöscht")


        else:
          print(f"Es existieren keine Filme mehr, mit dem director '{existing_director.first_name} {existing_director.last_name}'")

        # alle filme mit dem director wurden gelöscht, jetzt wird der director gelöscht
        self.db.delete(existing_director)
        self.db.commit()

        print(f"Der Director: '{existing_director.first_name} {existing_director.last_name}' ID: {existing_director.id}, wurde gelöscht")


      else:
        print(f"Es existiert kein director mit der ID: {director_id}")

    except Exception:
      print(f"Fehler beim löschen des Directors mit der ID: {director_id}")