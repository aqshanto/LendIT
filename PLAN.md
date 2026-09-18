# LendIt: Department Equipment Loan Desk

## Project Development Plan

---

# Project Goal

Build a Flask web application that replaces the department's paper equipment loan register.

The system allows:

- Public visitors to view available equipment.
- Students to create accounts and request equipment.
- Admins to manage equipment and approve/reject loan requests.

The application must focus on:

1. Required features working correctly.
2. Backend security and access control.
3. Simple code that can be explained easily.

---

# Technology Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-Login
- Jinja2 Templates
- Bootstrap 5 CDN

---

# Development Rules

- Keep the project beginner-friendly.
- Do not add unnecessary libraries.
- Complete required features before bonus features.
- Every permission rule must work even when users manually type URLs.
- Do not rely only on hidden buttons for security.

---

# Database Design

## Table 1: User

Purpose:

Stores student and admin accounts.

| Column        | Type    | Size | Constraints                 | Description             |
| ------------- | ------- | ---- | --------------------------- | ----------------------- |
| id            | Integer | -    | Primary Key, Auto Increment | Unique user ID          |
| username      | String  | 50   | Unique, Not Null            | User display/login name |
| email         | String  | 120  | Unique, Not Null            | User email              |
| password_hash | String  | 255  | Not Null                    | Hashed password         |
| role          | String  | 20   | Not Null, Default: student  | student or admin        |

---

## Table 2: Equipment

Purpose:

Stores department equipment information.

| Column      | Type    | Size | Constraints                  | Description          |
| ----------- | ------- | ---- | ---------------------------- | -------------------- |
| id          | Integer | -    | Primary Key, Auto Increment  | Equipment ID         |
| name        | String  | 100  | Not Null                     | Equipment name       |
| category    | String  | 50   | Not Null                     | Equipment category   |
| description | Text    | -    | Nullable                     | Equipment details    |
| status      | String  | 20   | Not Null, Default: Available | Available or On loan |

---

## Table 3: Request

Purpose:

Stores equipment loan requests.

| Column       | Type     | Size | Constraints                 | Description           |
| ------------ | -------- | ---- | --------------------------- | --------------------- |
| id           | Integer  | -    | Primary Key, Auto Increment | Request ID            |
| user_id      | Integer  | -    | Foreign Key, Not Null       | Student who requested |
| equipment_id | Integer  | -    | Foreign Key, Not Null       | Requested equipment   |
| return_by    | Date     | -    | Not Null                    | Expected return date  |
| note         | Text     | -    | Nullable                    | Optional student note |
| status       | String   | 20   | Not Null, Default: Pending  | Request status        |
| created_at   | DateTime | -    | Not Null                    | Request creation date |

---

# Database Relationships

## User and Request

Relationship:
User (1) -------- (Many) Request

Explanation:

One user can create multiple equipment requests.

---

## Equipment and Request

Relationship:
Equipment (1) -------- (Many) Request

Explanation:

One equipment item can have many requests over time.

---

# Application Routes

---

# Public Routes

| URL       | Method    | Purpose                    | Login Required |
| --------- | --------- | -------------------------- | -------------- |
| `/`       | GET       | Public equipment catalogue | No             |
| `/signup` | GET, POST | Create account             | No             |
| `/login`  | GET, POST | Login user                 | No             |
| `/logout` | GET       | Logout user                | Yes            |

---

# Student Routes

| URL                            | Method    | Purpose                    | Login Required |
| ------------------------------ | --------- | -------------------------- | -------------- |
| `/dashboard`                   | GET       | Student dashboard          | Yes            |
| `/request/<equipment_id>`      | GET, POST | Request equipment          | Yes            |
| `/my-requests`                 | GET       | View own requests          | Yes            |
| `/request/<request_id>/cancel` | POST      | Cancel own pending request | Yes            |

Rules:

- Student can only view own requests.
- Student can only cancel own pending requests.
- Maximum 2 active requests allowed.
- Return date must be future.

---

# Admin Routes

