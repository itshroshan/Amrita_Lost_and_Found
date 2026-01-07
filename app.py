from flask import Flask, render_template, request, redirect, session
import sqlite3 
import smtplib
import random
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv 
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

def send_otp(email, otp):
    print("OTP for", email, "is", otp)
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    subject = "OTP Verification - Lost & Found System"
    body = f"Your OTP for login is: {otp}"
    message = f"Subject: {subject}\n\n{body}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, email, message)
    server.quit()


def valid_student_email(email):
    return email.startswith("bl.") and email.endswith("@bl.students.amrita.edu")


def get_db():
    return sqlite3.connect("database.db")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_user():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT password, role, is_verified FROM users
        WHERE email=?
    """, (email,))
    user = cursor.fetchone()

    if not user:
        return render_template(
            "error.html",
            title="Login Error",
            message="Invalid password. Please try again.",
            redirect_url="/login",
            show_forgot=True
        )

    stored_hash = user[0]
    role = user[1]
    is_verified = user[2]

    #  check hashed password
    if not check_password_hash(stored_hash, password):
        return render_template(
            "error.html",
            title="Login Error",
            message="Invalid password. Please try again.",
            redirect_url="/login",
            show_forgot=True
        )
    
    # Only students need email verification
    if role != "admin" and is_verified == 0:
        return render_template(
            "error.html",
            title="Email Not Verified",
            message="Please verify your email before logging in.",
            redirect_url="/register"
        )

    session["email"] = email
    session["role"] = role

    return redirect("/admin" if role == "admin" else "/student")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_registration_otp():
    if "reg_data" not in session:
        return redirect("/register")

    if request.method == "POST":
        entered_otp = request.form["otp"]
        reg_data = session["reg_data"]

        if entered_otp == reg_data["otp"]:
            conn = get_db()
            cursor = conn.cursor()
            # Check if user already exists
            cursor.execute(
                "SELECT id FROM users WHERE email = ?",
                (reg_data["email"],)
            )
            existing_user = cursor.fetchone()

            if existing_user:
                # if user exists, just update is_verified
                cursor.execute("""
                    UPDATE users
                    SET is_verified = 1
                    WHERE email = ?
                """, (reg_data["email"],))
            else:
                # New user is inserted
                cursor.execute("""
                    INSERT INTO users (name, email, password, role, is_verified)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    reg_data["name"],
                    reg_data["email"],
                    reg_data["password"],
                    "student",
                    1
                ))

            conn.commit()
            session.pop("reg_data", None)

            return redirect("/login")
        else:
            return render_template(
                "error_otp.html",
                title="Verification Failed",
                message="Invalid OTP. Please try again.",
                redirect_url="/register"
            )

    return render_template("verify_otp.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register_user():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    if not valid_student_email(email):
        return render_template(
            "error.html",
            title="Invalid Email",
            message="Please use your official Amrita student email ID.",
            redirect_url="/register"
        )
    # Check if email already exists
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return render_template(
            "error.html",
            title="Already Registered",
            message="This email is already registered. Try logging in.",
            redirect_url="/login"
        )

    otp = str(random.randint(100000, 999999))

    hashed_password = generate_password_hash(password)
    # Store temp registration data in session
    session["reg_data"] = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "otp": otp
    }

    send_otp(email, otp)

    return redirect("/verify-otp")


@app.route("/admin")
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")
    return render_template("admin_dashboard.html")

@app.route("/upload-item")
def upload_item():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")
    return render_template("upload_item.html")


