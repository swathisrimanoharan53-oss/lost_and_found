from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "lostfoundsecret"

UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# create image folder if not exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_db():
    conn = sqlite3.connect("database.db")
    return conn


def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lost_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_name TEXT,
        contact TEXT,
        item_name TEXT,
        category TEXT,
        description TEXT,
        date_lost TEXT,
        location TEXT,
        status TEXT,
        image TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS found_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_name TEXT,
        contact TEXT,
        item_name TEXT,
        category TEXT,
        description TEXT,
        date_found TEXT,
        location TEXT,
        status TEXT,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Username already exists. Please login.")
            conn.close()
            return redirect(url_for("login"))

        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- REPORT LOST ----------------
@app.route("/report_lost", methods=["GET", "POST"])
def report_lost():

    if request.method == "POST":

        owner = request.form["owner_name"]
        contact = request.form["contact"]
        item = request.form["item_name"]
        category = request.form["category"]
        desc = request.form["description"]
        date = request.form["date_lost"]
        location = request.form["location"]
        status = request.form["status"]

        filename = ""

        # safe image upload
        if "image" in request.files:
            image_file = request.files["image"]

            if image_file.filename != "":
                filename = image_file.filename
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image_file.save(filepath)

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO lost_items
        (owner_name,contact,item_name,category,description,date_lost,location,status,image)
        VALUES(?,?,?,?,?,?,?,?,?)
        """, (owner,contact,item,category,desc,date,location,status,filename))

        conn.commit()
        conn.close()

        flash("Lost item reported successfully")

        return redirect(url_for("view_lost"))

    return render_template("report_lost.html")


# ---------------- REPORT FOUND ----------------
@app.route("/report_found", methods=["GET", "POST"])
def report_found():

    if request.method == "POST":

        owner = request.form["owner_name"]
        contact = request.form["contact"]
        item = request.form["item_name"]
        category = request.form["category"]
        desc = request.form["description"]
        date = request.form["date_found"]
        location = request.form["location"]
        status = request.form["status"]

        filename = ""

        # safe image upload
        if "image" in request.files:
            image_file = request.files["image"]

            if image_file.filename != "":
                filename = image_file.filename
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image_file.save(filepath)

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO found_items
        (owner_name,contact,item_name,category,description,date_found,location,status,image)
        VALUES(?,?,?,?,?,?,?,?,?)
        """, (owner,contact,item,category,desc,date,location,status,filename))

        conn.commit()
        conn.close()

        flash("Found item reported successfully")

        return redirect(url_for("view_found"))

    return render_template("report_found.html")


# ---------------- VIEW LOST ----------------
@app.route("/view_lost")
def view_lost():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM lost_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_lost.html", items=items)


# ---------------- VIEW FOUND ----------------
@app.route("/view_found")
def view_found():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM found_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_found.html", items=items)


if __name__ == "__main__":
    app.run(debug=True)
