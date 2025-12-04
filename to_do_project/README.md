# FocusFlow – To-Do Web App ✅

FocusFlow is a Django-based productivity web application that helps users manage tasks, set reminders, and stay organized.  
It includes user authentication, profile management, email notifications, and a clean, responsive interface.

---

## 🚀 Features
- **Task Management**: Add, edit, delete, and toggle tasks.
- **Calendar View**: Visualize tasks by due date.
- **Reminders**: Automated email reminders for pending tasks.
- **User Profiles**: Customizable profiles with avatar upload.
- **Authentication**: Secure login, registration, password reset, and account deletion.
- **Email Integration**: HTML emails with inline logo branding.
- **Admin Dashboard**: Manage tasks, profiles, and attachments with previews.

---

## 🛠️ Tech Stack
- **Backend**: Django 5.2.7
- **Database**: SQLite (default, easy setup)
- **Frontend**: Django templates, CSS, responsive design
- **Email**: Gmail SMTP integration
- **Testing**: Django TestCase + Coverage (currently ~94% test coverage!)

---

## 📂 Project Structure
to_do_project/
    blog_project/ # Project settings & URLs
    htmlcov/
    media/
    to_do_app/ # Main application
    .coverage
    db.sqlite
    manage.py
    README.md
    requirements.txt
    venv/
    .gitignore


---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/To-Do-Web-App.git
cd focusflow/to_do_project

---
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

---
pip install -r requirements.txt

---
**Apply migrations
python manage.py migrate

**Create a superuser (for admin access)
python manage.py createsuperuser

**Run the development server
python manage.py runserver
Visit server link in your browser.

---
**Testing & Coverage
python -m coverage run manage.py test to_do_app
python -m coverage report
python -m coverage html

---
👩‍💻 Authors
- **Naomi Liboke**
- **Ginna Seerane**
- **Nomfundo Mhlongo**