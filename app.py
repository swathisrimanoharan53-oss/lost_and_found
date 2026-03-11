from flask import Flask, render_template, request, redirect, session
import psycopg2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secretkey"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()


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


@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        if username=="admin" and password=="admin":
            session["user"]="admin"
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


@app.route("/report_lost",methods=["GET","POST"])
def report_lost():

    if request.method=="POST":

        title=request.form["title"]
        description=request.form["description"]
        location=request.form["location"]
        contact=request.form["contact"]
        date=request.form["date"]

        image=request.files["image"]

        filename=""

        if image:
            filename=secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"],filename))

        cur.execute("""
        INSERT INTO lost_items(title,description,location,contact,date,image)
        VALUES(%s,%s,%s,%s,%s,%s)
        """,(title,description,location,contact,date,filename))

        conn.commit()

        return redirect("/dashboard")

    return render_template("report_lost.html")


@app.route("/report_found",methods=["GET","POST"])
def report_found():

    if request.method=="POST":

        title=request.form["title"]
        description=request.form["description"]
        location=request.form["location"]
        contact=request.form["contact"]
        date=request.form["date"]

        image=request.files["image"]

        filename=""

        if image:
            filename=secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"],filename))

        cur.execute("""
        INSERT INTO found_items(title,description,location,contact,date,image)
        VALUES(%s,%s,%s,%s,%s,%s)
        """,(title,description,location,contact,date,filename))

        conn.commit()

        return redirect("/dashboard")

    return render_template("report_found.html")


@app.route("/view_lost")
def view_lost():

    cur.execute("SELECT * FROM lost_items")
    items=cur.fetchall()

    return render_template("view_lost.html",items=items)


@app.route("/view_found")
def view_found():

    cur.execute("SELECT * FROM found_items")
    items=cur.fetchall()

    return render_template("view_found.html",items=items)


@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")


if __name__=="__main__":

    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
