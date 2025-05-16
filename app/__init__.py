import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_admin import Admin
from flask_migrate import Migrate
from dotenv import load_dotenv
import jinja2
from markupsafe import Markup

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
admin = Admin(name='School Management System', template_mode='bootstrap4', url='/admin_panel', endpoint='admin_panel')
migrate = Migrate()

def nl2br(value):
    """Convert newlines to <br> tags."""
    if value:
        return Markup(value.replace('\n', '<br>\n'))
    return value

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///school.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # File upload configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'yes', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    mail.init_app(app)
    migrate.init_app(app, db)

    # Register custom Jinja2 filters
    app.jinja_env.filters['nl2br'] = nl2br

    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.admin_fees import admin_fees_bp
    from app.routes.admin_settings import admin_settings_bp
    from app.routes.admin_invoices import admin_invoices_bp
    from app.routes.teacher import teacher_bp
    from app.routes.teacher_homework import teacher_homework_bp
    from app.routes.teacher_attendance import teacher_attendance_bp
    from app.routes.parent import parent_bp
    from app.routes.student import student_bp
    from app.routes.student_homework import student_homework_bp
    from app.routes.student_attendance import student_attendance_bp
    from app.routes.student_invoices import student_invoices_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin_dashboard')  # Changed URL prefix to avoid conflict
    app.register_blueprint(admin_fees_bp)  # Fee management routes
    app.register_blueprint(admin_settings_bp)  # Admin settings routes
    app.register_blueprint(admin_invoices_bp)  # Invoice management routes
    app.register_blueprint(teacher_bp)
    app.register_blueprint(teacher_homework_bp)
    app.register_blueprint(teacher_attendance_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(student_homework_bp)
    app.register_blueprint(student_attendance_bp)
    app.register_blueprint(student_invoices_bp)  # Student invoice routes

    # Initialize admin views
    from app.routes.admin_views import init_admin_views
    init_admin_views(admin, db)
    admin.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

        # Import and create initial data if needed
        from app.utils.init_db import create_initial_data
        create_initial_data()

    return app
