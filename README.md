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
- Every private page uses `@login_required`, and every admin action also checks
  `current_user.role == "admin"` inside the route. Hiding a button is never the
  protection: typing the URL directly is blocked too.
- Students can only see and cancel their own requests. Ownership is checked in
  the route by comparing the request's `user_id` with the logged in user.
- All actions that change data (approve, reject, return, delete, cancel) are
  POST only. Opening those URLs in the browser gives "405 Method Not Allowed".
- Every form carries a CSRF token from the session. A POST without the correct
  token is rejected with "400 Bad Request", so another website cannot submit
  forms using your login.
- The session cookie is HttpOnly and SameSite=Lax.

### Before putting this on a real server

`python app.py` runs Flask in debug mode, which exposes the Werkzeug debug
console at `/console`. That is fine on your own computer, but debug mode must
be turned off before the app is reachable by anyone else.
