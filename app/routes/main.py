from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models.academic import ContentBlock

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
    
    return render_template('main/index.html', title='Home', content_blocks=content_blocks)

@main_bp.route('/about')
def about():
    # Get content blocks for the about page
    content_blocks = ContentBlock.query.filter_by(location='about', is_active=True).order_by(ContentBlock.order).all()
    
    return render_template('main/about.html', title='About Us', content_blocks=content_blocks)

@main_bp.route('/contact')
def contact():
    # Get content blocks for the contact page
    content_blocks = ContentBlock.query.filter_by(location='contact', is_active=True).order_by(ContentBlock.order).all()
    
    return render_template('main/contact.html', title='Contact Us', content_blocks=content_blocks)
