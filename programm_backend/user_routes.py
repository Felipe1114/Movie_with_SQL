from flask import Blueprint, jsonify, g, request, render_template, redirect, url_for
from sqlalchemy.exc import SQLAlchemyError
user_bp = Blueprint("user_bp", __name__)

# 1. indey-side: list all users
@user_bp.route("/", methods=["GET"])
def list_users():
	try:
		users = g.db_manager.list_user()
		user_list = [{"user_id": user.id, "user_name": user.name} for user in users]
		
		return render_template("index_template.html", users=user_list)

	except Exception as e:
		return jsonify({"error": f"Error with listing users{e}"}), 500


# 2. create new user
@user_bp.route("/", methods=["POST"])
def create_user():
	try:
		user_name = request.form.get("name")
		print(f"given user_name: {user_name}")
		
		if not user_name:
			return jsonify({"error": "user_name missing"}), 400
		
		new_user = g.db_manager.add_user(user_name)
		if not new_user:
			raise SQLAlchemyError
		
		return jsonify({"message": "User created", "user_id": new_user.id}), 201

	except SQLAlchemyError as e:
		return jsonify({"error": f"Error with adding user to database: {e}"}), 501

	except Exception as e:
		return jsonify({"error": f"Error with creating user: {e}"}), 500


# 3. delete user: int for user_id
@user_bp.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
	try:
		existing_user = g.db_manager.get_user(user_id)
		
		if not existing_user:
			return jsonify({"error": f"No user with id: {user_id}"}), 404
		
		g.db_manager.delete_user(user_id)
		
		return jsonify({"message": f"User wiht id: {user_id} was deleted"}), 200

	except Exception as e:
		return jsonify({"error": f"Error for deleting user: {e}"}), 500


@user_bp.route("/user", methods=["GET"])
def loggin():
	try:
		# Get user_id from query
		user_id = request.args.get("user_id", type=int)
		print(f"in 'loggin,76' user_id = {user_id}")
		
		if not user_id:
			return jsonify({"error": "No user-id given"}), 400

		# get user from database
		user = g.db_manager.get_user(user_id)
		print(f"In 'loggin,82'; user is: {user.name, user.id}")
		
		if not user:
				return jsonify({"error": "user not found"}), 404
		
		# render template and give user
		# redirect to route 'get_movies_for_user'
		return redirect(url_for("movie_bp.get_movies_for_user", user_id=user_id))


	except Exception as e:
		return jsonify({"error": f"Error with loading of user-side: {e}"}), 500



@user_bp.route("/user/logout", methods=["GET"])
def loggout():
	return redirect(url_for("main_route.index"))
