from flask import Blueprint, jsonify, g

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/user/<int:user_id>")
def get_user(user_id):
    try:
        user = g.db_manager.get_user(user_id)

        if not user:
            return jsonify({"error": f"Kein User mit der ID: {user_id}"}), 404

        return jsonify({"user_name": user.name, "user_id": user.id}), 200

    except Exception:
        return jsonify({"error": f"Fehler beim Zugriff auf User mit der ID: {user_id}"}), 404
