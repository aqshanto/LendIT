# LendIt: Department Equipment Loan Desk
# Main Flask application file.

import os
import secrets
from datetime import date, datetime

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
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

# Cookie safety.
# HTTPONLY: JavaScript cannot read the login cookie.
# SAMESITE: the browser does not send the cookie when another website
# posts a form to us, which blocks cross site request forgery (CSRF).
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

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


def csrf_token():
    """Give this browser session one secret token, and reuse it."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


# Templates can call csrf_token() inside any form.
app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def check_csrf_token():
    """Reject any POST that does not carry this session's token.

    Another website can make your browser send a POST, but it cannot read
    your token, so its POST is rejected before any route runs.
    """
    if request.method == "POST":
        form_token = request.form.get("csrf_token", "")
        real_token = session.get("csrf_token", "")
        if not real_token or not secrets.compare_digest(form_token, real_token):
            abort(400)


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


def check_equipment_fields(name, category):
    """Return an error message for the equipment form, or None if it is fine."""
    if not name or not category:
        return "Name and category are required."
    if len(name) > 100:
        return "Name must be 100 characters or fewer."
    if len(category) > 50:
        return "Category must be 50 characters or fewer."
    return None


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


@app.route("/admin/equipment")
@login_required
def admin_equipment():
    """Equipment management page. Admin only."""
    if current_user.role != "admin":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    equipment_list = Equipment.query.order_by(Equipment.name).all()
    return render_template("admin_equipment.html", equipment_list=equipment_list)


@app.route("/admin/equipment/add", methods=["GET", "POST"])
@login_required
def admin_equipment_add():
    """Add a new equipment item. Admin only."""
    if current_user.role != "admin":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()

        error = check_equipment_fields(name, category)
        if error:
            flash(error, "danger")
            return render_template(
                "admin_equipment_form.html",
                heading="Add Equipment",
                form_action=url_for("admin_equipment_add"),
                name=name,
                category=category,
                description=description,
            )

        # New equipment always starts as Available.
        new_item = Equipment(
            name=name,
            category=category,
            description=description or None,
            status="Available",
        )
        db.session.add(new_item)
        db.session.commit()

        flash("Equipment added.", "success")
        return redirect(url_for("admin_equipment"))

    return render_template(
        "admin_equipment_form.html",
        heading="Add Equipment",
        form_action=url_for("admin_equipment_add"),
        name="",
        category="",
        description="",
    )


@app.route("/admin/equipment/<int:equipment_id>/edit", methods=["GET", "POST"])
@login_required
def admin_equipment_edit(equipment_id):
    """Edit one equipment item. Admin only."""
    if current_user.role != "admin":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    item = db.session.get(Equipment, equipment_id)
    if item is None:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()

        error = check_equipment_fields(name, category)
        if error:
            flash(error, "danger")
            return render_template(
                "admin_equipment_form.html",
                heading="Edit Equipment",
                form_action=url_for("admin_equipment_edit", equipment_id=item.id),
                name=name,
                category=category,
                description=description,
            )

        # The status is not edited here. Feature 7 changes it
        # when a request is approved or returned.
        item.name = name
        item.category = category
        item.description = description or None
        db.session.commit()

        flash("Equipment updated.", "success")
        return redirect(url_for("admin_equipment"))

    return render_template(
        "admin_equipment_form.html",
        heading="Edit Equipment",
        form_action=url_for("admin_equipment_edit", equipment_id=item.id),
        name=item.name,
        category=item.category,
        description=item.description or "",
    )


@app.route("/admin/equipment/<int:equipment_id>/delete", methods=["POST"])
@login_required
def admin_equipment_delete(equipment_id):
    """Delete one equipment item. Admin only."""
    if current_user.role != "admin":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    item = db.session.get(Equipment, equipment_id)
    if item is None:
        abort(404)

    # Requests point at this equipment. Deleting it would break the
    # loan history, so it is not allowed while requests exist.
    request_count = Request.query.filter_by(equipment_id=item.id).count()
    if request_count > 0:
        flash("Cannot delete this equipment because it has loan requests.", "warning")
        return redirect(url_for("admin_equipment"))

    db.session.delete(item)
    db.session.commit()

    flash("Equipment deleted.", "success")
    return redirect(url_for("admin_equipment"))


@app.route("/admin/requests")
@login_required
def admin_requests():
    """Show every loan request. Admin only."""
    if current_user.role != "admin":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    request_list = Request.query.order_by(Request.created_at.desc()).all()
    return render_template("admin_requests.html", request_list=request_list)


@app.route("/admin/request/<int:request_id>/approve", methods=["POST"])
@login_required
def admin_request_approve(request_id):
    """Approve a pending request and mark the equipment as On loan."""
    if current_user.role != "admin":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    loan_request = db.session.get(Request, request_id)
    if loan_request is None:
        abort(404)

    if loan_request.status != "Pending":
        flash("Only pending requests can be approved.", "warning")
        return redirect(url_for("admin_requests"))

    item = loan_request.equipment

    # The item must be free. This is what stops two students
    # being approved for the same equipment.
    if item.status != "Available":
        flash("Equipment is currently unavailable.", "warning")
        return redirect(url_for("admin_requests"))

    loan_request.status = "Approved"
    item.status = "On loan"
    db.session.commit()

    flash("Request approved.", "success")
    return redirect(url_for("admin_requests"))


@app.route("/admin/request/<int:request_id>/reject", methods=["POST"])
@login_required
def admin_request_reject(request_id):
    """Reject a pending request. The equipment is not changed."""
    if current_user.role != "admin":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    loan_request = db.session.get(Request, request_id)
    if loan_request is None:
        abort(404)

    if loan_request.status != "Pending":
        flash("Only pending requests can be rejected.", "warning")
        return redirect(url_for("admin_requests"))

    loan_request.status = "Rejected"
    db.session.commit()

    flash("Request rejected.", "success")
    return redirect(url_for("admin_requests"))


@app.route("/admin/request/<int:request_id>/return", methods=["POST"])
@login_required
def admin_request_return(request_id):
    """Mark an approved loan as returned and free the equipment."""
    if current_user.role != "admin":
        flash("Permission denied.", "danger")
        return redirect(url_for("home"))

    loan_request = db.session.get(Request, request_id)
    if loan_request is None:
        abort(404)

    # Only equipment that is really on loan can come back.
    if loan_request.status != "Approved":
        flash("Only approved requests can be returned.", "warning")
        return redirect(url_for("admin_requests"))

    loan_request.status = "Returned"
    loan_request.equipment.status = "Available"
    db.session.commit()

    flash("Equipment marked as returned.", "success")
    return redirect(url_for("admin_requests"))


if __name__ == "__main__":
    app.run(debug=True)
