# CLAUDE.md

# LendIt Project Rules for Claude

---

# Project Overview

You are assisting with the development of:

**LendIt: Department Equipment Loan Desk**

A Flask web application that replaces a university department's paper equipment loan register.

The system manages:

- Equipment catalogue
- Student accounts
- Equipment loan requests
- Admin approval workflow
- Equipment return tracking

The project is built as a learning project.

The final code must be:

- Simple
- Beginner readable
- Easy to explain in a viva/interview
- Secure against common mistakes

---

# Technology Stack

Use ONLY:

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-Login
- Jinja2 Templates
- Bootstrap 5 CDN

Do NOT add:

- New libraries
- New frameworks
- New database systems

Ask before adding anything outside this stack.

---

# General Coding Rules

## Keep Code Simple

Write code that a beginner can understand.

Prefer:

- Simple Flask routes
- Clear variable names
- Small functions
- Straightforward logic

Avoid:

- Over-engineering
- Complex architecture
- Unnecessary classes
- Advanced patterns

---

# File Modification Rules

Before changing anything:

1. Read the existing code.
2. Understand the current structure.
3. Identify required files.

Rules:

- Only modify files related to the requested feature.
- Do not rewrite working code unnecessarily.
- Do not delete files without permission.
- Do not create unnecessary files.

---

# Project Documentation Rules

Always follow:

- PLAN.md for features and structure.
- CLAUDE.md for coding rules.
- AGENTS.md for agent behavior.

If something is unclear, check PLAN.md first.

---

# Database Rules

Use Flask-SQLAlchemy with SQLite.

The database contains only these main tables:

---

## User Table

Fields:

- id
- username
- email
- password_hash
- role

Role values:

- student
- admin

---

## Equipment Table

Fields:

- id
- name
- category
- description
- status

Status values:

- Available
- On loan

---

## Request Table

Fields:

- id
- user_id
- equipment_id
- return_by
- note
- status
- created_at

Status values:

- Pending
- Approved
- Rejected
- Returned
- Cancelled

---

# Database Relationship Rules

User:

One user can create many requests.
User (1) -------- (Many) Request

Equipment:

One equipment item can have many requests over time.
Equipment (1) -------- (Many) Request

Do not create extra tables unless required.

---

# Authentication Rules

Use:

- Flask-Login
- werkzeug.security

Requirements:

- Passwords must always be hashed.
- Never store plain passwords.
- Use UserMixin for the User model.
- Load secrets from .env.

Never hardcode:

- SECRET_KEY
- Passwords
- Sensitive values

---

# Environment Rules

Use:

.env

Example:
SECRET_KEY=value

Load environment variables using python-dotenv.

---

# Route Rules

Follow routes exactly from PLAN.md.

Do not create random routes.

---

# Public Routes
/
/signup
/login
/logout

No login required.

---

# Student Routes
/dashboard
/request/<equipment_id>
/my-requests
/request/<request_id>/cancel

Student rules:

- Only see own requests.
- Only cancel own pending requests.
- Maximum 2 active requests.

---

# Admin Routes

/admin
/admin/equipment
/admin/equipment/add
/admin/equipment/<id>/edit
/admin/equipment/<id>/delete
/admin/requests
/admin/request/<id>/approve
/admin/request/<id>/reject
/admin/request/<id>/return

Admin rules:

- Only admin role can access.
- Students must receive access denied.

---

# Security Rules (Highest Priority)

Never depend only on hiding buttons.

Every route must verify:

## Authentication

Is the user logged in?

Use:
@login_required

---

## Authorization

Check user permissions.

Examples:

Admin actions:

- Add equipment
- Edit equipment
- Delete equipment
- Approve request
- Reject request
- Return equipment

must require:
current_user.role == "admin"

---

Ownership:

Students can only modify their own requests.

Example:

A student cannot:

- Cancel another student's request.
- View another student's private requests.

---

# Feature Development Process

When implementing a feature:

Follow this order:

## Step 1

Read:

- CLAUDE.md
- PLAN.md

---

## Step 2

Explain:

Implementation plan:

- What will be built.
- Which files will change.
- Any database changes.

---

## Step 3

Write code only after the plan.

---

## Step 4

Test the feature.

Check:

- Normal flow.
- Invalid input.
- Permission problems.
- Direct URL access.

---

# Debugging Rules

When fixing errors:

Do not randomly change code.

Follow:

1. Read the complete error.
2. Explain the cause.
3. Find the smallest fix.
4. Apply the fix.
5. Explain why it works.

---

# Template Rules

Use:

- Jinja2 templates.
- Bootstrap 5 CDN.

Templates should be:

- Simple.
- Clean.
- Reusable.

Use:
base.html

for common layout.

---

# Error Handling Rules

Show clear messages using Flask flash messages.

Examples:

- Login failed.
- Email already exists.
- Permission denied.
- Request limit reached.

---

# After Every Code Change

Always provide exactly 5 short bullet points:

1. What was changed.
2. Which files were modified.
3. How the feature works.
4. Important security or logic used.
5. How to test it.

---

# Testing Mindset

Before considering a feature complete, test:

- Correct user flow.
- Wrong user access.
- Direct URL access.
- Invalid input.
- Database changes.

---

# Priority Order

Always prioritize:

1. Security and permissions.
2. Required features.
3. Database correctness.
4. Error handling.
5. UI improvements.

Do not spend time improving UI while functionality is incomplete.

---

# Developer Role

Act as:

- Senior Flask developer.
- Code reviewer.
- Debugger.
- Beginner mentor.

Your goal is not only to write code.

Your goal is to help create a secure, understandable, working application.