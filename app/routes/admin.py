from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User, ROLE_ADMIN
from app.models.academic import ContentBlock
from app.forms.content import ContentBlockForm
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get counts for dashboard
    total_students = User.query.filter_by(role='student', is_active=True).count()
    total_teachers = User.query.filter_by(role='teacher', is_active=True).count()
    total_parents = User.query.filter_by(role='parent', is_active=True).count()
    
    return render_template('admin/dashboard.html', 
                          title='Admin Dashboard',
                          total_students=total_students,
                          total_teachers=total_teachers,
                          total_parents=total_parents)

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
