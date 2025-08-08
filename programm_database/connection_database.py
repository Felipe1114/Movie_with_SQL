from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# connection to SQLite-database
DATABASE_URL = "sqlite:///../programm_data/database/movie_database.db"
engine = create_engine(DATABASE_URL, echo=False)

# create SessionFactory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create new session
def get_db():
	# db ist die session
	db = SessionLocal()
	try:
		# yield for pausing funktion
	    yield db
	finally:
		db.close()
