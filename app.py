import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this in production

# ===== Database setup =====
DB_PATH = "lost_found.db"
UPLOAD_FOLDER = "static/images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    # Lost items table
    c.execute("""
        CREATE TABLE IF NOT EXISTS lost_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_name TEXT,
            contact TEXT,
            item_name TEXT,
            category TEXT,
            description TEXT,
            date_lost TEXT,
            location TEXT,
            status TEXT,
            image TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    # Found items table
    c.execute("""
        CREATE TABLE IF NOT EXISTS found_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_name TEXT,
            contact TEXT,
            item_name TEXT,
            category TEXT,
            description TEXT,
            date_found TEXT,
            location TEXT,
            status TEXT,
            image TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ===== Routes =====

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = c.fetchone()
        conn.close()
        if user:
            session["user_id"] = user[0]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
            conn.commit()
            flash("Registered successfully! Login now.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists!")
        conn.close()
    return render_template("register.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# ===== Report Lost =====
@app.route("/report_lost", methods=["GET","POST"])
def report_lost():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":
        owner_name = request.form["owner_name"]
        contact = request.form["contact"]
        item_name = request.form["item_name"]
        category = request.form["category"]
        description = request.form["description"]
        date_lost = request.form["date_lost"]
        location = request.form["location"]
        status = request.form["status"]
        image_file = request.files.get("image")
        filename = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        user_id = session["user_id"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO lost_items 
            (owner_name, contact, item_name, category, description, date_lost, location, status, image, user_id)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (owner_name, contact, item_name, category, description, date_lost, location, status, filename, user_id))
        conn.commit()
        conn.close()
        flash("Lost item reported successfully!")
        return redirect(url_for("dashboard"))
    return render_template("report_lost.html")

# ===== Report Found =====
@app.route("/report_found", methods=["GET","POST"])
def report_found():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method=="POST":
        owner_name = request.form["owner_name"]
        contact = request.form["contact"]
        item_name = request.form["item_name"]
        category = request.form["category"]
        description = request.form["description"]
        date_found = request.form["date_found"]
        location = request.form["location"]
        status = request.form["status"]
        image_file = request.files.get("image")
        filename = None
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        user_id = session["user_id"]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO found_items 
            (owner_name, contact, item_name, category, description, date_found, location, status, image, user_id)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (owner_name, contact, item_name, category, description, date_found, location, status, filename, user_id))
        conn.commit()
        conn.close()
        flash("Found item reported successfully!")
        return redirect(url_for("dashboard"))
    return render_template("report_found.html")

# ===== View Lost =====
@app.route("/view_lost")
def view_lost():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM lost_items")
    items = c.fetchall()
    conn.close()
    return render_template("view_lost.html", items=items)

# ===== View Found =====
@app.route("/view_found")
def view_found():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM found_items")
    items = c.fetchall()
    conn.close()
    return render_template("view_found.html", items=items)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ===== Run =====
if __name__=="__main__":
    port = int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0", port=port, debug=True)
