from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

db = SQLAlchemy()

# ---------------- USER ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


# ---------------- MOVIE ----------------
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    language = db.Column(db.String(50))
    poster = db.Column(db.String(200))


# ---------------- THEATRE ----------------
class Theatre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("name", "city", name="unique_theatre_city"),
    )


# ---------------- SHOW ----------------
class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)
    theatre_id = db.Column(db.Integer, db.ForeignKey("theatre.id"), nullable=False)
    show_time = db.Column(db.String(20), nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "movie_id", "theatre_id", "show_time",
            name="unique_show"
        ),
    )

    movie = db.relationship("Movie", backref="shows")
    theatre = db.relationship("Theatre", backref="shows")



# ---------------- SEAT ----------------
class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"), nullable=False)

    seat_number = db.Column(db.String(6), nullable=False)  # AA01, A12
    seat_class = db.Column(db.String(30), nullable=False) # Balcony / First Class
    price = db.Column(db.Integer, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)

    show = db.relationship("Show", backref="seats")


# ---------------- BOOKING ----------------
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"), nullable=False)
    seats = db.Column(db.String(100), nullable=False)  # "AA01,AA02"

    user = db.relationship("User", backref="bookings")
    show = db.relationship("Show", backref="bookings")


# ---------------- AUTO CREATE SEATS (BOOKMYSHOW STYLE) ----------------
@event.listens_for(Show, "after_insert")
def create_seats(mapper, connection, target):

    layout = {
        "Balcony": {
            "rows": ["AA", "AB", "AC", "AD"],
            "cols": 14,
            "price": 120
        },
        "First Class": {
            "rows": ["A", "B", "C", "D", "E", "F"],
            "cols": 24,
            "price": 100
        }
    }

    seats = []

    for seat_class, config in layout.items():
        for row in config["rows"]:
            for col in range(1, config["cols"] + 1):
                seats.append({
                    "show_id": target.id,
                    "seat_number": f"{row}{str(col).zfill(2)}",
                    "seat_class": seat_class,
                    "price": config["price"],
                    "is_booked": False
                })

    connection.execute(Seat.__table__.insert(), seats)
