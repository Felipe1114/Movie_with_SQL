from flask import Blueprint, jsonify, g, request, render_template, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
user_bp = Blueprint("user_bp", __name__)

# 1. Index-Seite: Alle User auflisten
@user_bp.route("/", methods=["GET"])
def list_users():
    try:
        users = g.db_manager.list_user()
        user_list = [{"user_id": user.id, "user_name": user.name} for user in users]

        return render_template("index_template.html", users=user_list)


    except Exception as e:
        return jsonify({"error": f"Fehler beim Abrufen der Benutzer: {e}"}), 500

# 2. Neuen User erstellen
@user_bp.route("/", methods=["POST"])
def create_user():
    try:
        user_name = request.form.get("name")
        print(f"Empfangener Benutzername: {user_name}")

        if not user_name:
            return jsonify({"error": "Benutzername fehlt"}), 400

        new_user = g.db_manager.add_user(user_name)
        if not new_user:
          raise SQLAlchemyError

        return jsonify({"message": "User erstellt", "user_id": new_user.id}), 201

    except SQLAlchemyError as e:
      return jsonify({"error": f"Fehler beim hinzufügen des Users in die Datenbank: {e}"}), 501

    except Exception as e:
        return jsonify({"error": f"Fehler beim Erstellen des Users: {e}"}), 500


# 4. User löschen (Korrektur: int statt str bei user_id)
@user_bp.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        existing_user = g.db_manager.get_user(user_id)

        if not existing_user:
            return jsonify({"error": f"Kein User mit der ID: {user_id}"}), 404

        g.db_manager.delete_user(user_id)

        return jsonify({"message": f"User mit der ID {user_id} wurde entfernt"}), 200

    except Exception as e:
        return jsonify({"error": f"Fehler beim Löschen des Benutzers: {e}"}), 500


@user_bp.route("/user", methods=["GET"])
def loggin():
    try:
        # Hole die user_id aus den Query-Parametern
        user_id = request.args.get("user_id", type=int)
        print(f"in 'loggin,76' user_id = {user_id}")
        if not user_id:
            return jsonify({"error": "Keine Benutzer-ID angegeben"}), 400

        # Hole den Benutzer aus der Datenbank
        user = g.db_manager.get_user(user_id)
        print(f"In 'loggin,82'; nutzer ist: {user.name, user.id}")
        if not user:
            return jsonify({"error": "Benutzer nicht gefunden"}), 404

        # Rendere das Template und übergebe den Benutzer
        # hie rmuss zu der route get_moives_for_user redirected werden
        return redirect(url_for("movie_bp.get_movies_for_user", user_id=user_id))


    except Exception as e:
        return jsonify({"error": f"Fehler beim Laden der Benutzerseite: {e}"}), 500



@user_bp.route("/user/logout", methods=["GET"])
def loggout():
    return redirect(url_for("main_route.index"))
