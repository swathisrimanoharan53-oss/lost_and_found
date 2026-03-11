from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# -------------------- DATABASE SETUP --------------------

def init_db():
    conn = sqlite3.connect("lostfound.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lost_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        location TEXT,
        date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        location TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------- LOGIN --------------------

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("lostfound.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect("/dashboard")

    return render_template("login.html")


# -------------------- REGISTER --------------------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("lostfound.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# -------------------- DASHBOARD --------------------

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# -------------------- REPORT LOST ITEM --------------------

@app.route("/report_lost", methods=["GET","POST"])
def report_lost():

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        date = request.form["date"]

        conn = sqlite3.connect("lostfound.db")
        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO lost_items (name,description,location,date) VALUES (?,?,?,?)",
        (name,description,location,date)
        )

        conn.commit()
        conn.close()

        return redirect("/view_lost")

    return render_template("report_lost.html")


# -------------------- REPORT FOUND ITEM --------------------

@app.route("/report_found", methods=["GET","POST"])
def report_found():

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        date = request.form["date"]

        conn = sqlite3.connect("lostfound.db")
        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO found_items (name,description,location,date) VALUES (?,?,?,?)",
        (name,description,location,date)
        )

        conn.commit()
        conn.close()

        return redirect("/view_found")

    return render_template("report_found.html")


# -------------------- VIEW LOST ITEMS --------------------

@app.route("/view_lost")
def view_lost():

    conn = sqlite3.connect("lostfound.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM lost_items")
    data = cursor.fetchall()

    conn.close()

    return render_template("view_lost.html", data=data)


# -------------------- VIEW FOUND ITEMS --------------------

@app.route("/view_found")
def view_found():

    conn = sqlite3.connect("lostfound.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM found_items")
    data = cursor.fetchall()

    conn.close()

    return render_template("view_found.html", data=data)


# -------------------- LOGOUT --------------------

@app.route("/logout")
def logout():
    return redirect("/")


# -------------------- RUN APP --------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
