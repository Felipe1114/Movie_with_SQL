from flask import Blueprint, jsonify, g, request
from werkzeug.exceptions import BadRequest
from flask import UnsupportedMediaType

from programm_api.movie_service import MovieService
# Blueprint-Objekt für Movie-Routen
movie_bp = Blueprint("movie_bp", __name__)


# 1. Alle Filme eines Nutzers abrufen
@movie_bp.route("/user/<int:user_id>/movies", methods=["GET"])
def get_movies_for_user(user_id):
  db_manager = g.db_manager
  user = db_manager.get_user(user_id)

  if not user:
    return jsonify({"error": "User nicht gefunden"}), 404

  movies = [
    {"title": m.movie.title, "rating": float(m.rating) if m.rating else None}
    for m in user.movies
  ]

  return jsonify(movies), 200


#2. Einen neuen Film für einen Nutzer hinzufügen
# TODO ist movie_service richtig implementiert?
@movie_bp.route("/user/<int:user_id>/movies", methods=["POST"])
def add_movie_for_user(user_id):
    """
    Fügt einen neuen Film für einen Nutzer hinzu. Ruft Daten von der OMDb API ab.
    """
    try:
      # erhält daten aus dem HTML dokument
      movie_service = g.movie_service
      data = request.get_json()
      title = data.get("title")

      # wenn kein Titel vorhanden
      if not title:
          return jsonify({"error": "Der Titel des Films fehlt."}), 400

      # Film über den MovieService hinzufügen
      result = movie_service.add_movie_from_api(user_id=user_id, movie_title=title)

      if "error" in result:
          return jsonify(result), 400

      return jsonify(result), 201

    except BadRequest as e:
      print(f"Fehlerhafter Respond: {e}")

    except Exception:
      print(f"Fehler beim hinzufügen eines films in 'add_movie_for_user'")

# alter code
"""@movie_bp.route("/user/<int:user_id>/movies", methods=["POST"])
def add_movie_for_user(user_id):
  data = request.get_json()
  title = data.get("title")
  release_date = data.get("release_date")
  director_first_name = data.get("director_first_name")
  director_last_name = data.get("director_last_name")
  rating = data.get("rating")

  if not all([title, release_date, director_first_name, director_last_name]):
    return jsonify({"error": "Fehlende Felder"}), 400

  try:
    g.db_manager.add_movie_for_user(
      user_id, title, release_date, director_first_name, director_last_name, rating
    )
    return jsonify({"message": f"Film '{title}' hinzugefügt."}), 201

  except Exception as e:
    return jsonify({"error": str(e)}), 500"""


# 3. Film-Bewertung aktualisieren
@movie_bp.route("/user/<int:user_id>/movies/<int:movie_id>", methods=["PATCH"])
def update_movie_rating(user_id, movie_id):
  data = request.get_json()
  new_rating = data.get("rating")

  if new_rating is None:
    return jsonify({"error": "Rating fehlt"}), 400

  success = g.db_manager.update_movie_rating(user_id, movie_id, new_rating)

  updated_movie = g.db_manager.get_movie_from_user(movie_id, user_id)
  if not success:
    return jsonify({"error": "Film oder User nicht gefunden"}), 404

  return jsonify({"message": f"Bewertung aktualisiert"}), 200
  # warscheinlich ist hier ein fehler drin
  # return jsonify({"message": f"Bewertung für Film: {updated_movie.title} aktualisiert"}), 200



# 📌 4. Film eines Nutzers löschen
@movie_bp.route("/user/<int:user_id>/movies/<int:movie_id>", methods=["DELETE"])
def delete_movie_for_user(user_id, movie_id):
  try:
    success = g.db_manager.delete_movie_for_user(user_id, movie_id)

    if not success:
      return jsonify({"error": "Film oder User nicht gefunden"}), 404

    return jsonify({"message": f"Film mit ID {movie_id} wurde gelöscht."}), 200

  except Exception as e:
    return jsonify({"error": str(e)}), 500