@app.route("/upload-item", methods=["POST"])
def upload_item_post():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    item_name = request.form["item_name"]
    description = request.form["description"]
    location = request.form["location"]
    image = request.files["image"]

    filename = secure_filename(image.filename)
    image_path = os.path.join("static/uploads", filename)
    image.save(image_path)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO found_items (item_name, description, location, image, reported_by)
        VALUES (?, ?, ?, ?, ?)
    """, (item_name, description, location, filename, "Admin"))

    conn.commit()

    return redirect("/admin")

@app.route("/view-items")
def view_items():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM found_items")
    items = cursor.fetchall()

    return render_template("view_items.html", items=items)

@app.route("/delete-item/<int:item_id>")
def delete_item(item_id):
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    # Get image filename first
    cursor.execute("SELECT image FROM found_items WHERE id=?", (item_id,))
    item = cursor.fetchone()

    if item:
        image_file = item[0]
        image_path = os.path.join("static/uploads", image_file)

        # Delete image file if exists
        if os.path.exists(image_path):
            os.remove(image_path)

        # Delete DB record
        cursor.execute("DELETE FROM found_items WHERE id=?", (item_id,))
        conn.commit()

    return redirect("/view-items")

@app.route("/view-lost-items")
def view_lost_items():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lost_items")
    items = cursor.fetchall()

    return render_template("view_lost_items.html", items=items)

@app.route("/delete-lost-item/<int:item_id>")
def delete_lost_item(item_id):
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM lost_items WHERE id=?", (item_id,))
    conn.commit()

    return redirect("/view-lost-items")

@app.route("/claim-item/<int:item_id>")
def claim_item(item_id):
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM found_items WHERE id=?", (item_id,))
    item = cursor.fetchone()

    if not item:
        return redirect("/view-items")

    return render_template("claim_item.html", item_id=item_id)

@app.route("/claim-item/<int:item_id>", methods=["POST"])
def claim_item_post(item_id):
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    student_name = request.form["student_name"]
    reg_no = request.form["registration_number"]

    conn = get_db()
    cursor = conn.cursor()

    # Get item details
    cursor.execute("SELECT item_name, description, location, image FROM found_items WHERE id=?", (item_id,))
    item = cursor.fetchone()

    if not item:
        return redirect("/view-items")

    # Insert into claimed_items
    cursor.execute("""
        INSERT INTO claimed_items
        (item_name, description, location, image, student_name, registration_number)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        item[0], item[1], item[2], item[3],
        student_name, reg_no
    ))

    # Delete from found_items
    cursor.execute("DELETE FROM found_items WHERE id=?", (item_id,))
    conn.commit()

    return redirect("/view-items")

@app.route("/claimed-items")
def claimed_items():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM claimed_items ORDER BY claimed_at DESC")
    items = cursor.fetchall()

    return render_template("claimed_items.html", items=items)

@app.route("/delete-claimed-item/<int:item_id>")
def delete_claimed_item(item_id):
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM claimed_items WHERE id=?", (item_id,))
    conn.commit()

    return redirect("/claimed-items")

@app.route("/student")
def student_dashboard():
    if "role" not in session or session["role"] != "student":
        return redirect("/")
    return render_template("student_dashboard.html")

@app.route("/search")
def search_items():
    if "role" not in session or session["role"] != "student":
        return redirect("/")

    query = request.args.get("query", "").strip()

    conn = get_db()
    cursor = conn.cursor()

    # Always fetch all items
    cursor.execute("SELECT * FROM found_items")
    all_items = cursor.fetchall()

    search_results = []

    if query:
        cursor.execute("""
            SELECT * FROM found_items
            WHERE item_name LIKE ? OR location LIKE ?
        """, (f"%{query}%", f"%{query}%"))
        search_results = cursor.fetchall()

    return render_template(
        "search_items.html",
        query=query,
        search_results=search_results,
        all_items=all_items
    )

@app.route("/report-lost")
def report_lost():
    if "role" not in session or session["role"] != "student":
        return redirect("/")
    return render_template("report_lost.html")


