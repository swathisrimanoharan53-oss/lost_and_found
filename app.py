from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("lostfound.db")
    return conn


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
        user = cur.fetchone()

        conn.close()

        if user:
            session["user"] = email
            return redirect("/dashboard")
        else:
            return "Invalid login details"

    return render_template("login.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO users(email,password) VALUES(?,?)",(email,password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html")
    return redirect("/")


# ---------------- REPORT LOST ----------------

@app.route("/add_lost", methods=["GET","POST"])
def add_lost():

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

    return render_template("add_lost.html")


# ---------------- REPORT FOUND ----------------

@app.route("/add_found", methods=["GET","POST"])
def add_found():

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

    return render_template("add_found.html")


# ---------------- VIEW LOST ----------------

@app.route("/view_lost")
def view_lost():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM lost_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_lost.html", items=items)


# ---------------- VIEW FOUND ----------------

@app.route("/view_found")
def view_found():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM found_items")
    items = cur.fetchall()

    conn.close()

    return render_template("view_found.html", items=items)


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
