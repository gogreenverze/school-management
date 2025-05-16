from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT, TeacherProfile, StudentProfile, ParentProfile
from app.models.academic import ContentBlock
from app.models.academic_structure import Board, Standard, Section
from app.models.attendance import Class, Sport
from app.models.finance import SportFee, SportFeePayment
from app.models.settings import WhatsAppConfig
from app.forms.content import ContentBlockForm
from app.forms.academic import StandardForm, SectionForm
from app.forms.user_profile import TeacherProfileForm, StudentProfileForm, ClassAssignmentForm
from app.forms.sports import SportForm, SportFeeForm, SportStudentForm
from app.utils.decorators import admin_required
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin_dashboard')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get counts for dashboard
    total_students = User.query.filter_by(role='student', is_active=True).count()
    total_teachers = User.query.filter_by(role='teacher', is_active=True).count()
    total_parents = User.query.filter_by(role='parent', is_active=True).count()
    total_classes = Class.query.filter_by(is_active=True).count()
    total_sports = Sport.query.filter_by(is_active=True).count()

    # Get board data
    boards = Board.query.filter_by(is_active=True).all()
    total_boards = len(boards)

    # Check WhatsApp configuration status
    whatsapp_config = WhatsAppConfig.query.filter_by(is_enabled=True).first()
    whatsapp_enabled = whatsapp_config is not None and whatsapp_config.api_key and whatsapp_config.phone_number_id

    # Get standards count and student count by board
    board_data = []
    for board in boards:
        # Get standards for this board
        standards_count = Standard.query.filter_by(board_id=board.id, is_active=True).count()

        # Get standards IDs for this board
        standard_ids = [standard.id for standard in Standard.query.filter_by(board_id=board.id, is_active=True).all()]

        # Count students in these standards
        students_count = 0
        if standard_ids:
            students_count = StudentProfile.query.filter(
                StudentProfile.standard_id.in_(standard_ids),
                StudentProfile.is_active == True
            ).count()

        board_data.append({
            'id': board.id,
            'name': board.name,
            'code': board.code,
            'standards_count': standards_count,
            'students_count': students_count
        })

    return render_template('admin/dashboard.html',
                          title='Admin Dashboard',
                          total_students=total_students,
                          total_teachers=total_teachers,
                          total_parents=total_parents,
                          total_classes=total_classes,
                          total_boards=total_boards,
                          total_sports=total_sports,
                          board_data=board_data,
                          whatsapp_enabled=whatsapp_enabled)

@admin_bp.route('/content')
@login_required
@admin_required
def content_list():
    content_blocks = ContentBlock.query.order_by(ContentBlock.location, ContentBlock.order).all()
    return render_template('admin/content/list.html', title='Content Management', content_blocks=content_blocks)

@admin_bp.route('/content/create', methods=['GET', 'POST'])
@login_required
@admin_required
def content_create():
    form = ContentBlockForm()
    if form.validate_on_submit():
        content_block = ContentBlock(
            name=form.name.data,
            title=form.title.data,
            content=form.content.data,
            location=form.location.data,
            order=form.order.data,
            is_active=form.is_active.data,
            created_by=current_user.id
        )
        db.session.add(content_block)
        db.session.commit()
        flash('Content block created successfully', 'success')
        return redirect(url_for('admin.content_list'))

    return render_template('admin/content/create.html', title='Create Content Block', form=form)

