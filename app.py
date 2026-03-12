import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this in production

# ====== Database setup (SQLite temporary DB) ======
DB_PATH = "lost_found.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    # Lost items table
    c.execute("""
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            description TEXT,
            date_lost TEXT,
            location TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    # Found items table
    c.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            description TEXT,
            date_found TEXT,
            location TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ====== Routes ======

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("User registered! Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists!")
        conn.close()
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/report_lost", methods=["GET", "POST"])
def report_lost():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        date_lost = request.form["date_lost"]
        location = request.form["location"]
        user_id = session["user_id"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO lost_items (item_name, description, date_lost, location, user_id) VALUES (?, ?, ?, ?, ?)",
                  (item_name, description, date_lost, location, user_id))
        conn.commit()
        conn.close()
        flash("Lost item reported successfully!")
        return redirect(url_for("dashboard"))
    return render_template("report_lost.html")

@app.route("/report_found", methods=["GET", "POST"])
def report_found():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        date_found = request.form["date_found"]
        location = request.form["location"]
        user_id = session["user_id"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO found_items (item_name, description, date_found, location, user_id) VALUES (?, ?, ?, ?, ?)",
                  (item_name, description, date_found, location, user_id))
        conn.commit()
        conn.close()
        flash("Found item reported successfully!")
        return redirect(url_for("dashboard"))
    return render_template("report_found.html")

@app.route("/view_lost")
def view_lost():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT item_name, description, date_lost, location FROM lost_items")
    items = c.fetchall()
    conn.close()
    return render_template("view_lost.html", items=items)

@app.route("/view_found")
def view_found():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT item_name, description, date_found, location FROM found_items")
    items = c.fetchall()
    conn.close()
    return render_template("view_found.html", items=items)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ====== Run app ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render provides PORT
    app.run(host="0.0.0.0", port=port, debug=True)
