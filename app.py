from flask import Flask, render_template, request, redirect, session
import boto3
import uuid
import os

app = Flask(__name__)
app.secret_key = "cinibooker-secret"

AWS_REGION = "ap-south-1"

# ================= AWS CLIENTS =================
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)

movies_table = dynamodb.Table("Movies")
bookings_table = dynamodb.Table("Bookings")

SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:XXXX:CineBookerBookingTopic"


# ================= HOME =================
@app.route("/")
def home():
    response = movies_table.scan()
    movies = response.get("Items", [])

    # remove duplicate titles
    seen = set()
    unique_movies = []
    for m in movies:
        key = m["title"].lower()
        if key not in seen:
            seen.add(key)
            unique_movies.append(m)

    return render_template("home.html", movies=unique_movies)


# ================= BOOK =================
@app.route("/book/<movie_id>")
def book(movie_id):
    return render_template("seat.html", movie_id=movie_id)


# ================= PAYMENT =================
@app.route("/payment", methods=["POST"])
def payment():
    seats = request.form.getlist("seats")
    total = request.form.get("total")

    booking_id = str(uuid.uuid4())

    bookings_table.put_item(
        Item={
            "booking_id": booking_id,
            "user_id": session.get("user", "guest"),
            "seats": ",".join(seats),
            "total": int(total)
        }
    )

    # SNS notification
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="🎟 CineBooker Ticket Confirmed",
        Message=f"""
Booking ID: {booking_id}
Seats: {', '.join(seats)}
Total: ₹{total}
Enjoy your movie 🎬
"""
    )

    return render_template(
        "ticket.html",
        booking_id=booking_id,
        seats=seats,
        total=total
    )


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
