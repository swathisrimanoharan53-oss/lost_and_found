from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lost_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        location TEXT,
        contact TEXT,
        date TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS found_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        location TEXT,
        contact TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect("/login")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("INSERT INTO users(username,password) VALUES(?,?)",
                    (username, password))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?",
                    (username, password))

        user = cur.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


# ---------------- REPORT LOST ITEM ----------------

@app.route("/lost", methods=["GET", "POST"])
def lost():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        contact = request.form["contact"]
        date = request.form["date"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO lost_items(title,description,location,contact,date) VALUES(?,?,?,?,?)",
            (title, description, location, contact, date)
        )

        conn.commit()
        conn.close()

        return redirect("/view-lost")

    return render_template("add_lost.html")


# ---------------- REPORT FOUND ITEM ----------------

@app.route("/found", methods=["GET", "POST"])
def found():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        contact = request.form["contact"]
        date = request.form["date"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO found_items(title,description,location,contact,date) VALUES(?,?,?,?,?)",
            (title, description, location, contact, date)
        )

        conn.commit()
        conn.close()

        return redirect("/view-found")

    return render_template("add_found.html")


# ---------------- VIEW LOST ITEMS ----------------

@app.route("/view-lost")
def view_lost():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM lost_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_lost.html", items=items)


# ---------------- VIEW FOUND ITEMS ----------------

@app.route("/view-found")
def view_found():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM found_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_found.html", items=items)


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
