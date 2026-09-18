# LendIt: Department Equipment Loan Desk

A Flask web application that replaces the department's paper equipment loan register.

Students can create an account and request equipment. Admins manage the equipment
catalogue and approve or reject loan requests.

---

## Technology

- Python 3
- Flask
- Flask-SQLAlchemy + SQLite
- Flask-Login
- Jinja2 templates
- Bootstrap 5 (CDN)

---

## Setup

1. Create and activate the virtual environment:

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install the packages:

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project folder with a secret key:

   ```
   SECRET_KEY=put-any-long-random-value-here
   ```

   The app will refuse to start without it. The `.env` file is never committed.

4. Run the application:

   ```
   python app.py
   ```

5. Open http://127.0.0.1:5000/ in your browser.

The SQLite database file is created automatically at `instance/lendit.db`.

---

## Accounts

### Student account

Students register themselves on the website at `/signup`.

Every account created through the signup form is given the role `student`.
The role is set in the code, not taken from the form, so nobody can sign up as an admin.

### Admin account

Admins cannot be created from the website. Create one from the terminal:

```
python create_admin.py
```

The script asks for:

- Admin username
- Admin email
- Admin password (typing is hidden)

It saves the account with the role `admin` and a hashed password.

**Then log in at `/login` using the admin email and password you typed.**

There is no default admin username or password in this project, and no password is
written inside the code. If you forget the admin password, create another admin
account with the script.

---

## Routes so far

| URL       | Method    | Purpose                  | Login required |
| --------- | --------- | ------------------------ | -------------- |
| `/`       | GET       | Homepage                 | No             |
| `/signup` | GET, POST | Create a student account | No             |
| `/login`  | GET, POST | Log in                   | No             |
| `/logout` | GET       | Log out                  | Yes            |

---

## Security notes

- Passwords are stored only as hashes (`werkzeug.security`), never as plain text.
- `SECRET_KEY` is loaded from `.env` and is never hardcoded.
- Login errors show one message for a wrong email and a wrong password, so the
  form cannot be used to find out which emails are registered.
- `/logout` is protected with `@login_required`.
