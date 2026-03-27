# AssignHub — Centralized Lab Assignment Submission & Evaluation System

A role-based web platform for managing lab assignments in academic institutions. Faculty create and publish assignments, students submit their work, and faculty evaluate submissions — all through dedicated dashboards.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0 (Python) |
| Database | MySQL (via XAMPP MariaDB) |
| Frontend | HTML, CSS (Tailwind), JavaScript |
| Icons | Lucide Icons |
| Email | Gmail SMTP |

## Project Structure

```
AssignHub/
├── core/              # Django project settings, root URLs
├── accounts/          # Custom User model, login, register, password reset
├── academic/          # Course, Batch, Department models
├── assignments/       # Assignment CRUD, submissions, file uploads
├── dashboard/         # Role-based dashboards (admin, faculty, student)
│   └── views/         # Split into 8 view files by role/feature
├── templates/         # HTML templates (auth, dashboard, layouts)
├── static/            # CSS, JS, images
└── media/             # User uploads (assignments, submissions, profile pics)
```

## User Roles

| Role | Capabilities |
|------|-------------|
| **Admin** | Manage users, courses, batches, student enrollment, course-batch mapping |
| **Faculty** | Create/edit assignments, review submissions, evaluate with marks & feedback |
| **Student** | View enrolled courses, submit assignments, track grades |

> Admin accounts can only be created by existing admins or via CLI — public registration is restricted to Student and Faculty roles.

## Features

- **Role-based dashboards** with live stats (courses, submissions, evaluations)
- **Assignment lifecycle**: create → publish → submit → evaluate
- **File management**: multi-file upload with size/type restrictions
- **In-app notifications**: assignment posted, deadline extended, submission evaluated
- **Email integration**: welcome emails, password reset via Gmail SMTP
- **Batch management**: student enrollment, course-batch mapping, archive/unarchive
- **Profile management**: profile picture, password change, role-specific fields
- **Dynamic dropdowns**: course → batch filtering in assignment creation

## Prerequisites

- **Python 3.10+**
- **XAMPP** (for MySQL/MariaDB)
- **Git**

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/solanki-vimal/AssignHub.git
   cd AssignHub
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install django mysqlclient
   ```

4. **Set up the database**
   - Start XAMPP and ensure MySQL is running
   - Open phpMyAdmin and create a database named `assignhub`
   - Verify the database settings in `core/settings.py`:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'assignhub',
             'USER': 'root',
             'PASSWORD': '',
             'HOST': '127.0.0.1',
             'PORT': '3306',
         }
     }
     ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Open in browser**
   ```
   http://127.0.0.1:8000
   ```

## Email Configuration

The project uses Gmail SMTP for sending welcome emails and password reset links. Update the credentials in `core/settings.py`:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

> Use a [Google App Password](https://myaccount.google.com/apppasswords), not your regular Gmail password.

## License

This project is developed for academic purposes.
