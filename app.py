# LendIt: Department Equipment Loan Desk
# Main Flask application file.

import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from models import db, User

# Read values from the .env file (SECRET_KEY, etc.)
load_dotenv()

app = Flask(__name__)

# The secret key is loaded from .env, never written inside the code.
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("SECRET_KEY is missing. Add SECRET_KEY=... to your .env file.")

# SQLite database file. It will be created inside the instance folder.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lendit.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connect the database object from models.py to this Flask app.
db.init_app(app)

# Create the tables the first time the app starts.
with app.app_context():
    db.create_all()

# Flask-Login remembers which user is logged in.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in first."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login calls this to load the logged in user from the database."""
    return db.session.get(User, int(user_id))


@app.route("/")
def home():
    """Public homepage. For now it only shows a project running message."""
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Create a new student account."""
    # A logged in user does not need the signup page.
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("signup.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("signup.html")

        if password != confirm_password:
            flash("The two passwords do not match.", "danger")
            return render_template("signup.html")

        if User.query.filter_by(email=email).first():
            flash("Email already exists.", "danger")
            return render_template("signup.html")

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return render_template("signup.html")

        # The role is always student here. It is never read from the form,
        # so nobody can sign up as an admin.
        new_user = User(username=username, email=email, role="student")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log a user in with email and password."""
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        # One message for both mistakes, so nobody can find out
        # which emails have an account.
        if user is None or not user.check_password(password):
            flash("Login failed. Check your email and password.", "danger")
            return render_template("login.html")

        login_user(user)
        flash(f"Welcome back, {user.username}.", "success")
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log the current user out."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
