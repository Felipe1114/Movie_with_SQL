from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Verbindung zur SQLite-Datenbank herstellen -> einen "tunnel" erstellen
DATABASE_URL = "sqlite:///../programm_data/database/movie_database.db"
engine = create_engine(DATABASE_URL, echo=False)

# SessionFactory einrichten -> hiermit kann man mit der Datenbank arbeiten
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Funktion zum Erstellen einer neuen Session
def get_db():
    # db ist die session
    db = SessionLocal()
    try:
      # mit yield wird die funktion pausiert und nicht beendet
        yield db
    # egal ob ein fehler auftritt oder nicht, wird die datenbankvebindung am ende geschlossen.
    finally:
        db.close()
