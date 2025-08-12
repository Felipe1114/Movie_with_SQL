from dataclasses import field


class DataValidator:
	@staticmethod
	def validate_release_year(release_date: str):
		"""
		validates and converts the release year of a movie.
		:param release_date: release date of movie (string)
		:return: an integer for the release_year || None, if convertion fails
		"""
		try:
			# check if releaseyear is a single year (YYYY)
			if release_date.isdigit():
				return int(release_date)

			# check if it es a time range (YYYY-YYYY)
			if "–" in release_date:
				start_year = release_date.split("–")[0]
				if start_year.isdigit():
					return int(start_year)

			print(f"Wrong release_year format: {release_date}")
			return None
		except Exception as e:
			print(f"Error with validation from release_year: {e}")
   
			return None

	@staticmethod
	def validate_numeric_field(value, field_name):
		"""
		validates numeric fields, like rating
		:param value: value of a field
		:param field_name: name of a field (for debuging)
		:return: a float || None, if convertion fails
		"""
		try:
			return float(value)
		
		except ValueError:
			print(f"Value Error for {field_name}: {value}")
   
			return None

