# LendIt: Department Equipment Loan Desk

## Development Plan (PLAN.md)

## Project Goal

Build a web application that replaces the department's paper equipment loan register.

Students can view equipment, create accounts, request equipment, and track their requests.

Admins can manage equipment, approve or reject requests, and manage returns.

---

# Project Rules

## Technology Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-Login
- Jinja2 Templates
- Bootstrap 5 CDN

## Development Rules

- Keep the code simple and beginner-friendly.
- Do not add unnecessary libraries.
- Focus on required features first.
- Security and access control are higher priority than UI.

---

# Feature 1: Project Setup

## Goal

Prepare the Flask project environment.

## Tasks

- [ ] Create Flask project structure
- [ ] Create virtual environment
- [ ] Install required packages
- [ ] Configure Flask application
- [ ] Configure SQLite database
- [ ] Configure Bootstrap 5 CDN
- [ ] Create basic templates structure
- [ ] Confirm application runs successfully

## Expected Result

The Flask application starts successfully.

---

# Feature 2: Database Design and Models

## Goal

Create the database structure required for the application.

---

# Database Tables

## Table 1: User

Purpose:
Stores student and admin accounts.

| Column | Data Type | Size | Constraints | Description |
|-|-|-|-|-|
| id | Integer | - | Primary Key, Auto Increment | Unique user ID |
| username | String | 50 characters | Unique, Not Null | User login name |
| email | String | 120 characters | Unique, Not Null | User email address |
| password_hash | String | 255 characters | Not Null | Encrypted password |
| role | String | 20 characters | Not Null, Default: student | User permission level |

---

## Table 2: Equipment

Purpose:
Stores all department equipment.

| Column | Data Type | Size | Constraints | Description |
|-|-|-|-|-|
| id | Integer | - | Primary Key, Auto Increment | Unique equipment ID |
| name | String | 100 characters | Not Null | Equipment name |
| category | String | 50 characters | Not Null | Equipment category |
| description | Text | - | Nullable | Equipment details |
| status | String | 20 characters | Not Null, Default: Available | Available or On loan |

---

## Table 3: Request

Purpose:
Stores equipment loan requests.

| Column | Data Type | Size | Constraints | Description |
|-|-|-|-|-|
| id | Integer | - | Primary Key, Auto Increment | Unique request ID |
| user_id | Integer | - | Foreign Key, Not Null | Student who requested |
| equipment_id | Integer | - | Foreign Key, Not Null | Requested equipment |
| return_by | Date | - | Not Null | Expected return date |
| note | Text | - | Nullable | Optional student note |
| status | String | 20 characters | Not Null, Default: Pending | Request status |
| created_at | DateTime | - | Not Null | Request creation time |

---

# Database Relationships

## User and Request Relationship

One User can create many Requests.

Relationship:
User (1) -------- (Many) Request

Example:

A student can request multiple equipment items.

---

## Equipment and Request Relationship

One Equipment can have many Requests over time.

Relationship:
Equipment (1) -------- (Many) Request

Example:

A camera can be requested many times by different students.

---

# Feature 3: Authentication and User Roles

## Goal

Create account management system.

## Tasks

- [ ] Create signup page
- [ ] Create login page
- [ ] Create logout system
- [ ] Hash passwords using werkzeug.security
- [ ] Add Flask-Login authentication
- [ ] Set default role as student
- [ ] Create admin account method
- [ ] Document admin login in README

## Expected Result

Students and admins can log in with correct permissions.

---

# Feature 4: Public Equipment Catalogue

## Goal

Allow anyone to view available equipment.

## Tasks

- [ ] Create public equipment page
- [ ] Display equipment name
- [ ] Display category
- [ ] Display description
- [ ] Display current status
- [ ] Add search by name
- [ ] Add category filter
- [ ] Hide borrower information

## Expected Result

Logged-out visitors can browse equipment safely.

---

# Feature 5: Student Equipment Request System

## Goal

Allow students to request equipment.

## Tasks

- [ ] Create request form
- [ ] Allow request only for available equipment
- [ ] Add return date validation
- [ ] Add optional note
- [ ] Limit active requests to maximum 2
- [ ] Show clear error message after limit
- [ ] Create My Requests page
- [ ] Show request status:
    - Pending
    - Approved
    - Rejected
    - Returned
    - Cancelled

- [ ] Allow cancellation of own pending requests only

## Expected Result

Students can manage their own requests.

---

# Feature 6: Admin Equipment Management

## Goal

Allow admins to manage equipment.

## Tasks

- [ ] Create admin equipment list
- [ ] Add equipment
- [ ] Edit equipment
- [ ] Delete equipment

Security:

- [ ] Only admins can access these routes

## Expected Result

Admins can maintain equipment records.

---

# Feature 7: Admin Request Management

## Goal

Allow admins to control equipment loans.

## Tasks

- [ ] View pending requests
- [ ] Approve requests
- [ ] Reject requests
- [ ] Mark approved loans as returned

Rules:

- [ ] Approval changes equipment status to On loan
- [ ] Returned equipment changes status to Available
- [ ] Cannot approve already borrowed equipment

## Expected Result

Complete loan workflow works correctly.

---

# Feature 8: Access Control and Security Testing

## Goal

Ensure rules work even through direct URL access.

## Tasks

Test:

- [ ] Student cannot access admin pages
- [ ] Student cannot approve requests
- [ ] Student cannot reject requests
- [ ] Student cannot delete equipment
- [ ] Student cannot cancel another user's request
- [ ] Users cannot view other users' private requests

## Expected Result

Application is secure against URL attacks.

---

# Feature 9: Overdue Management

## Goal

Show overdue equipment to admins.

## Tasks

- [ ] Check approved loans where return date has passed
- [ ] Show Overdue badge
- [ ] Highlight overdue loans in red
- [ ] Returned loans should not count as overdue

## Expected Result

Admins can identify overdue equipment.

---

# Feature 10: Bonus Features (Only After Required Features)

Optional:

- [ ] Admin dashboard counts
    - Total items
    - On loan items
    - Overdue items
    - Pending requests

- [ ] Request history per item
- [ ] Item photo upload
- [ ] CSV export of current loans

---

# Final Testing

## Application Testing

- [ ] Signup works
- [ ] Login works
- [ ] Logout works
- [ ] Equipment catalogue works
- [ ] Search works
- [ ] Category filter works
- [ ] Student request works
- [ ] Request limit works
- [ ] Cancel request works
- [ ] Admin approval works
- [ ] Admin rejection works
- [ ] Return process works
- [ ] Overdue detection works

---

## Security Testing

- [ ] Student cannot access admin URLs
- [ ] Student cannot modify other users' requests
- [ ] Student cannot delete equipment
- [ ] Direct URL attacks blocked
- [ ] Permissions checked on backend

---

## Documentation Testing

- [ ] README.md completed
- [ ] PLAN.md completed
- [ ] mistakes.md updated
- [ ] Admin login details added
- [ ] AI tools usage documented

---

# Project Completion

Status:

- [ ] All required features completed
- [ ] Security tested
- [ ] Ready for GitHub submission
