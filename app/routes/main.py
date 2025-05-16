from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from app.models.academic import ContentBlock, Notification
from app.models.attendance import Sport
from app.models.user import StudentProfile
from app import db
from app.forms.auth import LoginForm

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher.dashboard'))
        elif current_user.is_parent():
            return redirect(url_for('parent.dashboard'))
        elif current_user.is_student():
            return redirect(url_for('student.dashboard'))

    # Get content blocks for the home page
    content_blocks = ContentBlock.query.filter_by(location='home', is_active=True).order_by(ContentBlock.order).all()

    # Create login form for the sidebar
    form = LoginForm()

    return render_template('main/index.html', title='Home', content_blocks=content_blocks, form=form)

@main_bp.route('/about')
def about():
    # Get content blocks for the about page
    content_blocks = ContentBlock.query.filter_by(location='about', is_active=True).order_by(ContentBlock.order).all()

    # Create login form for the sidebar
    form = LoginForm()

    return render_template('main/about.html', title='About Us', content_blocks=content_blocks, form=form)

@main_bp.route('/contact')
def contact():
    # Get content blocks for the contact page
    content_blocks = ContentBlock.query.filter_by(location='contact', is_active=True).order_by(ContentBlock.order).all()

    # Create login form for the sidebar
    form = LoginForm()

    return render_template('main/contact.html', title='Contact Us', content_blocks=content_blocks, form=form)

