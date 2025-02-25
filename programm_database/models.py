from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# baseclass for all models:
Base = declarative_base()


class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
  name = Column(String, nullable=False)

  # relationship to UserToMovie class
  movies = relationship("UserToMovie", back_populates="user")


class Movie(Base):
  __tablename__ = 'movies'
  id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
  title = Column(String, nullable=False)
  release_date = Column(Integer)
  director_id = Column(Integer, ForeignKey('directors.id'))

  # relationship to Director class
  director = relationship("Director", back_populates="movies")

  # relationshiop to UserToMovie class
  user = relationship("UserToMovie", back_populates="movies")


class Director(Base):
  __tablename__ = 'directors'
  id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
  first_name = Column(String, nullable=False)
  last_name = Column(String, nullable=False)

  # relationship to Movies class
  movies = relationship("Movie", back_populates="director")


class UserToMovie(Base):
  __tablename__ = 'user_to_movie'
  user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, nullable=False)
  movie_id = Column(Integer, ForeignKey('movies.id'), primary_key=True, nullable=False)
  rating = Column(Numeric)

  # relationship to Users and Movies
  user = relationship("User", back_populates="movies")
  movies = relationship("Movie", back_populates="user")
