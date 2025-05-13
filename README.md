# School Management System

A comprehensive school management system built with Python and Flask, featuring attendance tracking, fee management, homework management, and more.

## Features

- **Mobile-first design** with bottom navigation
- **Custom theme** using magenta, teal, white, and grey colors
- **Role-based access** for administrators, teachers, parents, and students
- **Attendance tracking** for both school classes and sports/martial arts
- **Fee management** with payment tracking and reminders
- **Homework management** system
- **Notification system** for parents and students
- **Content management** for administrators

## Technology Stack

- **Backend**: Python with Flask
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Authentication**: Flask-Login
- **Admin Panel**: Flask-Admin
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Email**: Flask-Mail

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/school-management.git
   cd school-management
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a .env file):
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///school.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-email-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

5. Run the application:
   ```
   python run.py
   ```

6. Access the application at http://localhost:5000

## Default Login Credentials

- **Username**: admin
- **Password**: admin123

## Project Structure

```
school-management/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── attendance.py
│   │   ├── finance.py
│   │   └── academic.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── admin.py
│   │   ├── teacher.py
│   │   ├── parent.py
│   │   └── student.py
│   ├── forms/
│   │   ├── auth.py
│   │   └── content.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── main/
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── teacher/
│   │   ├── parent/
│   │   └── student/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── utils/
│       ├── decorators.py
│       ├── email.py
│       └── init_db.py
├── run.py
├── requirements.txt
├── .env
└── README.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
