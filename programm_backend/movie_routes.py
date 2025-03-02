from flask import Blueprint, jsonify, g, request, render_template, redirect, url_for
from werkzeug.exceptions import BadRequest

# Blueprint-Objekt für Movie-Routen
movie_bp = Blueprint("movie_bp", __name__)
@movie_bp.route("/user/<int:user_id>/movies", methods=["GET"])
def get_movies_for_user(user_id):
    try:
        # Zugriff auf den DatabaseManager
        db_manager = g.db_manager

        # Benutzer aus der Datenbank abrufen
        user = db_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "Benutzer nicht gefunden"}), 404

        movies = g.db_manager.list_movies_for_user(user_id)
        # Filme des Benutzers abrufe
        print([
          {"title": movie[0], "year": movie[1], "rating": movie[2] if movie[2] else None}
          for movie in movies
        ])
        # movies = [
        #     {"id": m.movie.id, "title": m.movie.title, "rating": float(m.rating) if m.rating else None}
        #     for m in user.movies
        # ]

        # Template rendern und Benutzer- sowie Filmdaten übergeben
        return render_template("user_template.html", user=user, movies=movies)
    except AttributeError as e:
      return jsonify({"error": f"AttributeError:{e}"}), 500

    except Exception as e:
        return jsonify({"error": f"Fehler beim Abrufen der Filme: {e}"}), 500


#2. Einen neuen Film für einen Nutzer hinzufügen. wenn der film dann hinzugefügt wurde,
# soll er auch gleich mit den anderen filmen angezeigt werden
@movie_bp.route("/user/<int:user_id>/movies", methods=["POST"])
def add_movie_for_user(user_id):
    try:
        print(f"in 'movie_routes, 36', user_id = {user_id}")
        # Prüfen, ob ein Titel übergeben wurde
        title = request.form.get("title")
        if not title:
            raise BadRequest("Filmtitel fehlt.")

        # Benutzer in der Datenbank überprüfen
        db_manager = g.db_manager
        print(f"in 'movie_routes, 44'; g.db_manager ist:{g.db_manager}")

        user = db_manager.get_user(user_id)
        print(f"{user}")
        if not user:
            return jsonify({"error": "Benutzer nicht gefunden"}), 404

        # Film zur Datenbank hinzufügen
        movie_service = g.movie_service
        new_movie = movie_service.add_movie_from_api(user_id, title)

        if not new_movie:
            return jsonify({"error": "Film konnte nicht hinzugefügt werden."}), 500

        # Erfolgreich: Weiterleitung zur aktualisierten Filmübersicht
        return redirect(url_for("movie_bp.get_movies_for_user", user_id=user_id))

    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Fehler beim Hinzufügen des Films: {e}"}), 500


# 3. Film-Bewertung aktualisieren
@movie_bp.route("/user/<int:user_id>/movies/<int:movie_id>", methods=["POST"])
def update_movie_rating(user_id, movie_id):
  try:
    if request.form.get('_method') == 'PATCH':

      new_rating = request.form.get("rating")

      if new_rating is None:
        return jsonify({"error": "Rating fehlt"}), 400

      success = g.db_manager.update_movie_rating(user_id, movie_id, new_rating)

      updated_movie = g.db_manager.get_movie_from_user(movie_id, user_id)
      if not success:
        return jsonify({"error": "Film oder User nicht gefunden"}), 404

      # wewnn film aktualisert, alle filme wieder anzeigen lassen
      return redirect(url_for("movie_bp.get_movies_for_user", user_id=user_id))

  except Exception as e:
    return jsonify({"error": str(e)}), 500




# 4. Film eines Nutzers löschen
@movie_bp.route("/user/<int:user_id>/delete_movies/<int:movie_id>", methods=["POST"])
def delete_movie_for_user(user_id, movie_id):
  try:
    if request.form.get('_method') == 'DELETE':

      success = g.db_manager.delete_movie_for_user(user_id, movie_id)

      if not success:
        return jsonify({"error": "Film oder User nicht gefunden"}), 404


      # wewnn film gelöscht, alle filme wieder anzeigen lassen
      return redirect(url_for("movie_bp.get_movies_for_user", user_id=user_id))

  except Exception as e:
    return jsonify({"error": str(e)}), 500

