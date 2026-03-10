from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect("lostfound.db")
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
        date TEXT,
        image TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS found_items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        location TEXT,
        contact TEXT,
        date TEXT,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("lostfound.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = cur.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("lostfound.db")
        cur = conn.cursor()

        cur.execute("INSERT INTO users(username,password) VALUES(?,?)",(username,password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html")
    return redirect("/")


# ---------- REPORT LOST ITEM ----------
@app.route("/lost", methods=["GET","POST"])
def lost():
    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        contact = request.form["contact"]
        date = request.form["date"]

        image = request.files["image"]
        filename = secure_filename(image.filename)

        if filename != "":
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = sqlite3.connect("lostfound.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO lost_items(title,description,location,contact,date,image)
        VALUES(?,?,?,?,?,?)
        """,(title,description,location,contact,date,filename))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_lost.html")


# ---------- REPORT FOUND ITEM ----------
@app.route("/found", methods=["GET","POST"])
def found():
    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        contact = request.form["contact"]
        date = request.form["date"]

        image = request.files["image"]
        filename = secure_filename(image.filename)

        if filename != "":
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = sqlite3.connect("lostfound.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO found_items(title,description,location,contact,date,image)
        VALUES(?,?,?,?,?,?)
        """,(title,description,location,contact,date,filename))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_found.html")


# ---------- VIEW LOST ITEMS ----------
@app.route("/view-lost")
def view_lost():
    conn = sqlite3.connect("lostfound.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM lost_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_lost.html", items=items)


# ---------- VIEW FOUND ITEMS ----------
@app.route("/view-found")
def view_found():
    conn = sqlite3.connect("lostfound.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM found_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_found.html", items=items)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/")


# ---------- RUN APP ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port)
