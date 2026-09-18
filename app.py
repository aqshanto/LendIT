# LendIt: Department Equipment Loan Desk
# Main Flask application file.

import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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

# Database object. The models (User, Equipment, Request) come in Feature 2.
db = SQLAlchemy(app)


@app.route("/")
def home():
    """Public homepage. For now it only shows a project running message."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