| URL                            | Method    | Purpose                   | Login Required |
| ------------------------------ | --------- | ------------------------- | -------------- |
| `/admin`                       | GET       | Admin dashboard           | Yes            |
| `/admin/equipment`             | GET       | Equipment management page | Yes            |
| `/admin/equipment/add`         | GET, POST | Add equipment             | Yes            |
| `/admin/equipment/<id>/edit`   | GET, POST | Edit equipment            | Yes            |
| `/admin/equipment/<id>/delete` | POST      | Delete equipment          | Yes            |
| `/admin/requests`              | GET       | View loan requests        | Yes            |
| `/admin/request/<id>/approve`  | POST      | Approve request           | Yes            |
| `/admin/request/<id>/reject`   | POST      | Reject request            | Yes            |
| `/admin/request/<id>/return`   | POST      | Mark returned             | Yes            |

Rules:

- Only admin users can access admin routes.
- Cannot approve equipment already on loan.
- Returning equipment changes status to Available.

---

# Feature 1: Project Setup

## Tasks

- [ ] Create Flask project structure
- [ ] Setup virtual environment
- [ ] Install required packages
- [ ] Create requirements.txt
- [ ] Configure Flask application
- [ ] Configure SQLite
- [ ] Add Bootstrap CDN
- [ ] Confirm application runs

---

# Feature 2: Database Models

## Tasks

- [ ] Create User model
- [ ] Create Equipment model
- [ ] Create Request model
- [ ] Add relationships
- [ ] Create database tables

Expected Result:

Database structure works correctly.

---

# Feature 3: Authentication and Roles

## Tasks

- [ ] Signup system
- [ ] Login system
- [ ] Logout system
- [ ] Flask-Login setup
- [ ] Password hashing
- [ ] Student default role
- [ ] Admin creation method
- [ ] README admin login documentation

Expected Result:

Users can login with correct permissions.

---

# Feature 4: Public Equipment Catalogue

## Tasks

- [ ] Create equipment listing page
- [ ] Show name
- [ ] Show category
- [ ] Show description
- [ ] Show availability status
- [ ] Search by name
- [ ] Filter by category
- [ ] Hide borrower information

---

# Feature 5: Student Request System

## Tasks

- [ ] Request available equipment
- [ ] Add return-by date
- [ ] Validate future date
- [ ] Add optional note
- [ ] Limit active requests to 2
- [ ] Create My Requests page
- [ ] Show request statuses
- [ ] Cancel own pending request

Statuses:

- Pending
- Approved
- Rejected
- Returned
- Cancelled

---

# Feature 6: Admin Equipment Management

## Tasks

- [ ] View equipment
- [ ] Add equipment
- [ ] Edit equipment
- [ ] Delete equipment

Security:

- [ ] Only admin can perform actions

---

# Feature 7: Admin Request Management

## Tasks

- [ ] View pending requests
- [ ] Approve requests
- [ ] Reject requests
- [ ] Mark returned

Rules:

- [ ] Approval changes equipment status to On loan
- [ ] Return changes status to Available
- [ ] Cannot approve unavailable equipment

---

# Feature 8: Security Testing

## Test:

- [ ] Student cannot access admin pages
- [ ] Student cannot approve requests
- [ ] Student cannot delete equipment
- [ ] Student cannot cancel another user's request
- [ ] Direct URL attacks blocked
- [ ] Ownership checks work

---

# Feature 9: Overdue System

## Tasks

- [ ] Detect approved loans past return date
- [ ] Show Overdue badge
- [ ] Highlight overdue loans
- [ ] Returned loans are not overdue

---

# Feature 10: Bonus Features

Only after all required features work.

- [ ] Admin dashboard counts
- [ ] Request history per item
- [ ] Item photo upload
- [ ] CSV export

---

# Final Testing

## Features

- [ ] Signup works
- [ ] Login works
- [ ] Logout works
- [ ] Catalogue works
- [ ] Search works
- [ ] Category filter works
- [ ] Request system works
- [ ] Request limit works
- [ ] Cancellation works
- [ ] Admin approval works
- [ ] Return system works
- [ ] Overdue system works

---

## Security

- [ ] Authentication protection works
- [ ] Role protection works
- [ ] Ownership protection works
- [ ] Direct URL testing completed

---

## Documentation

- [ ] README.md completed
- [ ] PLAN.md completed
- [ ] mistakes.md updated
- [ ] AI usage documented

---

# Project Completion

- [ ] All required features completed
- [ ] Tested successfully
- [ ] Ready for GitHub submission
