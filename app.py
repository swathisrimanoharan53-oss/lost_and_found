from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "lostfoundsecret"

# Upload folder
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- MONGODB CONNECTION ----------------
client = MongoClient(os.environ.get("MONGO_URI"))
db = client["LostFoundProject"]

users_collection = db["users"]
lost_collection = db["lost_items"]
found_collection = db["found_items"]


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({
            "username": username,
            "password": password
        })

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = users_collection.find_one({"username": username})

        if existing_user:
            flash("Username already exists. Please login.")
            return redirect(url_for("login"))

        users_collection.insert_one({
            "username": username,
            "password": password
        })

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- REPORT LOST ----------------
@app.route("/report_lost", methods=["GET", "POST"])
def report_lost():
    if request.method == "POST":
        owner = request.form["owner_name"]
        contact = request.form["contact"]
        item = request.form["item_name"]
        category = request.form["category"]
        desc = request.form["description"]
        date = request.form["date_lost"]
        location = request.form["location"]
        status = request.form["status"]

        filename = ""

        if "image" in request.files:
            image_file = request.files["image"]
            if image_file.filename != "":
                filename = image_file.filename
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image_file.save(filepath)

        lost_collection.insert_one({
            "owner": owner,
            "contact": contact,
            "item_name": item,
            "category": category,
            "description": desc,
            "date": date,
            "location": location,
            "status": status,
            "image": filename
        })

        flash("Lost item reported successfully")
        return redirect(url_for("view_lost"))

    return render_template("report_lost.html")


# ---------------- REPORT FOUND ----------------
@app.route("/report_found", methods=["GET", "POST"])
def report_found():
    if request.method == "POST":
        owner = request.form["owner_name"]
        contact = request.form["contact"]
        item = request.form["item_name"]
        category = request.form["category"]
        desc = request.form["description"]
        date = request.form["date_found"]
        location = request.form["location"]
        status = request.form["status"]

        filename = ""

        if "image" in request.files:
            image_file = request.files["image"]
            if image_file.filename != "":
                filename = image_file.filename
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image_file.save(filepath)

        found_collection.insert_one({
            "owner": owner,
            "contact": contact,
            "item_name": item,
            "category": category,
            "description": desc,
            "date": date,
            "location": location,
            "status": status,
            "image": filename
        })

        flash("Found item reported successfully")
        return redirect(url_for("view_found"))

    return render_template("report_found.html")


# ---------------- VIEW LOST ----------------
@app.route("/view_lost")
def view_lost():
    items = list(lost_collection.find())
    return render_template("view_lost.html", items=items)


# ---------------- VIEW FOUND ----------------
@app.route("/view_found")
def view_found():
    items = list(found_collection.find())
    return render_template("view_found.html", items=items)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
