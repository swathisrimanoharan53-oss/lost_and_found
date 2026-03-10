from flask import Flask, render_template, request, redirect
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -------- DATABASE --------

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

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


# -------- DASHBOARD --------

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# -------- ADD LOST ITEM --------

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
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO lost_items(title,description,location,contact,date,image) VALUES(?,?,?,?,?,?)",
        (title,description,location,contact,date,filename)
        )

        conn.commit()
        conn.close()

        return redirect("/view-lost")

    return render_template("add_lost.html")


# -------- ADD FOUND ITEM --------

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
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO found_items(title,description,location,contact,date,image) VALUES(?,?,?,?,?,?)",
        (title,description,location,contact,date,filename)
        )

        conn.commit()
        conn.close()

        return redirect("/view-found")

    return render_template("add_found.html")


# -------- VIEW LOST --------

@app.route("/view-lost")
def view_lost():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM lost_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_lost.html",items=items)


# -------- VIEW FOUND --------

@app.route("/view-found")
def view_found():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM found_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_found.html",items=items)


# -------- UPDATE LOST --------

@app.route("/update-lost/<int:id>",methods=["GET","POST"])
def update_lost(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method=="POST":

        title=request.form["title"]
        description=request.form["description"]
        location=request.form["location"]
        contact=request.form["contact"]
        date=request.form["date"]

        cur.execute("""
        UPDATE lost_items
        SET title=?,description=?,location=?,contact=?,date=?
        WHERE id=?
        """,(title,description,location,contact,date,id))

        conn.commit()
        conn.close()

        return redirect("/view-lost")

    cur.execute("SELECT * FROM lost_items WHERE id=?",(id,))
    item=cur.fetchone()

    conn.close()

    return render_template("update_lost.html",item=item)


# -------- UPDATE FOUND --------

@app.route("/update-found/<int:id>",methods=["GET","POST"])
def update_found(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method=="POST":

        title=request.form["title"]
        description=request.form["description"]
        location=request.form["location"]
        contact=request.form["contact"]
        date=request.form["date"]

        cur.execute("""
        UPDATE found_items
        SET title=?,description=?,location=?,contact=?,date=?
        WHERE id=?
        """,(title,description,location,contact,date,id))

        conn.commit()
        conn.close()

        return redirect("/view-found")

    cur.execute("SELECT * FROM found_items WHERE id=?",(id,))
    item=cur.fetchone()

    conn.close()

    return render_template("update_found.html",item=item)


if __name__ == "__main__":
    app.run(debug=True)
