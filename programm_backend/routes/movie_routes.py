# api/movie_routes.py - Flask-Routen für Filme
from flask import Blueprint, request, jsonify
from programm_database.database_manager import DatabaseManager
from sqlalchemy.orm import Session
from app import Session

movie_bp = Blueprint("movie_bp", __name__)

@movie_bp.route("/user/<int:user_id>/movies", methods=["GET"])
def get_movies_for_user(user_id):
  db = Session()
  db_manager = DatabaseManager(db)

  try:
    user = db_manager.get_user(user_id)

    # überprüfen, ob 'user' existiert
    if not user:
      return jsonify({"error": "User nicht gefunden"}), 404

    # dann alle filme ausgeben für user
    else:
      movies = db_manager.list_movies_for_user(user_id)

    movies = [
      {"title": movie[0], "release_year": movie[1], "rating": movie[2], "director_first_name": movie[3], "director_last_name": movie[4]} for movie in movies
    ]

    return jsonify(movies), 200

  except Exception as e:
    return jsonify({"error": str(e)}), 500
  finally:
    db.close()
