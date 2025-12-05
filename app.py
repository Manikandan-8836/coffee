from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
import mysql.connector
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change before going live

ADMIN_USERNAME = "Manikandan"
ADMIN_PASSWORD = "Mani@2002"
PROJECT_NAME = "Coffee portal"
UPI_ID = "manikandan85670@oksbi"

# ------------------- MYSQL CONFIG -------------------
db_config = {
    "host": "YOUR_HOST",
    "port": YOUR_PORT,
    "user": "YOUR_USER",
    "password": "YOUR_PASSWORD",
    "database": "YOUR_DATABASE"
}

# Create table automatically if not exists
def create_table():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp VARCHAR(30),
            name VARCHAR(50),
            phone VARCHAR(20),
            work VARCHAR(100),
            location VARCHAR(100),
            cups INT,
            amount INT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()

# Save order to SQL
def save_to_db(order):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO orders (timestamp, name, phone, work, location, cups, amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (now, order["name"], order["phone"], order["work"], order["location"], order["cups"], order["amount"]))
    conn.commit()
    cur.close()
    conn.close()

# Read all orders
def load_orders():
    conn = mysql.connector.connect(**db_config)
    df = pd.read_sql("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()
    return df


# ------------------- ROUTES -------------------

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        work = request.form["work"]
        location = request.form["location"]
        cups = int(request.form["cups"])
        amount = 5 if cups == 1 else 10 if cups == 2 else 15

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
        save_to_db(order)
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

    df = load_orders()
    return render_template("admin_dashboard.html", project_name=PROJECT_NAME, tables=df.to_dict(orient="records"))


@app.route("/admin/download")
def admin_download():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    df = load_orders()
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="orders.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run()
