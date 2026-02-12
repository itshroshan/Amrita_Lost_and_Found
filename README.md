# 🎓 Lost and Found Management System

A beginner-friendly **Flask-based web application** that includes user authentication, role-based dashboards, and database integration.  
This project is designed to help understand **backend fundamentals**, **Flask routing**, **sessions**, and **SQLite databases**.

---

## 🚀 Features

- 🔐 User Registration & Login
- 🧑‍🎓 Role-based access (Student/Admin dashboard)
- 📊 Personalized dashboard (displays logged-in user’s name)
- 🗄️ SQLite database integration
- 🔑 Session-based authentication
- 🧾 Secure password handling
- 🌐 Simple and clean UI using HTML & CSS

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Version Control:** Git & GitHub

---

## 📂 Project Structure
```bash
    │── app.py
    │── database.db
    │── requirements.txt
    │── .gitignore
    │
    ├── templates/
    │ ├── admin_dashboard.html
    │ ├── change_password.html
    │ ├── claim_item.html
    │ ├── claimed_items.html
    │ ├── error.html
    │ ├── error_otp.html
    │ ├── footer.html
    │ ├── forgot_password.html
    │ ├── index.html
    │ ├── login.html
    │ ├── navbar.html
    │ ├── register.html
    │ ├── report_found.html
    │ ├── report_lost.html
    │ ├── reset_password.html
    │ ├── search_items.html
    │ ├── student_dashboard.html
    │ ├── success.html
    │ ├── upload_item.html
    │ ├── verify_change_password.html
    │ ├── verify_forgot_otp.html
    │ ├── verify_otp.html
    │ ├── view_items.html
    │ ├── view_lost_items.html
    │
    ├── static/
    │ ├── css/
    │ ├── js/
    │ ├── images/
    │
    └── README.md
```
---
### 🧠 How It Works

- Users register and log in using credentials
- Login creates a session storing user role and name
- Routes are protected using session checks
- Student dashboard dynamically displays logged-in user data
- SQLite handles persistent storage

---
### 📌 Learning Objectives
This project helped me learn:

- Flask routing and templates
- Session management
- Backend authentication logic
- Database CRUD operations
- GitHub project structuring

---

## 📄 License
This project is open-source and available under the MIT License.

---

## 🙋‍♂️ Author
Roshan Kumar Shah

