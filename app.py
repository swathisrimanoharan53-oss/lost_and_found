from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DATABASE ----------------

def get_db():
    db_path = os.path.join(os.getcwd(), "users.db")
    con = sqlite3.connect(db_path)
    return con


def init_db():
    con = get_db()
    cur = con.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )
    """)

    # Lost items table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lost_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT
        )
    """)

    # Found items table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS found_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT
        )
    """)

    con.commit()
    con.close()


init_db()


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        con.close()

        if user:
            session["user"] = user[1]
            session["role"] = user[3]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Login Details"

    return render_template("login.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        con = get_db()
        cur = con.cursor()

        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, "user")
        )

        con.commit()
        con.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# ---------------- ADD LOST ITEM ----------------

@app.route("/lost", methods=["GET", "POST"])
def lost():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form("description")

        con = get_db()
        cur = con.cursor()

        cur.execute(
            "INSERT INTO lost_items (title, description) VALUES (?, ?)",
            (title, description)
        )

        con.commit()
        con.close()

        return redirect(url_for("dashboard"))

    return render_template("add_lost.html")


# ---------------- ADD FOUND ITEM ----------------

@app.route("/found", methods=["GET", "POST"])
def found():

    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]

        con = get_db()
        cur = con.cursor()

        cur.execute(
            "INSERT INTO found_items (title, description) VALUES (?, ?)",
            (title, description)
        )

        con.commit()
        con.close()

        return redirect(url_for("dashboard"))

    return render_template("add_found.html")


# ---------------- VIEW LOST ITEMS ----------------

@app.route("/view-lost")
def view_lost():

    if "user" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM lost_items")
    items = cur.fetchall()

    con.close()

    return render_template("view.html", items=items, title="Lost Items")


# ---------------- VIEW FOUND ITEMS ----------------

@app.route("/view-found")
def view_found():

    if "user" not in session:
        return redirect(url_for("login"))

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM found_items")
    items = cur.fetchall()

    con.close()

    return render_template("view.html", items=items, title="Found Items")


# ---------------- ADMIN PANEL ----------------

@app.route("/admin")
def admin():

    if session.get("role") != "admin":
        return "Access Denied"

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM lost_items")
    lost = cur.fetchall()

    cur.execute("SELECT * FROM found_items")
    found = cur.fetchall()

    con.close()

    return render_template("admin.html", lost=lost, found=found)


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
