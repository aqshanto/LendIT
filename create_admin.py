# Small helper script that creates an admin account.
# Admins cannot sign up from the website, so run this once from the terminal:
#
#     python create_admin.py

from getpass import getpass

from app import app
from models import db, User


def create_admin():
    """Ask for the admin details and save the account."""
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password (hidden): ")

    if not username or not email or not password:
        print("All fields are required.")
        return

    if len(password) < 6:
        print("Password must be at least 6 characters.")
        return

    if User.query.filter_by(email=email).first():
        print("An account with this email already exists.")
        return

    if User.query.filter_by(username=username).first():
        print("An account with this username already exists.")
        return

    admin = User(username=username, email=email, role="admin")
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()

    print(f"Admin account created: {email}")


if __name__ == "__main__":
    # The database needs an application context to work outside a route.
    with app.app_context():
        create_admin()
