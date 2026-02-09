from app import db
from models import Theatre

theatres = [
    ("Asian CineSquare", "Chennai"),
    ("SPI Palazzo", "Chennai"),
    ("PVR Warangal", "Warangal"),
    ("Asian CineSquare", "Warangal"),
    ("PVR Orion Mall", "Bangalore"),
    ("INOX Garuda Mall", "Bangalore"),
]

for name, city in theatres:
    if not Theatre.query.filter_by(name=name, city=city).first():
        db.session.add(Theatre(name=name, city=city))

db.session.commit()
print("Theatres seeded")
