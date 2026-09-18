# LendIt: Department Equipment Loan Desk
# Main Flask application file.

import os
from datetime import date, datetime

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from models import db, Equipment, Request, User

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
    """Public equipment catalogue. Anyone can open it, even without logging in.

    Only the Equipment table is read here. Requests and users are never touched,
    so the page cannot show who borrowed an item.
    """
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    # Start with all equipment, then narrow it down.
    equipment_query = Equipment.query

    if search:
        # ilike means "contains, ignoring capital letters".
        equipment_query = equipment_query.filter(Equipment.name.ilike(f"%{search}%"))

    if category:
        equipment_query = equipment_query.filter(Equipment.category == category)

    equipment_list = equipment_query.order_by(Equipment.name).all()

    # Every category that exists, used to fill the filter dropdown.
    category_rows = (
        db.session.query(Equipment.category)
        .distinct()
        .order_by(Equipment.category)
        .all()
    )
    categories = [row[0] for row in category_rows]

    return render_template(
        "index.html",
        equipment_list=equipment_list,
        categories=categories,
        search=search,
        selected_category=category,
    )


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


# A request still using up a student's limit.
ACTIVE_STATUSES = ["Pending", "Approved"]


def count_active_requests(user_id):
    """How many requests of this user are still Pending or Approved."""
    return Request.query.filter(
        Request.user_id == user_id,
        Request.status.in_(ACTIVE_STATUSES),
    ).count()


@app.route("/dashboard")
@login_required
def dashboard():
    """Student dashboard with a short summary."""
    if current_user.role != "student":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    active_count = count_active_requests(current_user.id)
    total_count = Request.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "dashboard.html",
        active_count=active_count,
        total_count=total_count,
        slots_left=2 - active_count,
    )


@app.route("/request/<int:equipment_id>", methods=["GET", "POST"])
@login_required
def request_equipment(equipment_id):
    """Request one equipment item."""
    if current_user.role != "student":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    item = db.session.get(Equipment, equipment_id)
    if item is None:
        abort(404)

    if item.status != "Available":
        flash("Equipment is currently unavailable.", "warning")
        return redirect(url_for("home"))

    # The limit is checked here and again below, so it also blocks a
    # student who opens the form in two tabs.
    if count_active_requests(current_user.id) >= 2:
        flash("You cannot request more than 2 active items.", "warning")
        return redirect(url_for("my_requests"))

    # One active request per item is enough.
    already_requested = Request.query.filter(
        Request.user_id == current_user.id,
        Request.equipment_id == item.id,
        Request.status.in_(ACTIVE_STATUSES),
    ).first()
    if already_requested:
        flash("You already have an active request for this item.", "warning")
        return redirect(url_for("my_requests"))

    if request.method == "POST":
        return_by_text = request.form.get("return_by", "").strip()
        note = request.form.get("note", "").strip()

        if not return_by_text:
            flash("Please choose a return date.", "danger")
            return render_template("request_form.html", item=item, today=date.today())

        # The date arrives as text like 2026-12-01 and must be a real date.
        try:
            return_by = datetime.strptime(return_by_text, "%Y-%m-%d").date()
        except ValueError:
            flash("Please enter a valid return date.", "danger")
            return render_template("request_form.html", item=item, today=date.today())

        if return_by <= date.today():
            flash("Return date must be in the future.", "danger")
            return render_template("request_form.html", item=item, today=date.today())

        new_request = Request(
            user_id=current_user.id,
            equipment_id=item.id,
            return_by=return_by,
            note=note or None,
            status="Pending",
        )
        db.session.add(new_request)
        db.session.commit()

        # The equipment stays Available until an admin approves the request.
        flash("Request sent. Please wait for admin approval.", "success")
        return redirect(url_for("my_requests"))

    return render_template("request_form.html", item=item, today=date.today())


@app.route("/my-requests")
@login_required
def my_requests():
    """Show only the requests of the logged in student."""
    if current_user.role != "student":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    # Filtering by current_user.id means other students' requests
    # are never loaded from the database.
    my_request_list = (
        Request.query.filter_by(user_id=current_user.id)
        .order_by(Request.created_at.desc())
        .all()
    )

    return render_template("my_requests.html", my_request_list=my_request_list)


@app.route("/request/<int:request_id>/cancel", methods=["POST"])
@login_required
def cancel_request(request_id):
    """Cancel one of your own pending requests."""
    if current_user.role != "student":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    loan_request = db.session.get(Request, request_id)
    if loan_request is None:
        abort(404)

    # Ownership check: you may only touch your own request.
    if loan_request.user_id != current_user.id:
        flash("Permission denied.", "danger")
        return redirect(url_for("my_requests"))

    if loan_request.status != "Pending":
        flash("Only pending requests can be cancelled.", "warning")
        return redirect(url_for("my_requests"))

    loan_request.status = "Cancelled"
    db.session.commit()

    flash("Request cancelled.", "success")
    return redirect(url_for("my_requests"))


if __name__ == "__main__":
    app.run(debug=True)
