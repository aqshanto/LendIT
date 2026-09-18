# Database models for LendIt.
# Three tables only: User, Equipment, Request.

from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# The database object. app.py connects it to the Flask app with db.init_app(app).
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """A student or an admin account.

    UserMixin gives Flask-Login the helpers it needs (is_authenticated, get_id).
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")

    # One user can create many requests.
    requests = db.relationship("Request", backref="user")

    def set_password(self, password):
        """Save the password as a secure hash. Plain passwords are never stored."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Return True if the typed password matches the saved hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Equipment(db.Model):
    """One item in the department equipment catalogue."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Available")

    # One equipment item can have many requests over time.
    requests = db.relationship("Request", backref="equipment")

    def __repr__(self):
        return f"<Equipment {self.name} ({self.status})>"


class Request(db.Model):
    """A student's loan request for one equipment item."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    return_by = db.Column(db.Date, nullable=False)
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pending")

    # The time the request was created, saved in UTC.
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Request {self.id} status={self.status}>"
