from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from programm_database.models import Base
from programm_database.sqlite_database_manager import SQLiteDatabaseManager
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

# create data tables (only at start
Base.metadata.create_all(engine)

API_KEY = "70e6d1f0"

# create session
def init_service():
    """initialice database"""
    g.db = SessionLocal()
    g.db_manager = SQLiteDatabaseManager(g.db)

    # initialices MovieServie for putting movie datas into database
    g.movie_service = MovieService(g.db_manager, API_KEY)

@app.before_request
def create_session():
    """initialices Movie service"""
    init_service()

@app.teardown_request
def close_session(exception=None):
    """closes autmaticly the databaase connection after each database request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

    api = g.pop('movie_service', None)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)