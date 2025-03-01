from flask import Blueprint, jsonify, g

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/user/<int:user_id>", mehtod=["GET"])
def get_user(user_id):
    try:
        user = g.db_manager.get_user(user_id)

        if not user:
            return jsonify({"error": f"Kein User mit der ID: {user_id}"}), 404

        return jsonify({"user_name": user.name, "user_id": user.id}), 200

    except Exception:
        return jsonify({"error": f"Fehler beim Zugriff auf User mit der ID: {user_id}"}), 404

# TODO ist dieser code hier richtig?
@user_bp.route("/user/<str:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        existend_user = g.db_manager.get_user(user_id)

        if not existend_user:
            return jsonify({"error:": f"Kein User mit der ID: {user_id}"}), 404

        if existend_user:
            user_removed = g.db_manager.delete_user(user_id)

            if user_removed:
                return jsonify({"message": f"User mit der ID:{user_id} wurde entfernt"}), 200


    except Exception as e:
        return jsonify({"error:": f"Fehler: {e}"}), 500