import os
import qrcode
from io import BytesIO
import base64

from flask import Flask, render_template, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Movie, Theatre, Show, Seat, Booking, User

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "cinebooker_secret"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# ---------------- HOME ----------------
@app.route("/")
def home():
    all_movies = Movie.query.all()

    unique_movies = {}
    for m in all_movies:
        key = (m.title.lower(), m.language)
        if key not in unique_movies:
            unique_movies[key] = m

    movies = list(unique_movies.values())

    return render_template("home.html", movies=movies)



# ---------------- CITY ----------------
@app.route("/set_city", methods=["POST"])
def set_city():
    session["city"] = request.form.get("city", "Chennai")
    return redirect("/")

# ---------------- BOOK MOVIE ----------------
@app.route("/book/<int:movie_id>")
def book(movie_id):
    city = session.get("city", "Chennai")
    movie = Movie.query.get_or_404(movie_id)

    shows = (
        Show.query.join(Theatre)
        .filter(Show.movie_id == movie_id, Theatre.city == city)
        .all()
    )

    theatre_map = {}
    for show in shows:
        t = show.theatre
        theatre_map.setdefault(t.id, {"theatre": t, "shows": []})
        theatre_map[t.id]["shows"].append(show)

    return render_template(
        "booking.html",
        movie=movie,
        theatre_map=theatre_map,
        city=city
    )

# ---------------- SEATS (STEP 1) ----------------
@app.route("/seats/<int:show_id>")
def seat_selection(show_id):
    session["current_show_id"] = show_id  # ✅ VERY IMPORTANT

    seats = Seat.query.filter_by(show_id=show_id).all()
    seat_map = {"Balcony": [], "First Class": []}

    for seat in seats:
        row = seat.seat_number[:-2]
        number = seat.seat_number[-2:]

        data = {
            "seat_number": seat.seat_number,
            "row": row,
            "number": number,
            "is_booked": seat.is_booked
        }

        if row.startswith("A"):
            seat_map["Balcony"].append(data)
        else:
            seat_map["First Class"].append(data)

    return render_template(
        "seats.html",
        seat_map=seat_map,
        show_id=show_id
    )

# ---------------- PAYMENT (STEP 3) ----------------
@app.route("/payment", methods=["POST"])
def payment():
    seats = request.form.getlist("seats")
    total = request.form.get("total")

    if not seats or not total:
        return redirect("/")

    session["payment_seats"] = seats
    session["payment_total"] = int(total)

    return render_template(
        "payment.html",
        seats=seats,
        total=total,
        city=session.get("city")
    )

# ---------------- CONFIRM PAYMENT (STEP 4) ----------------
@app.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    if "user_id" not in session:
        return redirect("/login")

    seats = session.get("payment_seats")
    total = session.get("payment_total")
    method = request.form.get("payment_method")
    show_id = session.get("current_show_id")

    if not seats or not total or not method or not show_id:
        return redirect("/")

    # Create booking
    booking = Booking(
        user_id=session["user_id"],
        show_id=show_id,
        seats=",".join(seats)
    )
    db.session.add(booking)

    # Mark seats booked
    for seat_no in seats:
        seat = Seat.query.filter_by(
            show_id=show_id,
            seat_number=seat_no
        ).first()
        if seat:
            seat.is_booked = True

    db.session.commit()

    # Generate QR
    qr_data = f"""
    Booking ID: {booking.id}
    Seats: {booking.seats}
    Amount: ₹{total}
    """
    qr = qrcode.make(qr_data)

    qr_path = f"static/qr/booking_{booking.id}.png"
    os.makedirs("static/qr", exist_ok=True)
    qr.save(qr_path)

    show = Show.query.get(show_id)
    movie = Movie.query.get(show.movie_id)
    theatre = Theatre.query.get(show.theatre_id)

    return render_template(
        "confirmation.html",
        booking=booking,
        qr_image=qr_path,
        movie=movie,
        show=show,
        theatre=theatre,
        total=total
    )


# ---------------- AUTH ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect("/")
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"]
        ).first()
        if user and check_password_hash(
            user.password, request.form["password"]
        ):
            session["user_id"] = user.id
            return redirect("/")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")

# ---------------- MY BOOKINGS ----------------
@app.route("/my_bookings")
def my_bookings():
    if "user_id" not in session:
        return redirect("/login")

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings,
        city=session.get("city")
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