@admin_bp.route('/content/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def content_edit(id):
    content_block = ContentBlock.query.get_or_404(id)
    form = ContentBlockForm(obj=content_block)
    form.id.data = content_block.id  # Set the id field

    if form.validate_on_submit():
        content_block.name = form.name.data
        content_block.title = form.title.data
        content_block.content = form.content.data
        content_block.location = form.location.data
        content_block.order = form.order.data
        content_block.is_active = form.is_active.data

        db.session.commit()
        flash('Content block updated successfully', 'success')
        return redirect(url_for('admin.content_list'))

    return render_template('admin/content/edit.html', title='Edit Content Block', form=form, content_block=content_block)

@admin_bp.route('/content/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def content_delete(id):
    content_block = ContentBlock.query.get_or_404(id)
    db.session.delete(content_block)
    db.session.commit()
    flash('Content block deleted successfully', 'success')
    return redirect(url_for('admin.content_list'))

@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/users/list.html', title='User Management', users=users)

# Board Management Routes
@admin_bp.route('/boards')
@login_required
@admin_required
def board_list():
    boards = Board.query.order_by(Board.name).all()
    return render_template('admin/boards/list.html', title='Board Management', boards=boards)

@admin_bp.route('/add_board', methods=['POST'])
@login_required
@admin_required
def add_board():
    name = request.form.get('name')
    code = request.form.get('code')
    description = request.form.get('description')
    is_active = True if request.form.get('is_active') else False

    board = Board(name=name, code=code, description=description, is_active=is_active)
    db.session.add(board)
    db.session.commit()

    flash('Board added successfully!', 'success')
    return redirect(url_for('admin.board_list'))

@admin_bp.route('/edit_board/<int:board_id>', methods=['POST'])
@login_required
@admin_required
def edit_board(board_id):
    board = Board.query.get_or_404(board_id)

    board.name = request.form.get('name')
    board.code = request.form.get('code')
    board.description = request.form.get('description')
    board.is_active = True if request.form.get('is_active') else False

    db.session.commit()

    flash('Board updated successfully!', 'success')
    return redirect(url_for('admin.board_list'))

@admin_bp.route('/delete_board/<int:board_id>')
@login_required
@admin_required
def delete_board(board_id):
    board = Board.query.get_or_404(board_id)

    # Delete associated standards
    standards = Standard.query.filter_by(board_id=board.id).all()
    for standard in standards:
        db.session.delete(standard)

    db.session.delete(board)
    db.session.commit()

    flash('Board deleted successfully!', 'success')
    return redirect(url_for('admin.board_list'))

# Standard Management Routes
@admin_bp.route('/standards')
@login_required
@admin_required
def standard_list():
    standards = Standard.query.order_by(Standard.name).all()
    return render_template('admin/standards/list.html', title='Standard Management', standards=standards)

@admin_bp.route('/standards/create', methods=['GET', 'POST'])
@login_required
@admin_required
def standard_create():
    form = StandardForm()
    if form.validate_on_submit():
        # Set board_id to None if 0 is selected (no board)
        board_id = form.board_id.data if form.board_id.data and form.board_id.data != 0 else None

        standard = Standard(
            name=form.name.data,
            description=form.description.data,
            board_id=board_id,
            academic_year=form.academic_year.data,
            is_active=form.is_active.data
        )
        db.session.add(standard)
        db.session.commit()
        flash('Standard created successfully', 'success')
        return redirect(url_for('admin.standard_list'))

    return render_template('admin/standards/create.html', title='Create Standard', form=form)

@admin_bp.route('/standards/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def standard_edit(id):
    standard = Standard.query.get_or_404(id)
    form = StandardForm(obj=standard)

    # Set the current board_id in the form
    if standard.board_id:
        form.board_id.data = standard.board_id

    if form.validate_on_submit():
        standard.name = form.name.data
        standard.description = form.description.data
        # Set board_id to None if 0 is selected (no board)
        standard.board_id = form.board_id.data if form.board_id.data and form.board_id.data != 0 else None
        standard.academic_year = form.academic_year.data
        standard.is_active = form.is_active.data
        standard.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Standard updated successfully', 'success')
        return redirect(url_for('admin.standard_list'))

    return render_template('admin/standards/edit.html', title='Edit Standard', form=form, standard=standard)

@admin_bp.route('/standards/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def standard_delete(id):
    standard = Standard.query.get_or_404(id)

    # Check if standard has sections
    if standard.sections.count() > 0:
        flash('Cannot delete standard with sections. Remove sections first.', 'danger')
        return redirect(url_for('admin.standard_list'))

    # Check if standard has students
    if hasattr(standard, 'students') and standard.students.count() > 0:
        flash('Cannot delete standard with students. Remove students first.', 'danger')
        return redirect(url_for('admin.standard_list'))

    # Check if standard has classes
    if hasattr(standard, 'classes') and standard.classes.count() > 0:
        flash('Cannot delete standard with classes. Remove classes first.', 'danger')
        return redirect(url_for('admin.standard_list'))

    db.session.delete(standard)
    db.session.commit()
    flash('Standard deleted successfully', 'success')
    return redirect(url_for('admin.standard_list'))

# Section Management Routes
@admin_bp.route('/sections')
@login_required
@admin_required
def section_list():
    sections = Section.query.join(Standard).order_by(Standard.name, Section.name).all()
    return render_template('admin/sections/list.html', title='Section Management', sections=sections)

@admin_bp.route('/sections/create', methods=['GET', 'POST'])
@login_required
@admin_required
def section_create():
    form = SectionForm()
    form.standard_id.choices = [(s.id, s.name) for s in Standard.query.order_by(Standard.name).all()]

    if form.validate_on_submit():
        section = Section(
            name=form.name.data,
            standard_id=form.standard_id.data,
            description=form.description.data,
            capacity=form.capacity.data,
            is_active=form.is_active.data
        )
        db.session.add(section)
        db.session.commit()
        flash('Section created successfully', 'success')
        return redirect(url_for('admin.section_list'))

    return render_template('admin/sections/create.html', title='Create Section', form=form)

@admin_bp.route('/sections/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def section_edit(id):
    section = Section.query.get_or_404(id)
    form = SectionForm(obj=section)
    form.standard_id.choices = [(s.id, s.name) for s in Standard.query.order_by(Standard.name).all()]

    if form.validate_on_submit():
        section.name = form.name.data
        section.standard_id = form.standard_id.data
        section.description = form.description.data
        section.capacity = form.capacity.data
        section.is_active = form.is_active.data
        section.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Section updated successfully', 'success')
        return redirect(url_for('admin.section_list'))

    return render_template('admin/sections/edit.html', title='Edit Section', form=form, section=section)

@admin_bp.route('/sections/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def section_delete(id):
    section = Section.query.get_or_404(id)

    # Check if section has students
    if hasattr(section, 'students') and section.students.count() > 0:
        flash('Cannot delete section with students. Remove students first.', 'danger')
        return redirect(url_for('admin.section_list'))

    # Check if section has classes
    if hasattr(section, 'classes') and section.classes.count() > 0:
        flash('Cannot delete section with classes. Remove classes first.', 'danger')
        return redirect(url_for('admin.section_list'))

    db.session.delete(section)
    db.session.commit()
    flash('Section deleted successfully', 'success')
    return redirect(url_for('admin.section_list'))

# Teacher Management Routes
@admin_bp.route('/teachers')
@login_required
@admin_required
def teacher_list():
    teachers = TeacherProfile.query.join(User).order_by(User.first_name, User.last_name).all()
    return render_template('admin/teachers/list.html', title='Teacher Management', teachers=teachers)

@admin_bp.route('/teachers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def teacher_create():
    form = TeacherProfileForm()

    if form.validate_on_submit():
        # Create user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=ROLE_TEACHER
        )
        if form.password.data:
            user.set_password(form.password.data)
        else:
            # Set a default password (should be changed on first login)
            user.set_password('changeme')

        db.session.add(user)
        db.session.flush()  # Flush to get the user ID

        # Create teacher profile
        teacher = TeacherProfile(
            user_id=user.id,
            employee_id=form.employee_id.data,
            date_of_birth=form.date_of_birth.data,
            date_of_joining=form.date_of_joining.data,
            primary_subject=form.primary_subject.data,
            secondary_subjects=form.secondary_subjects.data,
            qualification=form.qualification.data,
            experience_years=form.experience_years.data,
            phone=form.phone.data,
            emergency_contact=form.emergency_contact.data,
            address=form.address.data,
            specialization=form.specialization.data,
            bio=form.bio.data,
            is_active=form.is_active.data
        )

        db.session.add(teacher)
        db.session.commit()
        flash('Teacher created successfully', 'success')
        return redirect(url_for('admin.teacher_list'))

    return render_template('admin/teachers/create.html', title='Create Teacher', form=form)

@admin_bp.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def teacher_edit(id):
    teacher = TeacherProfile.query.get_or_404(id)
    user = User.query.get_or_404(teacher.user_id)

    form = TeacherProfileForm(obj=teacher)
    # Populate user fields
    form.username.data = user.username
    form.email.data = user.email
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name

    if form.validate_on_submit():
        # Update user
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        if form.password.data:
            user.set_password(form.password.data)

        # Update teacher profile
        teacher.employee_id = form.employee_id.data
        teacher.date_of_birth = form.date_of_birth.data
        teacher.date_of_joining = form.date_of_joining.data
        teacher.primary_subject = form.primary_subject.data
        teacher.secondary_subjects = form.secondary_subjects.data
        teacher.qualification = form.qualification.data
        teacher.experience_years = form.experience_years.data
        teacher.phone = form.phone.data
        teacher.emergency_contact = form.emergency_contact.data
        teacher.address = form.address.data
        teacher.specialization = form.specialization.data
        teacher.bio = form.bio.data
        teacher.is_active = form.is_active.data
        teacher.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Teacher updated successfully', 'success')
        return redirect(url_for('admin.teacher_list'))

    return render_template('admin/teachers/edit.html', title='Edit Teacher', form=form, teacher=teacher)

@admin_bp.route('/teachers/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def teacher_delete(id):
    teacher = TeacherProfile.query.get_or_404(id)
    user = User.query.get_or_404(teacher.user_id)

    # Check if teacher has classes
    if teacher.classes.count() > 0:
        flash('Cannot delete teacher with assigned classes. Remove class assignments first.', 'danger')
        return redirect(url_for('admin.teacher_list'))

    # Check if teacher is instructing sports
    if hasattr(teacher, 'sports_instructed') and teacher.sports_instructed.count() > 0:
        flash('Cannot delete teacher who is instructing sports. Remove sport assignments first.', 'danger')
        return redirect(url_for('admin.teacher_list'))

    db.session.delete(teacher)
    db.session.delete(user)
    db.session.commit()
    flash('Teacher deleted successfully', 'success')
    return redirect(url_for('admin.teacher_list'))

# Student Management Routes
@admin_bp.route('/students')
@login_required
@admin_required
def student_list():
    # Get filter parameters
    board_id = request.args.get('board_id', type=int)

    # Base query
    query = StudentProfile.query.join(User)

    # Apply board filter if provided
    if board_id:
        # Get standards for the selected board
        standard_ids = [s.id for s in Standard.query.filter_by(board_id=board_id).all()]
        if standard_ids:
            query = query.filter(StudentProfile.standard_id.in_(standard_ids))

    # Get all students with the applied filters
    students = query.order_by(User.first_name, User.last_name).all()

    # Get all boards for the filter dropdown
    boards = Board.query.filter_by(is_active=True).order_by(Board.name).all()

    return render_template('admin/students/list.html',
                          title='Student Management',
                          students=students,
                          boards=boards,
                          selected_board_id=board_id)

@admin_bp.route('/students/create', methods=['GET', 'POST'])
@login_required
@admin_required
def student_create():
    form = StudentProfileForm()

    # Populate board choices
    form.board_id.choices = [(0, 'Select Board')] + [(b.id, b.name) for b in Board.query.filter_by(is_active=True).order_by(Board.name).all()]

    # Dynamically update standards based on selected board
    selected_board_id = request.args.get('board_id', type=int)
    if selected_board_id:
        form.board_id.data = selected_board_id
        standards = Standard.query.filter_by(board_id=selected_board_id, is_active=True).order_by(Standard.name).all()
        form.standard_id.choices = [(s.id, s.name) for s in standards]
    else:
        form.standard_id.choices = [(s.id, s.name) for s in Standard.query.order_by(Standard.name).all()]

    form.parent_id.choices = [(0, 'None')] + [(p.id, p.user.get_full_name()) for p in ParentProfile.query.join(User).order_by(User.first_name, User.last_name).all()]

    # Dynamically update sections based on selected standard
    selected_standard_id = request.args.get('standard_id', type=int)
    if selected_standard_id:
        form.standard_id.data = selected_standard_id
        sections = Section.query.filter_by(standard_id=selected_standard_id).order_by(Section.name).all()
        form.section_id.choices = [(0, 'None')] + [(s.id, s.name) for s in sections]
    else:
        form.section_id.choices = [(0, 'None')]

    if form.validate_on_submit():
        # Create user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=ROLE_STUDENT
        )
        if form.password.data:
            user.set_password(form.password.data)
        else:
            # Set a default password (should be changed on first login)
            user.set_password('changeme')

        db.session.add(user)
        db.session.flush()  # Flush to get the user ID

        # Create student profile
        student = StudentProfile(
            user_id=user.id,
            roll_number=form.roll_number.data,
            date_of_birth=form.date_of_birth.data,
            standard_id=form.standard_id.data,
            section_id=form.section_id.data if form.section_id.data != 0 else None,
            admission_date=form.admission_date.data,
            parent_id=form.parent_id.data if form.parent_id.data != 0 else None,
            blood_group=form.blood_group.data,
            address=form.address.data,
            emergency_contact=form.emergency_contact.data,
            medical_conditions=form.medical_conditions.data,
            previous_school=form.previous_school.data,
            academic_year=form.academic_year.data,
            is_active=form.is_active.data
        )

        db.session.add(student)
        db.session.commit()
        flash('Student created successfully', 'success')
        return redirect(url_for('admin.student_list'))

    return render_template('admin/students/create.html', title='Create Student', form=form)

@admin_bp.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def student_edit(id):
    student = StudentProfile.query.get_or_404(id)
    user = User.query.get_or_404(student.user_id)

    form = StudentProfileForm(obj=student)
    # Populate user fields
    form.username.data = user.username
    form.email.data = user.email
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name

    # Populate board choices
    form.board_id.choices = [(0, 'Select Board')] + [(b.id, b.name) for b in Board.query.filter_by(is_active=True).order_by(Board.name).all()]

    # Get current board_id if standard has a board
    current_board_id = None
    if student.standard and student.standard.board:
        current_board_id = student.standard.board.id
        form.board_id.data = current_board_id

    # Dynamically update standards based on selected board
    selected_board_id = request.args.get('board_id', type=int) or current_board_id
    if selected_board_id:
        form.board_id.data = selected_board_id
        standards = Standard.query.filter_by(board_id=selected_board_id, is_active=True).order_by(Standard.name).all()
        form.standard_id.choices = [(s.id, s.name) for s in standards]
    else:
        form.standard_id.choices = [(s.id, s.name) for s in Standard.query.order_by(Standard.name).all()]

    form.parent_id.choices = [(0, 'None')] + [(p.id, p.user.get_full_name()) for p in ParentProfile.query.join(User).order_by(User.first_name, User.last_name).all()]

    # Load sections for the current standard
    selected_standard_id = request.args.get('standard_id', type=int) or student.standard_id
    if selected_standard_id:
        form.standard_id.data = selected_standard_id
        sections = Section.query.filter_by(standard_id=selected_standard_id).order_by(Section.name).all()
        form.section_id.choices = [(0, 'None')] + [(s.id, s.name) for s in sections]
    else:
        form.section_id.choices = [(0, 'None')]

    if form.validate_on_submit():
        # Update user
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data

        if form.password.data:
            user.set_password(form.password.data)

        # Update student profile
        student.roll_number = form.roll_number.data
        student.date_of_birth = form.date_of_birth.data
        student.standard_id = form.standard_id.data
        student.section_id = form.section_id.data if form.section_id.data != 0 else None
        student.admission_date = form.admission_date.data
        student.parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        student.blood_group = form.blood_group.data
        student.address = form.address.data
        student.emergency_contact = form.emergency_contact.data
        student.medical_conditions = form.medical_conditions.data
        student.previous_school = form.previous_school.data
        student.academic_year = form.academic_year.data
        student.is_active = form.is_active.data
        student.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Student updated successfully', 'success')
        return redirect(url_for('admin.student_list'))

    return render_template('admin/students/edit.html', title='Edit Student', form=form, student=student)

@admin_bp.route('/students/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def student_delete(id):
    student = StudentProfile.query.get_or_404(id)
    user = User.query.get_or_404(student.user_id)

    # Check if student has attendances
    if student.attendances.count() > 0:
        flash('Cannot delete student with attendance records.', 'danger')
        return redirect(url_for('admin.student_list'))

    # Check if student has fee payments
    if student.fee_payments.count() > 0:
        flash('Cannot delete student with fee payment records.', 'danger')
        return redirect(url_for('admin.student_list'))

    # Check if student has homework submissions
    if student.homework_submissions.count() > 0:
        flash('Cannot delete student with homework submissions.', 'danger')
        return redirect(url_for('admin.student_list'))

    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    flash('Student deleted successfully', 'success')
    return redirect(url_for('admin.student_list'))

# Class Assignment Routes
@admin_bp.route('/classes')
@login_required
@admin_required
def class_list():
    classes = Class.query.order_by(Class.name).all()
    return render_template('admin/classes/list.html', title='Class Management', classes=classes)

# Sports Management Routes
@admin_bp.route('/sports')
@login_required
@admin_required
def sport_list():
    # Get all sports with pagination
    page = request.args.get('page', 1, type=int)
    sports = Sport.query.order_by(Sport.name).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/sports/list.html', title='Sports Management', sports=sports)

@admin_bp.route('/sports/create', methods=['GET', 'POST'])
@login_required
@admin_required
def sport_create():
    form = SportForm()

    if form.validate_on_submit():
        sport = Sport(
            name=form.name.data,
            category=form.category.data,
            instructor_id=form.instructor_id.data,
            schedule=form.schedule.data,
            location=form.location.data,
            description=form.description.data,
            image=form.image.data,
            icon=form.icon.data,
            capacity=form.capacity.data,
            is_active=form.is_active.data
        )
        db.session.add(sport)
        db.session.commit()

        flash('Sport created successfully!', 'success')
        return redirect(url_for('admin.sport_list'))

    return render_template('admin/sports/create.html', title='Create Sport', form=form)

@admin_bp.route('/sports/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def sport_edit(id):
    sport = Sport.query.get_or_404(id)
    form = SportForm(obj=sport)
    form.id = sport.id

    if form.validate_on_submit():
        sport.name = form.name.data
        sport.category = form.category.data
        sport.instructor_id = form.instructor_id.data
        sport.schedule = form.schedule.data
        sport.location = form.location.data
        sport.description = form.description.data
        sport.image = form.image.data
        sport.icon = form.icon.data
        sport.capacity = form.capacity.data
        sport.is_active = form.is_active.data

        db.session.commit()
        flash('Sport updated successfully!', 'success')
        return redirect(url_for('admin.sport_list'))

    return render_template('admin/sports/edit.html', title='Edit Sport', form=form, sport=sport)

@admin_bp.route('/sports/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def sport_delete(id):
    sport = Sport.query.get_or_404(id)

    # Check if sport has students enrolled
    if sport.students.count() > 0:
        flash('Cannot delete sport with enrolled students. Remove student enrollments first.', 'danger')
        return redirect(url_for('admin.sport_list'))

    # Check if sport has fee payments
    if hasattr(sport, 'fee_payments') and sport.fee_payments.count() > 0:
        flash('Cannot delete sport with fee payments. Remove fee payments first.', 'danger')
        return redirect(url_for('admin.sport_list'))

    # Delete associated fees
    SportFee.query.filter_by(sport_id=sport.id).delete()

    # Delete the sport
    db.session.delete(sport)
    db.session.commit()
    flash('Sport deleted successfully!', 'success')
    return redirect(url_for('admin.sport_list'))

@admin_bp.route('/sports/view/<int:id>')
@login_required
@admin_required
def sport_view(id):
    sport = Sport.query.get_or_404(id)
    fees = SportFee.query.filter_by(sport_id=sport.id).all()
    students = sport.students  # sport.students is already a list, no need to call .all()

    return render_template('admin/sports/view.html',
                          title=f'Sport Details - {sport.name}',
                          sport=sport,
                          fees=fees,
                          students=students)

# Sport Fee Management Routes
@admin_bp.route('/sports/<int:sport_id>/fees')
@login_required
@admin_required
def sport_fee_list(sport_id):
    sport = Sport.query.get_or_404(sport_id)
    fees = SportFee.query.filter_by(sport_id=sport_id).all()

    return render_template('admin/sports/fees/list.html',
                          title=f'Fee Structures - {sport.name}',
                          sport=sport,
                          fees=fees)

@admin_bp.route('/sports/<int:sport_id>/fees/create', methods=['GET', 'POST'])
@login_required
@admin_required
def sport_fee_create(sport_id):
    sport = Sport.query.get_or_404(sport_id)
    form = SportFeeForm()
    form.sport_id.data = sport_id

    if form.validate_on_submit():
        fee = SportFee(
            sport_id=sport_id,
            name=form.name.data,
            amount=form.amount.data,
            frequency=form.frequency.data,
            duration=form.duration.data,
            description=form.description.data,
            is_active=form.is_active.data
        )
        db.session.add(fee)
        db.session.commit()

        flash('Fee structure created successfully!', 'success')
        return redirect(url_for('admin.sport_fee_list', sport_id=sport_id))

    return render_template('admin/sports/fees/create.html',
                          title=f'Create Fee Structure - {sport.name}',
                          form=form,
                          sport=sport)

@admin_bp.route('/sports/<int:sport_id>/fees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def sport_fee_edit(sport_id, id):
    sport = Sport.query.get_or_404(sport_id)
    fee = SportFee.query.get_or_404(id)

    if fee.sport_id != sport_id:
        flash('Invalid fee structure for this sport', 'danger')
        return redirect(url_for('admin.sport_fee_list', sport_id=sport_id))

    form = SportFeeForm(obj=fee)
    form.id = fee.id
    form.sport_id.data = sport_id

    if form.validate_on_submit():
        fee.name = form.name.data
        fee.amount = form.amount.data
        fee.frequency = form.frequency.data
        fee.duration = form.duration.data
        fee.description = form.description.data
        fee.is_active = form.is_active.data

        db.session.commit()
        flash('Fee structure updated successfully!', 'success')
        return redirect(url_for('admin.sport_fee_list', sport_id=sport_id))

    return render_template('admin/sports/fees/edit.html',
                          title=f'Edit Fee Structure - {sport.name}',
                          form=form,
                          sport=sport,
                          fee=fee)

@admin_bp.route('/sports/<int:sport_id>/fees/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def sport_fee_delete(sport_id, id):
    sport = Sport.query.get_or_404(sport_id)
    fee = SportFee.query.get_or_404(id)

    if fee.sport_id != sport_id:
        flash('Invalid fee structure for this sport', 'danger')
        return redirect(url_for('admin.sport_fee_list', sport_id=sport_id))

    # Check if fee has payments
    if fee.payments.count() > 0:
        flash('Cannot delete fee structure with payments. Remove payments first.', 'danger')
        return redirect(url_for('admin.sport_fee_list', sport_id=sport_id))

    db.session.delete(fee)
    db.session.commit()
    flash('Fee structure deleted successfully!', 'success')
    return redirect(url_for('admin.sport_fee_list', sport_id=sport_id))

# Student Enrollment Routes
@admin_bp.route('/sports/<int:sport_id>/students', methods=['GET', 'POST'])
@login_required
@admin_required
def sport_students(sport_id):
    sport = Sport.query.get_or_404(sport_id)
    enrolled_students = sport.students  # sport.students is already a list, no need to call .all()

    # Get all active students
    all_students = StudentProfile.query.filter_by(is_active=True).all()
    available_students = [s for s in all_students if s not in enrolled_students]

    form = SportStudentForm()
    form.sport_id.data = sport_id

    # Populate student choices
    form.student_ids.choices = [(s.id, f"{s.user.first_name} {s.user.last_name} ({s.roll_number})")
                              for s in available_students]

    if form.validate_on_submit():
        student_id = form.student_ids.data
        student = StudentProfile.query.get_or_404(student_id)

        # Check if student is already enrolled
        if student in sport.students:
            flash(f'{student.user.first_name} {student.user.last_name} is already enrolled in this sport', 'warning')
        else:
            # Check if sport has reached capacity
            if len(enrolled_students) >= sport.capacity:
                flash(f'Sport has reached maximum capacity of {sport.capacity} students', 'danger')
            else:
                # Enroll student
                sport.students.append(student)
                db.session.commit()
                flash(f'{student.user.first_name} {student.user.last_name} enrolled successfully!', 'success')

        return redirect(url_for('admin.sport_students', sport_id=sport_id))

    return render_template('admin/sports/students.html',
                          title=f'Student Enrollment - {sport.name}',
                          sport=sport,
                          enrolled_students=enrolled_students,
                          form=form)

@admin_bp.route('/sports/<int:sport_id>/students/remove/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def sport_student_remove(sport_id, student_id):
    sport = Sport.query.get_or_404(sport_id)
    student = StudentProfile.query.get_or_404(student_id)

    # Check if student is enrolled
    if student not in sport.students:
        flash(f'{student.user.first_name} {student.user.last_name} is not enrolled in this sport', 'warning')
        return redirect(url_for('admin.sport_students', sport_id=sport_id))

    # Check if student has attendance records
    attendance_count = SportsAttendance.query.filter_by(sport_id=sport_id, student_id=student_id).count()
    if attendance_count > 0:
        flash(f'Cannot remove student with attendance records. Delete attendance records first.', 'danger')
        return redirect(url_for('admin.sport_students', sport_id=sport_id))

    # Check if student has fee payments
    payment_count = SportFeePayment.query.filter_by(sport_id=sport_id, student_id=student_id).count()
    if payment_count > 0:
        flash(f'Cannot remove student with fee payments. Delete fee payments first.', 'danger')
        return redirect(url_for('admin.sport_students', sport_id=sport_id))

    # Remove student from sport
    sport.students.remove(student)
    db.session.commit()
    flash(f'{student.user.first_name} {student.user.last_name} removed from {sport.name}', 'success')
    return redirect(url_for('admin.sport_students', sport_id=sport_id))

@admin_bp.route('/classes/create', methods=['GET', 'POST'])
@login_required
@admin_required
def class_create():
    form = ClassAssignmentForm()
    form.standard_id.choices = [(s.id, s.name) for s in Standard.query.order_by(Standard.name).all()]
    form.teacher_id.choices = [(t.id, f"{t.user.get_full_name()} ({t.primary_subject})") for t in TeacherProfile.query.join(User).order_by(User.first_name, User.last_name).all()]

    # Dynamically update sections based on selected standard
    if request.method == 'GET' and request.args.get('standard_id'):
        standard_id = int(request.args.get('standard_id'))
        sections = Section.query.filter_by(standard_id=standard_id).order_by(Section.name).all()
        form.section_id.choices = [(0, 'None')] + [(s.id, s.name) for s in sections]
    else:
        form.section_id.choices = [(0, 'None')]

    if form.validate_on_submit():
        class_obj = Class(
            name=form.name.data,
            standard_id=form.standard_id.data,
            section_id=form.section_id.data if form.section_id.data != 0 else None,
            subject=form.subject.data,
            teacher_id=form.teacher_id.data,
            schedule=form.schedule.data,
            room=form.room.data,
            academic_year=form.academic_year.data,
            is_active=form.is_active.data
        )

        db.session.add(class_obj)
        db.session.commit()
        flash('Class created successfully', 'success')
        return redirect(url_for('admin.class_list'))

    return render_template('admin/classes/create.html', title='Create Class', form=form)

@admin_bp.route('/classes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def class_edit(id):
    class_obj = Class.query.get_or_404(id)
    form = ClassAssignmentForm(obj=class_obj)

    form.standard_id.choices = [(s.id, s.name) for s in Standard.query.order_by(Standard.name).all()]
    form.teacher_id.choices = [(t.id, f"{t.user.get_full_name()} ({t.primary_subject})") for t in TeacherProfile.query.join(User).order_by(User.first_name, User.last_name).all()]

    # Load sections for the current standard
    sections = Section.query.filter_by(standard_id=class_obj.standard_id).order_by(Section.name).all()
    form.section_id.choices = [(0, 'None')] + [(s.id, s.name) for s in sections]

    if form.validate_on_submit():
        class_obj.name = form.name.data
        class_obj.standard_id = form.standard_id.data
        class_obj.section_id = form.section_id.data if form.section_id.data != 0 else None
        class_obj.subject = form.subject.data
        class_obj.teacher_id = form.teacher_id.data
        class_obj.schedule = form.schedule.data
        class_obj.room = form.room.data
        class_obj.academic_year = form.academic_year.data
        class_obj.is_active = form.is_active.data
        class_obj.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Class updated successfully', 'success')
        return redirect(url_for('admin.class_list'))

    return render_template('admin/classes/edit.html', title='Edit Class', form=form, class_obj=class_obj)

@admin_bp.route('/classes/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def class_delete(id):
    class_obj = Class.query.get_or_404(id)

    # Check if class has attendances
    if class_obj.attendances.count() > 0:
        flash('Cannot delete class with attendance records.', 'danger')
        return redirect(url_for('admin.class_list'))

    # Check if class has homeworks
    if class_obj.homeworks.count() > 0:
        flash('Cannot delete class with homework records.', 'danger')
        return redirect(url_for('admin.class_list'))

    db.session.delete(class_obj)
    db.session.commit()
    flash('Class deleted successfully', 'success')
    return redirect(url_for('admin.class_list'))
