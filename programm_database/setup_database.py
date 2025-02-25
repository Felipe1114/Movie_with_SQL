from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from programm_database.models import Base, User, Movie, Director, UserToMovie



# Sicherstellen, dass das Verzeichnis existiert
#os.makedirs("../programm_data/database", exist_ok=True)

# Verbindung zur SQLite-Datenbank herstellen (relativer Pfad)
DATABASE_URL = "sqlite:///../programm_data/database/movie_database.db"
engine = create_engine(DATABASE_URL, echo=True)

# Tabellen erstellen
Base.metadata.create_all(engine)
print("Datenbank erfolgreich eingerichtet!")

# 3. SessionFactory einrichten
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Testen: Eine neue Session erstellen
def init_db():
    session = SessionLocal()
    try:

        # Einen Regisseur hinzufügen
        director = Director(first_name="Steven", last_name="Spielberg")
        session.add(director)

        # Einen Film hinzufügen
        movie = Movie(title="Jurassic Park", release_date=1993, director=director)
        session.add(movie)
        session.commit()

        print(f"Überprüfung das movie.id nicht 'None' ist: movie.id: {movie.id}")

        # Einen Benutzer hinzufügen
        user = User(name="Alice")
        session.add(user)
        session.commit()

        print(f"Überprüfung das user.id nicht 'None' ist: user.id: {user.id}")

        # Beziehung zwischen Benutzer und Film hinzufügen
        user_to_movie = UserToMovie(user_id=user.id, movie_id=movie.id, rating=9.5)
        session.add(user_to_movie)
        session.commit()

        print(f"Überprüfung das ForeignKeys korrekt verbunden wurden: user_id: {user_to_movie.user_id} movie_id: {user_to_movie.movie_id}")


        # Änderungen speichern
        session.commit()
    except Exception as e:
        print("Fehler beim Initialisieren der Datenbank:", e)
        session.rollback()
    finally:
        session.close()

# Initialisierung der Datenbank aufrufen
if __name__ == "__main__":
    init_db()