@main_bp.route('/standards')
def standards():
    # Create login form for the sidebar
    form = LoginForm()

    # Get active standards from the database
    from app.models.academic_structure import Standard, Board

    # Get page parameter (default to page 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Show 10 standards per page

    # Get all active standards with pagination
    standards_pagination = Standard.query.filter_by(is_active=True).order_by(Standard.name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Format standards data for the template
    standards = []

    # Default subject lists based on standard name patterns
    default_subjects = {
        '1': ['English', 'Mathematics', 'Science', 'Art'],
        '2': ['English', 'Mathematics', 'Science', 'Social Studies', 'Art'],
        '3': ['English', 'Mathematics', 'Science', 'Social Studies', 'Computer Science'],
        '4': ['English', 'Mathematics', 'Science', 'History', 'Geography', 'Computer Science'],
        '5': ['English', 'Mathematics', 'Science', 'History', 'Geography', 'Computer Science', 'Foreign Language'],
        '6': ['English', 'Mathematics', 'Science', 'History', 'Geography', 'Computer Science', 'Foreign Language'],
        '7': ['English', 'Mathematics', 'Science', 'History', 'Geography', 'Computer Science', 'Foreign Language'],
        '8': ['English', 'Mathematics', 'Science', 'History', 'Geography', 'Computer Science', 'Foreign Language'],
        '9': ['English', 'Mathematics', 'Science', 'History', 'Geography', 'Computer Science', 'Foreign Language'],
        '10': ['English', 'Mathematics', 'Science', 'History', 'Geography', 'Computer Science', 'Foreign Language'],
        '11': ['English', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science', 'Economics'],
        '12': ['English', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Computer Science', 'Economics']
    }

    # Default images for standards
    standard_images = [
        'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
        'https://images.unsplash.com/photo-1588072432836-e10032774350?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
        'https://images.unsplash.com/photo-1580582932707-520aed937b7b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
        'https://images.unsplash.com/photo-1588075592446-265fd1e6e76f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
        'https://images.unsplash.com/photo-1516979187457-637abb4f9353?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80',
        'https://images.unsplash.com/photo-1509062522246-3755977927d7?ixlib=rb-1.2.1&auto=format&fit=crop&w=1050&q=80'
    ]

    for i, standard in enumerate(standards_pagination.items):
        # Extract grade number if present in the name
        import re
        grade_match = re.search(r'(\d+)', standard.name)
        grade_num = grade_match.group(1) if grade_match else str((i % 12) + 1)

        # Get subjects based on grade number or default to a basic set
        subjects = default_subjects.get(grade_num, ['English', 'Mathematics', 'Science'])

        # Get image (cycle through available images)
        image = standard_images[i % len(standard_images)]

        # Format board information if available
        board_info = standard.board.name if standard.board else "General"

        standards.append({
            'id': standard.id,
            'name': standard.name,
            'description': standard.description or f'Curriculum for {standard.name}',
            'image': image,
            'subjects': subjects,
            'board': board_info,
            'academic_year': standard.academic_year
        })

    return render_template('main/standards.html',
                          title='Standards/Grades',
                          standards=standards,
                          pagination=standards_pagination,
                          form=form)

@main_bp.route('/sports/detail/<int:sport_id>')
def sport_detail(sport_id):
    # Create login form for the sidebar
    form = LoginForm()

    # Get the sport
    sport = Sport.query.get_or_404(sport_id)

    if not sport.is_active:
        flash('This sport program is not currently active', 'warning')
        return redirect(url_for('main.sports'))

    # Get appropriate image based on sport category
    default_image = '/static/img/sports/default.jpg'

    # Category-specific images
    category_images = {
        'team sport': '/static/img/sports/team_sport.jpg',  # Soccer
        'individual sport': '/static/img/sports/individual_sport.jpg',  # Track
        'martial arts': '/static/img/sports/martial_arts.jpg',  # Karate
        'swimming': '/static/img/sports/swimming.jpg',  # Swimming
        'aquatics': '/static/img/sports/swimming.jpg',  # Swimming
        'athletics': '/static/img/sports/athletics.jpg',  # Athletics
        'track and field': '/static/img/sports/athletics.jpg',  # Athletics
        'yoga': '/static/img/sports/yoga.jpg',  # Yoga
        'fitness': '/static/img/sports/yoga.jpg',  # Yoga
        'dance': '/static/img/sports/dance.jpg',  # Dance
        'board game': '/static/img/sports/chess.jpg',  # Chess
        'racquet sport': '/static/img/sports/badminton.jpg',  # Badminton
        'other': '/static/img/sports/default.jpg'  # Generic
    }

    # Sport-specific images
    sport_name_images = {
        'football': '/static/img/sports/football.jpg',
        'cricket': '/static/img/sports/cricket.jpg',
        'basketball': '/static/img/sports/basketball.jpg',
        'volleyball': '/static/img/sports/volleyball.jpg',
        'tennis': '/static/img/sports/tennis.jpg',
        'badminton': '/static/img/sports/badminton.jpg',
        'table tennis': '/static/img/sports/table_tennis.jpg',
        'swimming': '/static/img/sports/swimming.jpg',
        'karate': '/static/img/sports/karate.jpg',
        'taekwondo': '/static/img/sports/taekwondo.jpg',
        'judo': '/static/img/sports/judo.jpg',
        'yoga': '/static/img/sports/yoga.jpg',
        'dance': '/static/img/sports/dance.jpg',
        'gymnastics': '/static/img/sports/gymnastics.jpg',
        'athletics': '/static/img/sports/athletics.jpg',
        'kabaddi': '/static/img/sports/kabaddi.jpg',
        'kho kho': '/static/img/sports/kho_kho.jpg',
        'chess': '/static/img/sports/chess.jpg',
        'carrom': '/static/img/sports/carrom.jpg',
        'silambam': '/static/img/sports/silambam.jpg'
    }

    # Try to find a sport-specific image first, then category image, then use default or user-set image
    sport_name_lower = sport.name.lower()
    sport_category_lower = sport.category.lower() if sport.category else ''

    if sport.image:
        image = sport.image
    elif sport_name_lower in sport_name_images:
        image = sport_name_images[sport_name_lower]
    elif sport_category_lower in category_images:
        image = category_images[sport_category_lower]
    else:
        image = default_image

    # Set appropriate icon
    icon = sport.icon or 'fas fa-running'

    # Get coach name
    coach_name = f"{sport.instructor.user.first_name} {sport.instructor.user.last_name}"

    # Get fee structures
    fees = []
    for fee in sport.fees.filter_by(is_active=True).all():
        fees.append({
            'id': fee.id,
            'name': fee.name,
            'amount': fee.amount,
            'frequency': fee.frequency,
            'description': fee.description
        })

    # Format sport data
    sport_data = {
        'id': sport.id,
        'name': sport.name,
        'description': sport.description,
        'image': image,
        'icon': icon,
        'coach': coach_name,
        'schedule': sport.schedule,
        'location': sport.location,
        'category': sport.category,
        'fees': fees,
        'capacity': sport.capacity,
        'enrolled': len(sport.students)
    }

    return render_template('main/sport_detail.html', title=f'{sport.name} Program', sport=sport_data, form=form)

@main_bp.route('/sports')
def sports():
    # Create login form for the sidebar
    form = LoginForm()

    # Get active sports from the database
    db_sports = Sport.query.filter_by(is_active=True).all()

    # Format sports data for the template
    sports = []
    for sport in db_sports:
        # Get appropriate image based on sport category
        default_image = '/static/img/sports/default.jpg'

        # Category-specific images
        category_images = {
            'team sport': '/static/img/sports/team_sport.jpg',  # Soccer
            'individual sport': '/static/img/sports/individual_sport.jpg',  # Track
            'martial arts': '/static/img/sports/martial_arts.jpg',  # Karate
            'swimming': '/static/img/sports/swimming.jpg',  # Swimming
            'aquatics': '/static/img/sports/swimming.jpg',  # Swimming
            'athletics': '/static/img/sports/athletics.jpg',  # Athletics
            'track and field': '/static/img/sports/athletics.jpg',  # Athletics
            'yoga': '/static/img/sports/yoga.jpg',  # Yoga
            'fitness': '/static/img/sports/yoga.jpg',  # Yoga
            'dance': '/static/img/sports/dance.jpg',  # Dance
            'board game': '/static/img/sports/chess.jpg',  # Chess
            'racquet sport': '/static/img/sports/badminton.jpg',  # Badminton
            'other': '/static/img/sports/default.jpg'  # Generic
        }

        # Sport-specific images
        sport_name_images = {
            'football': '/static/img/sports/football.jpg',
            'cricket': '/static/img/sports/cricket.jpg',
            'basketball': '/static/img/sports/basketball.jpg',
            'volleyball': '/static/img/sports/volleyball.jpg',
            'tennis': '/static/img/sports/tennis.jpg',
            'badminton': '/static/img/sports/badminton.jpg',
            'table tennis': '/static/img/sports/table_tennis.jpg',
            'swimming': '/static/img/sports/swimming.jpg',
            'karate': '/static/img/sports/karate.jpg',
            'taekwondo': '/static/img/sports/taekwondo.jpg',
            'judo': '/static/img/sports/judo.jpg',
            'yoga': '/static/img/sports/yoga.jpg',
            'dance': '/static/img/sports/dance.jpg',
            'gymnastics': '/static/img/sports/gymnastics.jpg',
            'athletics': '/static/img/sports/athletics.jpg',
            'kabaddi': '/static/img/sports/kabaddi.jpg',
            'kho kho': '/static/img/sports/kho_kho.jpg',
            'chess': '/static/img/sports/chess.jpg',
            'carrom': '/static/img/sports/carrom.jpg',
            'silambam': '/static/img/sports/silambam.jpg'
        }

        # Try to find a sport-specific image first, then category image, then use default or user-set image
        sport_name_lower = sport.name.lower()
        sport_category_lower = sport.category.lower() if sport.category else ''

        if sport.image:
            image = sport.image
        elif sport_name_lower in sport_name_images:
            image = sport_name_images[sport_name_lower]
        elif sport_category_lower in category_images:
            image = category_images[sport_category_lower]
        else:
            image = default_image

        # Set appropriate icon
        icon = sport.icon or 'fas fa-running'

        # Get coach name
        coach_name = f"{sport.instructor.user.first_name} {sport.instructor.user.last_name}"

        # Get fee structures
        fees = []
        for fee in sport.fees.filter_by(is_active=True).all():
            fees.append({
                'id': fee.id,
                'name': fee.name,
                'amount': fee.amount,
                'frequency': fee.frequency,
                'description': fee.description
            })

        sports.append({
            'id': sport.id,
            'name': sport.name,
            'description': sport.description,
            'image': image,
            'icon': icon,
            'coach': coach_name,
            'schedule': sport.schedule,
            'location': sport.location,
            'category': sport.category,
            'fees': fees
        })

    return render_template('main/sports.html', title='Sports Programs', sports=sports, form=form)

@main_bp.route('/sports/join/<int:sport_id>')
def join_sport(sport_id):
    # Store the sport_id in session to redirect back after login
    session['join_sport_id'] = sport_id

    # If user is not logged in, redirect to login page
    if not current_user.is_authenticated:
        flash('Please log in or create an account to join this program', 'info')
        return redirect(url_for('auth.login', next=url_for('main.complete_join_sport')))

    # If user is logged in, proceed to enrollment
    return redirect(url_for('main.complete_join_sport'))

@main_bp.route('/sports/join/complete')
@login_required
def complete_join_sport():
    # Get the sport_id from session
    sport_id = session.pop('join_sport_id', None)

    if not sport_id:
        flash('No sport selected for enrollment', 'danger')
        return redirect(url_for('main.sports'))

    # Get the sport
    sport = Sport.query.get_or_404(sport_id)

    # Get or create student profile
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()

    # If user is not a student, create a student profile
    if not student:
        if current_user.is_admin() or current_user.is_teacher() or current_user.is_parent():
            # Generate a unique roll number based on user role and ID
            role_prefix = {
                'admin': 'ADM',
                'teacher': 'TCH',
                'parent': 'PAR'
            }.get(current_user.role, 'USR')

            # Get the first standard (for required standard_id)
            from app.models.academic_structure import Standard
            default_standard = Standard.query.first()
            if not default_standard:
                flash('Cannot create student profile: No standards found in the system', 'danger')
                return redirect(url_for('main.sports'))

            # Create a student profile for this user with required fields
            from datetime import datetime, date
            student = StudentProfile(
                user_id=current_user.id,
                roll_number=f"{role_prefix}{current_user.id:04d}",  # Generate unique roll number
                date_of_birth=date(2000, 1, 1),  # Default date of birth
                standard_id=default_standard.id,  # Required field
                admission_date=datetime.now().date(),  # Current date as admission date
                academic_year=f"{datetime.now().year}-{datetime.now().year + 1}",  # Current academic year
                is_active=True
            )
            db.session.add(student)
            db.session.commit()
            flash('A student profile has been created for you to join sports programs', 'info')
        else:
            flash('Only students can join sports programs', 'warning')
            return redirect(url_for('main.sports'))

    # Check if student is already enrolled
    if student in sport.students:
        flash(f'You are already enrolled in {sport.name}', 'info')
        return redirect(url_for('main.sport_detail', sport_id=sport.id))

    # Check if sport has reached capacity
    if len(sport.students) >= sport.capacity:
        flash(f'Sorry, {sport.name} has reached its maximum capacity', 'warning')
        return redirect(url_for('main.sport_detail', sport_id=sport.id))

    # Enroll the student
    sport.students.append(student)

    # Create a notification for the student
    notification = Notification(
        user_id=current_user.id,
        title=f"Enrolled in {sport.name}",
        message=f"You have successfully enrolled in {sport.name}. Schedule: {sport.schedule}, Location: {sport.location}",
        category="sports",
        related_id=sport.id,
        is_read=False
    )
    db.session.add(notification)

    # Create a notification for the instructor
    instructor_notification = Notification(
        user_id=sport.instructor.user_id,
        title=f"New Student in {sport.name}",
        message=f"{current_user.first_name} {current_user.last_name} has enrolled in your {sport.name} program.",
        category="sports",
        related_id=sport.id,
        is_read=False
    )
    db.session.add(instructor_notification)

    db.session.commit()

    flash(f'Successfully enrolled in {sport.name}!', 'success')

    # Redirect to the sport detail page instead of the sports list
    return redirect(url_for('main.sport_detail', sport_id=sport.id))
