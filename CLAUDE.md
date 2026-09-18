# LendIt Project Rules for Claude

## Project Overview

You are helping build:

**LendIt: Department Equipment Loan Desk**

A small Flask web application that replaces a university department's paper equipment loan register.

The application allows:

- Public users to view equipment catalogue
- Students to create accounts and request equipment
- Admins to manage equipment and approve/reject requests
- Students and admins to have different permissions

This is a learning project. The code must remain simple and easy for a beginner to understand.

---

# Technology Stack

Use only:

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite
- Flask-Login
- Jinja2 Templates
- Bootstrap 5 via CDN

Do not add any new library, package, or framework without asking first.

---

# Coding Style Rules

## Keep Code Beginner Friendly

- Write simple readable code.
- Avoid unnecessary advanced patterns.
- Avoid complex architecture.
- Use clear variable names.
- Add short comments only where needed.
- Do not over-engineer.

The final code should be explainable in a viva/interview.

---

# File Modification Rules

Before making changes:

1. Understand the existing project structure.
2. Only modify files directly related to the requested feature.
3. Do not rewrite unrelated files.
4. Do not create unnecessary files.

If a change requires modifying additional files, explain why first.

---

# Security Rules (Very Important)

Security is a priority.

Always enforce rules on the backend, not only by hiding buttons.

Never trust:

- URLs
- Form submissions
- User input

Always check permissions.

Examples:

- Students cannot access admin routes.
- Students cannot approve requests.
- Students cannot delete equipment.
- Students cannot cancel another student's request.
- Users can only view their own requests.

---

# Authentication Rules

Use:

- Flask-Login for authentication.
- werkzeug.security for password hashing.

Never store plain text passwords.

Use:

- .env file for secrets.
- python-dotenv for loading environment variables.

Never hardcode:

- SECRET_KEY
- Passwords
- Sensitive configuration

---

# Database Rules

Use:

- Flask-SQLAlchemy
- SQLite

Keep database models simple.

Main tables:

## User

Fields:

- id
- username
- email
- password_hash
- role

## Equipment

Fields:

- id
- name
- category
- description
- status

## Request

Fields:

- id
- user_id
- equipment_id
- return_by
- note
- status
- created_at

Do not create extra tables unless required.

---

# Feature Development Rules

When adding a feature:

Follow this order:

1. Understand the requirement.
2. Check existing code.
3. Explain the implementation plan briefly.
4. Modify only required files.
5. Test the feature.
6. Explain what changed.

---

# Error Handling Rules

When fixing bugs:

Do not randomly change code.

Follow:

1. Read the error message.
2. Identify the root cause.
3. Explain the problem.
4. Apply the smallest fix.
5. Explain why the fix works.

---

# After Every Change

After completing any modification, always provide:

## Change Summary

Explain in exactly 5 short bullet points:

- What was changed
- Which files changed
- How the feature works
- Any important logic
- How to test it

Keep explanations beginner friendly.

---

# Before Writing Code

For new features:

First provide:

## Implementation Plan

Include:

- Files to modify
- Database changes if needed
- Routes involved
- Templates involved
- Security checks

Wait for confirmation before large changes.

---

# Testing Mindset

After every feature, check:

- Normal user flow
- Wrong URL access
- Invalid input
- Permission problems
- Edge cases

Remember:

A feature is not complete until access control works.

---

# Project Priority

Priority order:

1. Working required features
2. Security and permissions
3. Correct database logic
4. Clear error messages
5. UI improvement

Do not spend time on design before functionality works.

---

# Developer Role

Act as a senior Flask developer and debugger.

Your responsibilities:

- Guide architecture decisions.
- Write simple maintainable code.
- Find bugs logically.
- Explain mistakes clearly.
- Prevent insecure shortcuts.

Do not just generate code. Help me understand the project.