@app.route("/report-lost", methods=["POST"])
def report_lost_post():
    if "role" not in session or session["role"] != "student":
        return redirect("/")

    item_name = request.form["item_name"]
    description = request.form["description"]
    location = request.form["location"]
    student_email = session.get("email")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lost_items (student_email, item_name, description, location)
        VALUES (?, ?, ?, ?)
    """, (student_email, item_name, description, location))

    conn.commit()

    return redirect("/student")

@app.route("/report-found")
def report_found():
    if "role" not in session or session["role"] != "student":
        return redirect("/")
    return render_template("report_found.html")


@app.route("/report-found", methods=["POST"])
def report_found_post():
    if "role" not in session or session["role"] != "student":
        return redirect("/")

    item_name = request.form["item_name"]
    description = request.form["description"]
    location = request.form["location"]
    image = request.files["image"]

    filename = secure_filename(image.filename)
    image.save(os.path.join("static/uploads", filename))

    conn = get_db()
    cursor = conn.cursor()
    student_email = session.get("email")
    cursor.execute("""
        INSERT INTO found_items (item_name, description, location, image, reported_by)
        VALUES (?, ?, ?, ?, ?)
    """, (item_name, description, location, filename, student_email))

    conn.commit()

    return redirect("/student")

@app.route("/change-password")
def change_password():
    if "email" not in session:
        return redirect("/login")

    return render_template("change_password.html", email=session["email"])

@app.route("/change-password", methods=["POST"])
def change_password_post():
    if "email" not in session:
        return redirect("/login")

    email = session["email"]
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    if new_password != confirm_password:
        return render_template(
            "change_password.html",
            email=email,
            error="New passwords do not match"
        )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE email=?",
        (email,)
    )
    user = cursor.fetchone()

    stored_hash = user[0]

    if not check_password_hash(stored_hash, current_password):
        return render_template(
            "change_password.html",
            email=email,
            error="Current password is incorrect"
        )

    # Generate OTP
    otp = str(random.randint(100000, 999999))

    session["pwd_change"] = {
        "email": email,
        "new_password": new_password,
        "otp": otp
    }

    send_otp(email, otp)

    return redirect("/verify-change-password")

@app.route("/verify-change-password", methods=["GET", "POST"])
def verify_change_password():
    if "pwd_change" not in session:
        return redirect("/change-password")

    if request.method == "POST":
        entered_otp = request.form["otp"]
        data = session["pwd_change"]

        if entered_otp != data["otp"]:
            return render_template(
                "verify_change_password.html",
                error="Invalid OTP"
            )

        conn = get_db()
        cursor = conn.cursor()

        new_hashed = generate_password_hash(data["new_password"])
        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (new_hashed, data["email"])
        )
        conn.commit()

        session.pop("pwd_change")

        return render_template(
            "success.html",
            message="Password changed successfully"
        )

    return render_template("verify_change_password.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template(
                "forgot_password.html",
                error="Email not registered"
            )

        otp = str(random.randint(100000, 999999))

        session["forgot_pwd"] = {
            "email": email,
            "otp": otp
        }

        send_otp(email, otp)

        return redirect("/verify-forgot-otp")

    return render_template("forgot_password.html")

@app.route("/verify-forgot-otp", methods=["GET", "POST"])
def verify_forgot_otp():
    if "forgot_pwd" not in session:
        return redirect("/forgot-password")

    if request.method == "POST":
        entered_otp = request.form["otp"]
        data = session["forgot_pwd"]

        if entered_otp != data["otp"]:
            return render_template(
                "verify_forgot_otp.html",
                error="Invalid OTP"
            )

        return redirect("/reset-password")

    return render_template("verify_forgot_otp.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if "forgot_pwd" not in session:
        return redirect("/forgot-password")

    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            return render_template(
                "reset_password.html",
                error="Passwords do not match"
            )

        email = session["forgot_pwd"]["email"]

        conn = get_db()
        cursor = conn.cursor()

        new_hashed = generate_password_hash(new_password)

        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (new_hashed, email)
        )
        conn.commit()

        session.pop("forgot_pwd")

        return render_template(
            "success.html",
            message="Password reset successfully. Please login again."
        )

    return render_template("reset_password.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
