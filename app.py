from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change before going live

ADMIN_USERNAME = "Manikandan"
ADMIN_PASSWORD = "Mani@2002"
PROJECT_NAME = "Coffee portal"
UPI_ID = "manikandan85670@oksbi"

# Calculate amount
def get_amount(cups):
    return 5 if cups == 1 else 10 if cups == 2 else 15 if cups == 3 else 0


# Save to CSV
def save_to_csv(order):
    file_exists = os.path.isfile("data.csv")
    with open("data.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "Phone", "Work", "Location", "Cups", "Amount"])
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([now, order["name"], order["phone"], order["work"], order["location"], order["cups"], order["amount"]])


# Read CSV for Admin dashboard
def load_csv():
    records = []
    if os.path.isfile("data.csv"):
        with open("data.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    return records


@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        work = request.form["work"]
        location = request.form["location"]
        cups = int(request.form["cups"])
        amount = get_amount(cups)

        session["order"] = {
            "name": name,
            "phone": phone,
            "work": work,
            "location": location,
            "cups": cups,
            "amount": amount,
        }
        return redirect(url_for("payment"))

    return render_template("form.html", project_name=PROJECT_NAME)


@app.route("/payment", methods=["GET", "POST"])
def payment():
    if "order" not in session:
        return redirect(url_for("form"))

    order = session["order"]

    if request.method == "POST":
        save_to_csv(order)
        session.pop("order")
        return redirect(url_for("success"))

    return render_template("payment.html", project_name=PROJECT_NAME, upi_id=UPI_ID, amount=order["amount"])


@app.route("/success")
def success():
    return render_template("success.html", project_name=PROJECT_NAME)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", project_name=PROJECT_NAME, error="Invalid login")

    return render_template("admin_login.html", project_name=PROJECT_NAME)


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    records = load_csv()
    return render_template("admin_dashboard.html", project_name=PROJECT_NAME, records=records)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run()
