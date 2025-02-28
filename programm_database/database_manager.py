from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session
from programm_database.models import User, Movie, Director, UserToMovie


#  wenn zeit, dann self.db.query() in extra funktion modularisieren -> eigene class dafür bauen?
#  z.b: def get_user_by_name(self, user_name: str): -> so aufbauen, dass der rodner auch modular ist
#     return self.db.query(User).filter(User.name == user_name).first()

class DatabaseManager:
  def __init__(self, db: Session):
    """
    Initialisiert den DatabaseManager mit einer Datenbank-Session.
    :param db: SQLAlchemy-Session
    """
    self.db = db

    print(f"DatabaseManager wurde als {self.__class__.__name__} instanziert")

  def get_user(self, user_id: int):
    try:
      existing_user = self.db.query(User).filter(User.id == user_id).one()

      return existing_user

    except NoResultFound as e:
      print(f"Kein User mit der ID: {user_id} gefunden: {e}")

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception:
      print(f"Fehler beim zugriff auf User mit der ID: {user_id}")


  def get_user_id(self, user_name: str):
    """
    gibt die user_id eines bestimmten users zurück
    """
    try:
      user = (
        self.db.query(User).
        filter(User.name == user_name).
        first()
      )

      if not user:
        print(f"keinen nutzer mit dem namen: {user_name} gefunden")

      # gibt user.id zurück, falls user existiert. Ansonsten wird None returned
      return user.id if user else None

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception:
      print("Fehler beim abrufen der user_id")


  def add_user(self, user_name: str):
    """
    fügt einen neuen user in die datenbank ein
    """
    try:
      existing_user = self.db.query(User.name).filter(User.name == user_name).first()

      if not existing_user:
        new_user = User(name=user_name)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user) # jetzt hat new_user auch eine id

        print(f"Neuer user hinzugefügt: name:{new_user.name}, id: {new_user.id}")

      else:
        new_user = existing_user
        print(f"Es existiert bereits ein User mit diesem Namen: name:{new_user.name}, id: {new_user.id}")

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

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
        # löscht alle verbundenen daten zu 'user' aus der datenbank
        self.db.query(UserToMovie).filter(UserToMovie.user_id == user_id).delete()

        self.db.commit()

        self.db.delete(removable_user)
        self.db.commit()

        print(f"User mit dem namen: {removable_user.name}; und der ID: {removable_user.id}; wurde, mit all seien verknüpften daten, gelöscht")

    except NoResultFound as e:
      print(f"User mit der ID: {user_id}, wurde nicht gefunden: {e}")
      self.db.rollback()

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception as e:
      print(f"Fehler beim Löschen des Users: {e}")
      self.db.rollback()


  def list_user(self):
    try:
      all_user = self.db.query(User).all()
      return all_user

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception:
      print("Fehler beim auflisten der User")


  def list_movies_for_user(self, user_id: int) -> tuple:
    """
    Listet alle Filme eines Nutzers basierend auf der user_id.
    tuple aufbau:
      (Movie_name: str, release_year: int, rating: float, director_first_name: str, director_last_name: str)
    """
    try:
      user_movies = (
        self.db.query(Movie.title, Movie.release_date, UserToMovie.rating, Director.first_name, Director.last_name)
        .join(UserToMovie, Movie.id == UserToMovie.movie_id).join(Director, Movie.director_id == Director.id)
        .filter(UserToMovie.user_id == user_id)
        .all()
      )

      if not user_movies:
        print(f"Keine Filme für Nutzer mit ID {user_id} gefunden.")
        return []

      for index, movie in enumerate(user_movies):
        print("Folgende Filme wurden gefunden:")
        print(f"\t{index + 1}. Film: {movie.title}, Erscheinungsjahr: {movie.release_date}, Bewertung: {movie.rating}")

      return user_movies

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception as e:
      print(f"Fehler beim Abrufen der Filme für Nutzer {user_id}: {e}")
      return []


  def add_movie_for_user(self, user_id: int, movie_title: str, release_date: int, director_first_name: str, director_last_name: str, rating: float):
    """
    Fügt einen neuen Film für einen Nutzer hinzu und verknüpft ihn mit allen verinkten tables
    """
    try:
      # wenn kein User mit der user_id vorhanden ist
      if not self.get_user(user_id):
        raise ValueError(f"User mit ID {user_id} existiert nicht.")

      # abfrage, ob director bereits in datenbank existiert
      existing_director = self.db.query(Director).filter(Director.first_name == director_first_name, Director.last_name == director_last_name).one_or_none()

      # wenn der director noch nicht existiert
      if not existing_director:
        new_director = self.add_director(director_first_name, director_last_name)

        if not new_director:
          raise ValueError

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

    except ValueError as e:
      print(f"Director konnte nicht hinzugefügt werden: {e}")

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

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
      # hier könnte man den print noch mla genauer machen, in dem anch den use rund mvoie name hinschreibt
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

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

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
        print(f"Keine verbindung von Nutzer {user_id} und Film {movie_id} gefunden.")
        return False

      user_to_movie_entry.rating = new_rating
      self.db.commit()
      print(f"Das Rating für Nutzer {user_id} und Film {movie_id} wurde auf {new_rating} aktualisiert.")
      return True

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception as e:
      print(f"Fehler beim Aktualisieren des Ratings für Nutzer {user_id} und Film {movie_id}: {e}")
      self.db.rollback()
      return False


  def get_movie_from_user(self, movie_id, user_id):
    """
    gibt einen Film zurück, mit dem spezifischen Rating des Users mit der ID: user_id
    """
    try:
      existing_movie = self.db.query(Movie.title, UserToMovie.rating).join(UserToMovie, Movie.id == UserToMovie.movie_id).join(User, UserToMovie.user_id == User.id).filter(Movie.id == movie_id, User.id == user_id).first()

      if not existing_movie:
        print(f"Es existiert kein Film mit dieser ID: {user_id}")

      return existing_movie

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception:
      print("Fehler beim zugriff auf Filme")
      self.db.rollback()

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

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception:
      print(f"Fehler beim hinzufügen des directors {director_first_name} {director_last_name}, in die datenbank.")
      self.db.rollback()

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

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception:
      print(f"Es gab einen Fehler beim zugriff auf die datenbank")
      self.db.rollback()

  def list_up_directors(self):
    try:
      directors = self.db.query(Director).all()

      if not directors:
        print(f"Keine Directoren in der Datenbank")
        return

      else:
        return directors

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception:
      print("Fehler beim zugriff auf Directoren")
      self.db.rollback()

  def delete_director(self, director_id: int):
    """
    Entfernt einen director aus der Datenbank, auf basis seiner ID
    """
    try:
      existing_director = self.db.query(Director).filter(Director.id == director_id).one_or_none()

      if not existing_director:
        print(f"Es gibt keinen director mit dieser ID: {director_id}")

        return

      connected_movies = self.db.query(Movie).filter(Movie.director_id == director_id).all()

      if not connected_movies:
        print(f"Es existieren keine Filme mehr, mit dem director '{existing_director.first_name} {existing_director.last_name}'")

        return

      else:
        for movie in connected_movies:
          #lösche alle verbindungen zu einem film
          self.db.query(UserToMovie).filter(UserToMovie.movie_id == movie.id).delete()

          print(f"Alle verbindungen zu {movie.title}, wurden gelöscht")

          # alle film verbindungen wurden gelöscht, jetzt werden alle filme gelöscht
          self.db.delete(movie)

          print(f"Der Film: {movie.title}, Director: {existing_director.first_name, existing_director.last_name}, Rating: {movie.rating}, ID: {movie.id}, wurde gelöscht")

        # alle filme mit dem director wurden gelöscht, jetzt wird der director gelöscht
        self.db.delete(existing_director)

        print(f"Der Director: '{existing_director.first_name} {existing_director.last_name}' ID: {existing_director.id}, wurde gelöscht")

        # alle änderungen auf die datenbank übertragen
        self.db.commit()

    except SQLAlchemyError as e:
      print(f"Datenbankfehler: {e}")

    except Exception as e:

      print(f"Fehler beim Löschen des Directors mit der ID: {director_id}: {e}")

      self.db.rollback()