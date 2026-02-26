from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import streamlit as st

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Initialize Database
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            login_time TEXT,
            logout_time TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("home.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (username, password, role))
            conn.commit()
        except:
            return "Username already exists!"

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            session["username"] = username
            session["role"] = user[3]

            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO login_history (username, login_time, logout_time)
                VALUES (?, ?, NULL)
            """, (username, login_time))
            conn.commit()

            conn.close()

            if session["role"] == "admin":
                return redirect(url_for("dashboard"))
            else:
                return redirect(url_for("diet_plan"))

        conn.close()
        return "Invalid Credentials"

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "role" in session and session["role"] == "admin":

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, role FROM users")
        users = cursor.fetchall()

        cursor.execute("""
            SELECT username, login_time, logout_time 
            FROM login_history 
            ORDER BY id DESC
        """)
        history = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM login_history")
        total_logins = cursor.fetchone()[0]

        conn.close()

        return render_template("dashboard.html",
                               users=users,
                               history=history,
                               total_logins=total_logins)

    return "Access Denied"

# DELETE USER
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "role" in session and session["role"] == "admin":
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    return "Access Denied"

@app.route("/diet")
def diet_plan():
    if "username" not in session:
        return redirect(url_for("login"))
    # Redirect to Streamlit
    return redirect("http://localhost:8501")
# LOGOUT
@app.route("/logout")
def logout():
    if "username" in session:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE login_history
            SET logout_time=?
            WHERE username=? AND logout_time IS NULL
        """, (logout_time, session["username"]))
        conn.commit()
        conn.close()

    session.clear()
    return redirect(url_for("home"))

# --- This goes at the end ---
if __name__ == "__main__":
    app.run(debug=True)
    
   
   


