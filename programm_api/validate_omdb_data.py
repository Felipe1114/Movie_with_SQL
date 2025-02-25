class DataValidator:
  @staticmethod
  def validate_release_year(release_date: str):
    """
    Validiert und konvertiert das Erscheinungsjahr eines Films.
    :param release_date: Das Erscheinungsjahr (String).
    :return: Ein Integer-Wert für das Jahr oder None, wenn die Konvertierung fehlschlägt.
    """
    try:
      # Prüfen, ob das Erscheinungsjahr ein einzelnes Jahr ist (z.B., "1993")
      if release_date.isdigit():
        return int(release_date)

      # Prüfen, ob es sich um eine Zeitspanne handelt (z.B., "1993–1995")
      if "–" in release_date:
        start_year = release_date.split("–")[0]
        if start_year.isdigit():
          return int(start_year)

      print(f"Ungültiges Erscheinungsjahr-Format: {release_date}")
      return None
    except Exception as e:
      print(f"Fehler bei der Validierung des Erscheinungsjahrs: {e}")
      return None

  @staticmethod
  def validate_numeric_field(value, field_name):
    """
    Validiert numerische Felder wie Bewertungen.
    :param value: Der Wert des Feldes.
    :param field_name: Der Name des Feldes (für Debugging).
    :return: Ein Float-Wert oder None, wenn die Konvertierung fehlschlägt.
    """
    try:
      return float(value)
    except ValueError:
      print(f"Ungültiger Wert für {field_name}: {value}")
      return None

