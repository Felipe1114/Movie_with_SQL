from abc import ABC, abstractmethod

class DatabaseManager(ABC):
	"""BaseClass for all database managers"""
	
	@abstractmethod
	def get_user(self, user_id: int):
		"""
		Gets specific user from database by user_id

		:param user_id: id from specific user
		:return: user || None
		"""
		pass
	
	@abstractmethod
	def get_user_id(self, user_name: str):
		"""
		gives back the id for specific user

		:arg user_name: name from user; str
		:return: user_id || None
		"""
		pass
	
	
	@abstractmethod
	def add_user(self, user_name: str):
		"""
		Adds a new user to database.
		If user_name exist in database, new_user = existing_user

		:param user_name: name for new user
		:return: new_user || existing_user
		"""
		pass
	
	@abstractmethod
	def delete_user(self, user_id: int):
		"""
		Deletes a user form database and all connected data
		"""
		pass
	
	@abstractmethod
	def list_user(self):
		"""
		Lists up all users

		:return: list of users
		"""
		pass
	
	@abstractmethod
	def list_movies_for_user(self, user_id: int) -> tuple:
		"""
		Lists up all movies form user, by its id

		movie-tuple architecture:
			(Movie_name: str, release_year: int, rating: float, director_first_name: str, director_last_name: str)
		"""
		pass
		
	@abstractmethod
	def add_movie_for_user(self, user_id: int, movie_title: str, release_date: int, director_first_name: str,
	                       director_last_name: str, rating: float):
		"""
		adds a new movie to user and links it to all linked tables
		"""
		pass
		
	@abstractmethod
	def delete_movie_for_user(self, user_id: int, movie_id: int):
		"""
		Deletes the connection from user to movie
		if no user is connected to the movie, the movie also will deleted from database
		"""
		pass
	
	@abstractmethod
	def update_movie_rating(self, user_id: int, movie_id: int, new_rating: float):
		"""
		update rating of a movie for a specific user
		"""
		pass
	
	@abstractmethod
	def get_movie_from_user(self, movie_id, user_id):
		"""
		gives back a movie, with specific rating, user and the user_id
		"""
		pass
	
	@abstractmethod
	def add_director(self, director_first_name: str, director_last_name: str):
		"""
		adds a new director to the database
		"""
		pass
	
	@abstractmethod
	def get_director(self, director_id: int):
		"""
		gives back a director on base of his id
		"""
		pass
	
	@abstractmethod
	def list_up_directors(self):
		"""
		Lists up all directors form database
		"""
		pass
	
	@abstractmethod
	def delete_director(self, director_id: int):
		"""
		deletes a director on base of his id
		"""
		pass
		