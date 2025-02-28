from flask import Flask, g, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from programm_database.models import Base
from programm_database.database_manager import DatabaseManager
from programm_backend.movie_routes import movie_bp
from programm_backend.user_routes import user_bp


app = Flask(__name__)

app.register_blueprint(movie_bp, url_prefix="/api/movies")
app.register_blueprint(user_bp, url_prefix="/api/users")

DATABASE_URL = "sqlite:///../programm_data/database/movie_database.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Datenbanktabellen erstellen (nur einmal beim Start)
Base.metadata.create_all(engine)

# session mit 'g' bereitstellen
@app.before_request
def create_session():
    g.db = SessionLocal()
    g.db_manager = DatabaseManager(g.db)

@app.teardown_request
def close_session(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#

if __name__ == "__main__":
    app.run(debug=True)