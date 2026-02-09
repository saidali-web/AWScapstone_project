from app import app
from models import db, Movie, Theatre, Show

with app.app_context():

    # ---------------- FETCH MOVIES ----------------
    leo = Movie.query.filter_by(title="Leo", city="Chennai").first()
    salaar_blr = Movie.query.filter_by(title="Janayagan", city="Bangalore").first()
    salaar_wgl = Movie.query.filter_by(title="Janayagan", city="Warangal").first()

    if not leo or not salaar_blr or not salaar_wgl:
        print("❌ Movies not found. Run seed_movies.py first.")
        exit()

    # ---------------- FETCH THEATRES ----------------
    chennai_theatres = Theatre.query.filter_by(city="Chennai").all()
    bangalore_theatres = Theatre.query.filter_by(city="Bangalore").all()
    warangal_theatres = Theatre.query.filter_by(city="Warangal").all()

    # ---------------- CREATE SHOWS ----------------
    def create_show(movie, theatre, time):
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

    for t in chennai_theatres:
        create_show(leo, t, "6:30 PM")
        create_show(leo, t, "9:30 PM")

    for t in bangalore_theatres:
        create_show(Janayagan_blr, t, "7:00 PM")

    for t in warangal_theatres:
        create_show(Janayagan_wgl, t, "9:00 PM")

    db.session.commit()
    print("✅ Shows seeded successfully")
