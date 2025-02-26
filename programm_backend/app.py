from flask import Flask, render_template, request, redirect, url_for
from programm_database.connection_database import get_db
from programm_database.database_manager import DatabaseManager
from programm_api.omdb_api import OMDbAPI
from programm_api.validate_omdb_data import DataValidator

# Flask-App initialisieren
app = Flask(__name__)

# OMDb API-Schlüssel (ersetze durch deinen eigenen Schlüssel)
OMDB_API_KEY = "http://www.omdbapi.com/?i=tt3896198&apikey=70e6d1f0"
omdb_api = OMDbAPI(api_key=OMDB_API_KEY)


@app.route("/")
def index():
    """
    Startseite: Nutzer auswählen oder hinzufügen.
    """
    with next(get_db()) as db:
        db_manager = DatabaseManager(db)
        #TODO richtige user abfrage einbauen
        users = db.query(DatabaseManager.User).all()  # Alle Nutzer abrufen

    return render_template("index.html", users=users)


@app.route("/add_user", methods=["POST"])
def add_user():
    """
    Neuen Nutzer hinzufügen.
    """
    username = request.form.get("username")
    if username:
        with next(get_db()) as db:
            db_manager = DatabaseManager(db)
            #TODO auch hier richtige user abfrage einbauen
            new_user = DatabaseManager.User(name=username)
            db.add(new_user)
            db.commit()
    return redirect(url_for("index"))


@app.route("/movies/<int:user_id>")
def movies(user_id):
    """
    Filmverwaltungsseite für einen bestimmten Nutzer.
    """
    with next(get_db()) as db:
        db_manager = DatabaseManager(db)
        #TODO richtigen USER einbauen
        user = db.query(DatabaseManager.User).filter_by(id=user_id).first()
        movies = db_manager.list_movies_for_user(user_id=user_id)

    return render_template("movie_side.html", user=user, movies=movies)


@app.route("/add_movie/<int:user_id>", methods=["POST"])
def add_movie(user_id):
    """
    Film hinzufügen und mit einem Nutzer verbinden.
    """
    #TODO bisher wird kein direcotor in die datenbank eingebuat
    movie_title = request.form.get("movie_title")
    if movie_title:
        # Filmdaten von der OMDb API abrufen
        movie_data = omdb_api.fetch_movie_data(movie_title)

        if movie_data:
            # Daten validieren
            release_year = DataValidator.validate_release_year(movie_data.get("Year", ""))
            rating = DataValidator.validate_numeric_field(movie_data.get("imdbRating", 0), "IMDb Rating")
            director_name = movie_data.get("Director", "Unknown")

            # Regisseur aufteilen (Vorname und Nachname)
            director_first_name = director_name.split()[0] if director_name else "Unknown"
            director_last_name = " ".join(director_name.split()[1:]) if len(director_name.split()) > 1 else "Unknown"

            # Film in die Datenbank einfügen
            with next(get_db()) as db:
                db_manager = DatabaseManager(db)
                db_manager.add_movie_for_user(
                    user_id=user_id,
                    movie_title=movie_title,
                    release_date=release_year,
                    director_id=None,  # Optional: Regisseur-ID hinzufügen
                    rating=rating or 0.0,
                )

    return redirect(url_for("movies", user_id=user_id))


@app.route("/delete_movie/<int:user_id>/<int:movie_id>", methods=["POST"])
def delete_movie(user_id, movie_id):
    """
    Filmverbindung eines Nutzers löschen (und ggf. den Film selbst).
    """
    with next(get_db()) as db:
        db_manager = DatabaseManager(db)
        db_manager.delete_movie_for_user(user_id=user_id, movie_id=movie_id)

    return redirect(url_for("movies", user_id=user_id))


@app.route("/update_rating/<int:user_id>/<int:movie_id>", methods=["POST"])
def update_rating(user_id, movie_id):
    """
    Bewertung eines Films aktualisieren.
    """
    new_rating = request.form.get("new_rating")
    if new_rating:
        with next(get_db()) as db:
            db_manager = DatabaseManager(db)
            db_manager.update_movie_rating(user_id=user_id, movie_id=movie_id,
                                           new_rating=float(new_rating))

    return redirect(url_for("movies", user_id=user_id))


if __name__ == "__main__":
    app.run(debug=True)
