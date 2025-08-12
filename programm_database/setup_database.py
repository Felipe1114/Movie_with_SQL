from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from programm_database.models import Base, User, Movie, Director, UserToMovie

# create connection to SQLite-database wiht relative path
DATABASE_URL = "sqlite:///../programm_data/database/movie_database.db"
engine = create_engine(DATABASE_URL, echo=True)

# create tables
Base.metadata.create_all(engine)
print("Datenbank erfolgreich eingerichtet!")

# initialice SessionFactory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create new Session and test it funktions
def init_db():
    session = SessionLocal()
    try:

        # add new director
        director = Director(first_name="Steven", last_name="Spielberg")
        session.add(director)

        # add a movie
        movie = Movie(title="Jurassic Park", release_date=1993, director=director)
        session.add(movie)
        session.commit()

        print(f"check, that movie.id is not 'None': movie.id: {movie.id}")
      
        # add a user
        user = User(name="Alice")
        session.add(user)
        session.commit()

        print(f"Check, that user.id is not 'None': user.id: {user.id}")
        
        # add connection between user and movie
        user_to_movie = UserToMovie(user_id=user.id, movie_id=movie.id, rating=9.5)
        session.add(user_to_movie)
        session.commit()

        print(f"Check that all ForegnKeys connected correctly: user_id: {user_to_movie.user_id} movie_id: {user_to_movie.movie_id}")

        # save changes
        session.commit()
    except Exception as e:
        print(f"Error with initialicing database: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
