from programm_database.base_classes.database_manager import DatabaseManager
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.orm import Session
from programm_database.models import User, Movie, Director, UserToMovie

class SQLiteDatabaseManager(DatabaseManager):
  def __init__(self, db: Session):
    """
    initialices DatabaseManager via argument
    """
    self.db = db

    print(f"DatabaseManager was initialiced as: {self.__class__.__name__}")

  def get_user(self, user_id: int):
    """
    Gets specific user from database by user_id
   
    :param user_id: id from specific user
    :return: user || None
    """
    try:
      existing_user = (self.db.query(User).
                       filter(User.id == user_id).
                       one())

      return existing_user

    except NoResultFound as e:
      print(f"No user with found with id: {user_id}: {e}")

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")

    except Exception:
      print(f"Error for request to user wiht id: {user_id}")


  def get_user_id(self, user_name: str):
    """
		gives back the id for specific user
		
		:arg user_name: name from user; str
		:return: user_id || None
    """
    try:
      user = (
        self.db.query(User).
        filter(User.name == user_name).
        first()
      )

      if not user:
        print(f"no user with name: {user_name} found")

      # gives back user.id, if user exists; else return None
      return user.id if user else None

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")

    except Exception:
      print("Error for request for user_id")


  def add_user(self, user_name: str):
    """
    Adds a new user to database.
    If user_name exist in database, new_user = existing_user
    
    :param user_name: name for new user
    :return: new_user || existing_user
    """
    try:
      existing_user = self.db.query(User.name).filter(User.name == user_name).first()

      if not existing_user:
        new_user = User(name=user_name)
        self.db.add(new_user)
        self.db.commit()
        
        # give new_user an ID
        self.db.refresh(new_user)

        print(f"New user added: name: {new_user.name}, id: {new_user.id}")
        
        return new_user

      else:
        new_user = existing_user
        print(f"A user with this name already exist: name:{new_user.name}, id: {new_user.id}")

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")
      self.db.rollback()
    
    except Exception:
      print("Error for adding new_user to database")
      self.db.rollback()

  def delete_user(self, user_id: int):
    """
    Deletes a user form database and all connected data
    """
    try:
      removable_user = self.db.query(User).filter(User.id == user_id).one()

      if removable_user:
        # deletes all data wich is connected to removable_user
        self.db.query(UserToMovie).filter(UserToMovie.user_id == user_id).delete()

        self.db.commit()

        self.db.delete(removable_user)
        self.db.commit()

        print(f"User with the name: {removable_user.name}; and the ID: {removable_user.id}; was deleted, with all other connected data")

        return True

      else:
        return False

    except NoResultFound as e:
      print(f"User with the id: {user_id}, was not found: {e}")
      self.db.rollback()

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")

    except Exception as e:
      print(f"Error by deleting user: {e}")
      self.db.rollback()

  def list_user(self):
    """
    Lists up all users
    
    :return: list of users
    """
    try:
      all_user = self.db.query(User).all()
      
      return all_user

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")

    except Exception:
      print("Error by listing users")

  def list_movies_for_user(self, user_id: int) -> tuple:
    """
		Lists up all movies form user, by its id
		
    movie-tuple architecture:
      (Movie_name: str, release_year: int, rating: float, director_first_name: str, director_last_name: str)
    """
    try:
      # is given as tuple and has to be packed up, in the html document
      user_movies = (
        self.db.query(Movie.title, Movie.release_date, UserToMovie.rating, Director.first_name, Director.last_name, Movie.id)
        .join(UserToMovie, Movie.id == UserToMovie.movie_id).join(Director, Movie.director_id == Director.id)
        .filter(UserToMovie.user_id == user_id)
        .all()
      )

      if not user_movies:
        print(f"No movie with id: {user_id} found.")
        return ()
        
      print("Movies found:")
      for index, movie in enumerate(user_movies):
        print(f"\t{index + 1}. Movietitle: {movie.title}, release_year: {movie.release_date}, rating: {movie.rating}")

      return user_movies

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")

    except Exception as e:
      print(f"Error for getting movies for user with id: {user_id}: {e}")
      return ()


  def add_movie_for_user(self, user_id: int, movie_title: str, release_date: int, director_first_name: str, director_last_name: str, rating: float):
    """
    adds a new movie to user and links it to all linked tables
    """
    try:
      # if no user exists with this id
      if not self.get_user(user_id):
        raise ValueError(f"User wiht id: {user_id} does not exist.")

      # does director exists in database?
      existing_director = self.db.query(Director).filter(Director.first_name == director_first_name, Director.last_name == director_last_name).one_or_none()

      # if director not exist
      if not existing_director:
        new_director = self.add_director(director_first_name, director_last_name)

        if not new_director:
          raise ValueError

      else:
        new_director = existing_director

      # does movie exist in database?
      existing_movie = self.db.query(Movie).filter(Movie.title == movie_title).first()

      if not existing_movie:
        new_movie = Movie(title=movie_title, release_date=release_date, director_id=new_director.id)
        self.db.add(new_movie)
        self.db.commit()
        self.db.refresh(new_movie)
        print(f"New movie added: {new_movie.title} (ID: {new_movie.id})")

      else:
        new_movie = existing_movie
        print(f"Movie already exists in database: {new_movie.title} (ID: {new_movie.id})")

      user_to_movie = UserToMovie(user_id=user_id, movie_id=new_movie.id, rating=rating)
      self.db.add(user_to_movie)
      self.db.commit()

      print(f"Movie '{new_movie.title}' was added to user with ID {user_id}")

    except ValueError as e:
      print(f"Director couldn´t be added: {e}")
      self.db.rollback()
    
    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")
      self.db.rollback()
      
    except Exception as e:
      print(f"Error for adding movie to user with id: {user_id}: {e}")
      self.db.rollback()

  def delete_movie_for_user(self, user_id: int, movie_id: int):
    """
    Deletes the connection from user to movie
    if no user is connected to the movie, the movie also will deleted from database
    """
    try:
      user_to_movie_entry = (
        self.db.query(UserToMovie)
        .filter(UserToMovie.user_id == user_id, UserToMovie.movie_id == movie_id)
        .first()
      )

      if not user_to_movie_entry:
        print(f"No conncetion to user with id: {user_id} and the movie with id: {movie_id} was found.")
        return False

      self.db.delete(user_to_movie_entry)
      self.db.commit()
      # hier könnte man den print noch mla genauer machen, in dem anch den use rund mvoie name hinschreibt
      print(f"Connection from user with id: {user_id} and movie with id: {movie_id} was deleted.")

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
          print(f"Movie with id: {movie_id} was deleted from database.")

      return True

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")
      self.db.rollback()
    
    except Exception as e:
      print(f"Error for deleting movie wiht id: {movie_id} for user with id: {user_id}: {e}")
      self.db.rollback()
      return False

  def update_movie_rating(self, user_id: int, movie_id: int, new_rating: float):
    """
    update rating of a movie for a specific user
    """
    try:
      user_to_movie_entry = (
        self.db.query(UserToMovie)
        .filter(UserToMovie.user_id == user_id, UserToMovie.movie_id == movie_id)
        .first()
      )

      if not user_to_movie_entry:
        print(f"No connection from user with id: {user_id} and movie wiht id: {movie_id} was found.")
        return False

      user_to_movie_entry.rating = new_rating
      self.db.commit()
      print(f"Rating from user with id: {user_id} for movie with id: {movie_id} was updated to: {new_rating}.")
      return True

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")
      self.db.rollback()
    
    except Exception as e:
      print(f"Error for updating rating for user wiht id: {user_id} and movie with id: {movie_id}: {e}")
      self.db.rollback()
      return False


  def get_movie_from_user(self, movie_id, user_id):
    """
    gives back a movie, with specific rating, user and the user_id
    """
    try:
      existing_movie = self.db.query(Movie.title, UserToMovie.rating).join(UserToMovie, Movie.id == UserToMovie.movie_id).join(User, UserToMovie.user_id == User.id).filter(Movie.id == movie_id, User.id == user_id).first()

      if not existing_movie:
        print(f"No movie with this id: {user_id}")

      return existing_movie

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")

    except Exception:
      print("Error with connection to movies")
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

        print(f"New director: {new_director.first_name} {new_director.last_name} (ID:{new_director.id}), was added to database")
      else:
        new_director = existing_director
        print(f"Director: {new_director.first_name} {new_director.last_name}, ID: {new_director.id}, already exists")

      return new_director

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")
      self.db.rollback()

    except Exception:
      print(f"Error for adding director: {director_first_name} {director_last_name} to database")
      self.db.rollback()

  def get_director(self, director_id: int):
    """
    gives back a director on base of his id
    """
    try:
      existing_director = self.db.query(Director).filter(Director.id == director_id).one_or_none()

      if existing_director:
        return existing_director

      else:
        print(f"No director with id: {director_id}")
        return None

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")
      self.db.rollback()

    except Exception:
      print(f"DatabaseError")
      self.db.rollback()

  def list_up_directors(self):
    """
    Lists up all directors form database
    """
    try:
      directors = self.db.query(Director).all()

      if not directors:
        print(f"No directors in database")
        return

      else:
        return directors

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")
      self.db.rollback()

    except Exception:
      print("Error for request to directors")
      self.db.rollback()

  def delete_director(self, director_id: int):
    """
		deletes a director on base of his id
    """
    try:
      existing_director = self.db.query(Director).filter(Director.id == director_id).one_or_none()

      if not existing_director:
        print(f"No director with id: {director_id}")

        return

      connected_movies = self.db.query(Movie).filter(Movie.director_id == director_id).all()

      if not connected_movies:
        print(f"No movie with director: '{existing_director.first_name} {existing_director.last_name}'")

        return

      else:
        for movie in connected_movies:
          # deletes all connections to movie
          self.db.query(UserToMovie).filter(UserToMovie.movie_id == movie.id).delete()

          print(f"All connections to movie: {movie.title}, deleted")

          # all movie connections deleted; now all movies will be deleted
          self.db.delete(movie)

          print(f"The movie: {movie.title}, director: {existing_director.first_name, existing_director.last_name}, Rating: {movie.rating}, ID: {movie.id}, was deleted")

        # all movies was deleted, no the director will be deleted
        self.db.delete(existing_director)

        print(f"The Director: '{existing_director.first_name} {existing_director.last_name}' ID: {existing_director.id}, was deleted")

        # all changes commit to database
        self.db.commit()

    except SQLAlchemyError as e:
      print(f"DatabaseError: {e}")

    except Exception as e:

      print(f"Error by deleting director with id: {director_id}: {e}")
      self.db.rollback()