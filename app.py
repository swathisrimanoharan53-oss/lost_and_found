from flask import Flask, render_template, request, redirect, session
import psycopg2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

# Upload folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()


# Create tables if not exist
def init_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS lost_items(
        id SERIAL PRIMARY KEY,
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
        id SERIAL PRIMARY KEY,
        title TEXT,
        description TEXT,
        location TEXT,
        contact TEXT,
        date TEXT,
        image TEXT
    )
    """)
    
    conn.commit()

init_db()


# Login
@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username,password)
        )

        user = cur.fetchone()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")


# Register
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username,password)
        )

        conn.commit()

        return redirect("/")

    return render_template("register.html")


# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


# Report Lost Item
@app.route("/lost", methods=["GET","POST"])
def lost():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        contact = request.form["contact"]
        date = request.form["date"]

        image = request.files["image"]

        filename = ""
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cur.execute("""
        INSERT INTO lost_items(title,description,location,contact,date,image)
        VALUES(%s,%s,%s,%s,%s,%s)
        """,(title,description,location,contact,date,filename))

        conn.commit()

        return redirect("/dashboard")

    return render_template("add_lost.html")


# Report Found Item
@app.route("/found", methods=["GET","POST"])
def found():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]
        contact = request.form["contact"]
        date = request.form["date"]

        image = request.files["image"]

        filename = ""
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cur.execute("""
        INSERT INTO found_items(title,description,location,contact,date,image)
        VALUES(%s,%s,%s,%s,%s,%s)
        """,(title,description,location,contact,date,filename))

        conn.commit()

        return redirect("/dashboard")

    return render_template("add_found.html")


# View Lost Items
@app.route("/view-lost")
def view_lost():

    cur.execute("SELECT * FROM lost_items")
    items = cur.fetchall()

    return render_template("view_lost.html",items=items)


# View Found Items
@app.route("/view-found")
def view_found():

    cur.execute("SELECT * FROM found_items")
    items = cur.fetchall()

    return render_template("view_found.html",items=items)


# Logout
@app.route("/logout")
def logout():

    session.pop("user",None)

    return redirect("/")


if __name__ == "__main__":

    port = int(os.environ.get("PORT",10000))

    app.run(host="0.0.0.0",port=port)
