from app import db
from models import Movie, Theatre, Show

movies = Movie.query.all()
theatres = Theatre.query.all()

times = ["10:30 AM", "6:30 PM"]

for movie in movies:
    for theatre in theatres:
        for time in times:
            exists = Show.query.filter_by(
                movie_id=movie.id,
                theatre_id=theatre.id,
                show_time=time
            ).first()

            if not exists:
                db.session.add(
                    Show(
                        movie_id=movie.id,
                        theatre_id=theatre.id,
                        show_time=time
                    )
                )

db.session.commit()
print("Shows seeded")