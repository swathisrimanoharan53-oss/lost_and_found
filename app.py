from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Create database
def init_db():
    conn = sqlite3.connect("lostfound.db")
    cursor = conn.cursor()

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

# Login page
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            return redirect("/dashboard")

    return render_template("login.html")


# Dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# Report lost item
@app.route("/report_lost", methods=["GET","POST"])
def report_lost():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        date = request.form["date"]

        conn = sqlite3.connect("lostfound.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO lost_items (name,description,location,date) VALUES (?,?,?,?)",
                       (name,description,location,date))

        conn.commit()
        conn.close()

        return redirect("/view_lost")

    return render_template("report_lost.html")


# Report found item
@app.route("/report_found", methods=["GET","POST"])
def report_found():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        date = request.form["date"]

        conn = sqlite3.connect("lostfound.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO found_items (name,description,location,date) VALUES (?,?,?,?)",
                       (name,description,location,date))

        conn.commit()
        conn.close()

        return redirect("/view_found")

    return render_template("report_found.html")


# View lost items
@app.route("/view_lost")
def view_lost():
    conn = sqlite3.connect("lostfound.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM lost_items")
    data = cursor.fetchall()

    conn.close()

    return render_template("view_lost.html", data=data)


# View found items
@app.route("/view_found")
def view_found():
    conn = sqlite3.connect("lostfound.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM found_items")
    data = cursor.fetchall()

    conn.close()

    return render_template("view_found.html", data=data)


# Logout
@app.route("/logout")
def logout():
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
