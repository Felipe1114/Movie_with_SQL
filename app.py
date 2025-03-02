from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from programm_database.models import Base
from programm_database.database_manager import DatabaseManager
from programm_backend.movie_routes import movie_bp
from programm_backend.user_routes import user_bp
from programm_backend.main_route import main_bp
from programm_api.movie_service import MovieService

app = Flask(__name__)

app.register_blueprint(movie_bp)
app.register_blueprint(user_bp, url_prefix="/")
app.register_blueprint(main_bp)

DATABASE_URL = "sqlite:///./programm_data/database/movie_database.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Datenbanktabellen erstellen (nur einmal beim Start)
Base.metadata.create_all(engine)

API_KEY = "70e6d1f0"
# session mit 'g' bereitstellen
def init_service():
    # initialisiert die datenbank und ihren zugriff
    g.db = SessionLocal()
    g.db_manager = DatabaseManager(g.db)

    # initialisiert MovieService, damit die API daten in die Datenbank eingesetzt werden können
    g.movie_service = MovieService(g.db_manager, API_KEY)

@app.before_request
def create_session():
    init_service()

@app.teardown_request
def close_session(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

    api = g.pop('movie_service', None)



if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)