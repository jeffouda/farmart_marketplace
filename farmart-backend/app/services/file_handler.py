import csv
from io import StringIO
from app.models import Livestock
from app import db

REQUIRED_FIELDS = ["animal_type", "weight", "price", "location"]

def parse_livestock_csv(file_stream, farmer_id):
    csv_data = csv.DictReader(StringIO(file_stream.read().decode("utf-8")))
    animals = []

    for row in csv_data:
        for field in REQUIRED_FIELDS:
            if not row.get(field):
                raise ValueError(f"Missing field: {field}")

        animal = Livestock(
            farmer_id=farmer_id,
            animal_type=row["animal_type"],
            weight=float(row["weight"]),
            price=float(row["price"]),
            location=row["location"],
            breed=row.get("breed"),
            age_months=row.get("age_months")
        )
        animals.append(animal)

    try:
        db.session.bulk_save_objects(animals)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return len(animals)
