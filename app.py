from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Database connection
def get_db():
    conn = sqlite3.connect("lostfound.db")
    return conn


# Dashboard
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# Report Lost Item
@app.route("/report_lost", methods=["GET","POST"])
def report_lost():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        date = request.form["date"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO lost_items(name,description,location,date) VALUES(?,?,?,?)",
                    (name,description,location,date))

        conn.commit()
        conn.close()

        return redirect("/view_lost")

    return render_template("report_lost.html")


# Report Found Item
@app.route("/add_found", methods=["GET","POST"])
def report_found():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        date = request.form["date"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO found_items(name,description,location,date) VALUES(?,?,?,?)",
                    (name,description,location,date))

        conn.commit()
        conn.close()

        return redirect("/view_found")

    return render_template("report_found.html")


# View Lost Items
@app.route("/view_lost")
def view_lost():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM lost_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_lost.html", items=items)


# View Found Items
@app.route("/view_found")
def view_found():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM found_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_found.html", items=items)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
