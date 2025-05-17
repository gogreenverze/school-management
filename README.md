# School Management System

A comprehensive school management system built with Python and Flask, featuring attendance tracking, fee management, homework management, sports activities, and more. Designed with a mobile-first approach for Indian schools in Tamil Nadu.

## Features

- **Mobile-first design** with responsive layouts for all devices
- **Custom theme** using magenta as the primary color
- **Role-based access** for administrators, teachers, parents, and students
- **Academic structure** with boards, standards, sections, and classes
- **Attendance tracking** for both school classes and sports activities
- **Fee management** with comprehensive fee structure and payment tracking
- **Invoice system** with automatic generation and reminders
- **Homework management** system
- **Sports activities** management with enrollment and fee tracking
- **Notification system** for parents and students (including WhatsApp integration)
- **Content management** for administrators

## Technology Stack

- **Backend**: Python with Flask
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Migrations**: Flask-Migrate
- **Email**: Flask-Mail
- **PDF Generation**: WeasyPrint, pdfkit
- **Frontend**: HTML, CSS, JavaScript

## Installation from Git

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
   DATABASE_URL=sqlite:///instance/school.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-email-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

5. Initialize the database:
   ```
   python create_db.py
   ```

6. Import the mock data (optional):
   ```
   python import_database.py
   ```
   This will import all the mock data for Tamil Nadu schools, including students, teachers, classes, standards, sections, boards, and sports activities.

7. Run the application:
   ```
   python run.py
   ```

8. Access the application at http://127.0.0.1:5007

## Default Login Credentials

- **Admin Username**: admin
- **Admin Password**: admin123
- **Teacher Username**: teacher1
- **Teacher Password**: teacher123
- **Student Username**: student1
- **Student Password**: student123

## Project Structure

```
school-management/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py
│   │   ├── attendance.py
│   │   ├── finance.py
│   │   ├── academic_structure.py
│   │   └── settings.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── main.py
│   │   ├── admin.py
│   │   ├── admin_views.py
│   │   ├── admin_fees.py
│   │   ├── admin_invoices.py
│   │   ├── admin_settings.py
│   │   ├── teacher.py
│   │   ├── teacher_attendance.py
│   │   ├── teacher_homework.py
│   │   ├── student.py
│   │   ├── student_attendance.py
│   │   ├── student_homework.py
│   │   └── student_invoices.py
│   ├── forms/
│   │   ├── auth.py
│   │   ├── content.py
│   │   ├── academic.py
│   │   ├── attendance.py
│   │   ├── fees.py
│   │   ├── invoices.py
│   │   ├── settings.py
│   │   ├── sports.py
│   │   └── user_profile.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── main/
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── teacher/
│   │   ├── student/
│   │   ├── email/
│   │   └── pdf/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── uploads/
│   └── utils/
│       ├── email.py
│       ├── fee_utils.py
│       ├── pdf_utils.py
│       ├── scheduler.py
│       ├── whatsapp.py
│       └── generate_data.py
├── migrations/
├── instance/
├── run.py
├── create_db.py
├── requirements.txt
├── .env
└── README.md
```

## Development

To contribute to this project:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License.

## Footer

Developed by Praba Krishna @2023
