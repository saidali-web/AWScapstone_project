from app import db
from models import Movie

movies = [
    ("Mersal", "Tamil"),
    ("Theri", "Tamil"),
    ("Ghilli", "Tamil"),
    ("Jana Nayagan", "Tamil"),
    ("Leo", "Tamil"),
]

for title, lang in movies:
    if not Movie.query.filter_by(title=title, language=lang).first():
        db.session.add(Movie(title=title, language=lang))

db.session.commit()
print("Movies seeded")
