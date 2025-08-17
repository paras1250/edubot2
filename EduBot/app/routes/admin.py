from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Faculty, Course, Event, Attendance, ChatLog
from app.models.note import Note
from app.models.quick_action import QuickAction
from werkzeug.security import generate_password_hash
from datetime import datetime, date, time, timedelta
from wtforms.validators import DataRequired, Length, EqualTo
from sqlalchemy import func, desc, and_
from collections import defaultdict
import re
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    # Get basic statistics for dashboard
    try:
        total_users = User.query.count()
        total_conversations = ChatLog.query.count()
        
        # Active users today
        today = datetime.now().date()
        active_today = db.session.query(ChatLog.user_id).filter(
            func.date(ChatLog.created_at) == today
        ).distinct().count()
        
        # Average response time
        avg_response_time = db.session.query(
            func.avg(ChatLog.response_time_ms)
        ).filter(
            ChatLog.response_time_ms.isnot(None)
        ).scalar()
        avg_response_time = round(avg_response_time) if avg_response_time else 0
        
    except Exception as e:
        # Fallback values if there's an error
        total_users = 0
        total_conversations = 0
        active_today = 0
        avg_response_time = 0
    
    return render_template('admin/dashboard.html', 
                         user=current_user,
                         total_users=total_users,
                         total_conversations=total_conversations,
                         active_today=active_today,
                         avg_response_time=avg_response_time)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """List all users with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    role_filter = request.args.get('role', '', type=str)
    
    per_page = 20
    
    # Build query with filters
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    users = query.order_by(User.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', 
                         users=users, 
                         search=search, 
                         role_filter=role_filter,
                         user=current_user)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add new user"""
    from app.forms import UserForm
    
    form = UserForm()
    
    # For new users, password is required
    form.password.validators = [DataRequired(message='Password is required'), 
                               Length(min=6, message='Password must be at least 6 characters long')]
    form.confirm_password.validators = [DataRequired(message='Please confirm password'),
                                       EqualTo('password', message='Passwords must match')]
    
    if form.validate_on_submit():
        # Check if username exists
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append('Username already exists')
            return render_template('admin/user_form.html', 
                                 form=form,
                                 mode='add',
                                 user=current_user)
        
        # Check if email exists
        if User.query.filter_by(email=form.email.data).first():
            form.email.errors.append('Email already exists')
            return render_template('admin/user_form.html', 
                                 form=form,
                                 mode='add',
                                 user=current_user)
        
        # Create new user
        try:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role=form.role.data,
                password_hash=generate_password_hash(form.password.data),
                is_active=form.is_active.data,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'User {form.username.data} created successfully!', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating user. Please try again.', 'error')
    
    return render_template('admin/user_form.html', 
                         form=form,
                         mode='add', 
                         user=current_user)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit existing user"""
    from app.forms import UserForm
    
    user_to_edit = User.query.get_or_404(user_id)
    form = UserForm()
    
    if request.method == 'GET':
        # Pre-populate form with existing user data
        form.username.data = user_to_edit.username
        form.email.data = user_to_edit.email
        form.first_name.data = user_to_edit.first_name
        form.last_name.data = user_to_edit.last_name
        form.role.data = user_to_edit.role
        form.is_active.data = user_to_edit.is_active
    
    if form.validate_on_submit():
        # Check if username exists for other users
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != user_id:
            form.username.errors.append('Username already exists')
            return render_template('admin/user_form.html', 
                                 form=form,
                                 form_user=user_to_edit, 
                                 mode='edit',
                                 user=current_user)
        
        # Check if email exists for other users
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email and existing_email.id != user_id:
            form.email.errors.append('Email already exists')
            return render_template('admin/user_form.html', 
                                 form=form,
                                 form_user=user_to_edit, 
                                 mode='edit',
                                 user=current_user)
        
        # Update user
        try:
            user_to_edit.username = form.username.data
            user_to_edit.email = form.email.data
            user_to_edit.first_name = form.first_name.data
            user_to_edit.last_name = form.last_name.data
            user_to_edit.role = form.role.data
            user_to_edit.is_active = form.is_active.data
            
            # Only update password if provided
            if form.password.data:
                user_to_edit.password_hash = generate_password_hash(form.password.data)
            
            db.session.commit()
            
            flash(f'User {form.username.data} updated successfully!', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating user. Please try again.', 'error')
    
    return render_template('admin/user_form.html', 
                         form=form,
                         form_user=user_to_edit, 
                         mode='edit', 
                         user=current_user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user"""
    user_to_delete = User.query.get_or_404(user_id)
    
    # Prevent deleting current user
    if user_to_delete.id == current_user.id:
        flash('You cannot delete your own account!', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        username = user_to_delete.username
        db.session.delete(user_to_delete)
        db.session.commit()
        
        flash(f'User {username} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user_to_toggle = User.query.get_or_404(user_id)
    
    # Prevent deactivating current user
    if user_to_toggle.id == current_user.id:
        return jsonify({'success': False, 'message': 'You cannot deactivate your own account!'})
    
    try:
        user_to_toggle.is_active = not user_to_toggle.is_active
        db.session.commit()
        
        status = 'activated' if user_to_toggle.is_active else 'deactivated'
        return jsonify({
            'success': True, 
            'message': f'User {user_to_toggle.username} {status} successfully!',
            'is_active': user_to_toggle.is_active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating user status.'})

@admin_bp.route('/faculty')
@login_required
@admin_required
def manage_faculty():
    """List all faculty with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    department_filter = request.args.get('department', '', type=str)
    
    per_page = 20
    
    # Build query with filters
    query = Faculty.query.join(User, Faculty.user_id == User.id)
    
    if search:
        query = query.filter(
            db.or_(
                Faculty.employee_id.ilike(f'%{search}%'),
                Faculty.department.ilike(f'%{search}%'),
                Faculty.designation.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    if department_filter:
        query = query.filter(Faculty.department == department_filter)
    
    faculty_members = query.order_by(Faculty.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get unique departments for filter
    departments = db.session.query(Faculty.department).distinct().order_by(Faculty.department).all()
    departments = [dept[0] for dept in departments if dept[0]]
    
    return render_template('admin/faculty.html', 
                         faculty_members=faculty_members, 
                         search=search, 
                         department_filter=department_filter,
                         departments=departments,
                         user=current_user)

@admin_bp.route('/faculty/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_faculty():
    """Add new faculty member"""
    if request.method == 'POST':
        # Get form data
        employee_id = request.form.get('employee_id', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        department = request.form.get('department', '').strip()
        designation = request.form.get('designation', '').strip()
        specialization = request.form.get('specialization', '').strip()
        office_location = request.form.get('office_location', '').strip()
        office_hours = request.form.get('office_hours', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Validation
        errors = []
        
        if not employee_id:
            errors.append('Employee ID is required')
        elif Faculty.query.filter_by(employee_id=employee_id).first():
            errors.append('Employee ID already exists')
        
        if not first_name:
            errors.append('First name is required')
        
        if not last_name:
            errors.append('Last name is required')
        
        if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors.append('Valid email is required')
        elif User.query.filter_by(email=email).first():
            errors.append('Email already exists')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        if not department:
            errors.append('Department is required')
        
        if not designation:
            errors.append('Designation is required')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/faculty_form.html', 
                                 form_data=request.form, 
                                 mode='add',
                                 user=current_user)
        
        # Generate username from employee ID
        username = f"fac_{employee_id}"
        
        # Create new user first
        try:
            new_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='faculty',
                password_hash=generate_password_hash(password),
                phone=phone if phone else None,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_user)
            db.session.flush()  # Flush to get the user ID
            
            # Create faculty profile
            new_faculty = Faculty(
                user_id=new_user.id,
                employee_id=employee_id,
                department=department,
                designation=designation,
                specialization=specialization if specialization else None,
                office_location=office_location if office_location else None,
                office_hours=office_hours if office_hours else None,
                bio=bio if bio else None,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_faculty)
            db.session.commit()
            
            flash(f'Faculty member {first_name} {last_name} created successfully!', 'success')
            return redirect(url_for('admin.manage_faculty'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating faculty member. Please try again.', 'error')
            return render_template('admin/faculty_form.html', 
                                 form_data=request.form, 
                                 mode='add',
                                 user=current_user)
    
    return render_template('admin/faculty_form.html', mode='add', user=current_user)

@admin_bp.route('/faculty/<int:faculty_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_faculty(faculty_id):
    """Edit existing faculty member"""
    faculty_to_edit = Faculty.query.get_or_404(faculty_id)
    
    if request.method == 'POST':
        # Get form data
        employee_id = request.form.get('employee_id', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '').strip()
        department = request.form.get('department', '').strip()
        designation = request.form.get('designation', '').strip()
        specialization = request.form.get('specialization', '').strip()
        office_location = request.form.get('office_location', '').strip()
        office_hours = request.form.get('office_hours', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        is_active = 'is_active' in request.form
        
        # Validation
        errors = []
        
        if not employee_id:
            errors.append('Employee ID is required')
        else:
            existing_faculty = Faculty.query.filter_by(employee_id=employee_id).first()
            if existing_faculty and existing_faculty.id != faculty_id:
                errors.append('Employee ID already exists')
        
        if not first_name:
            errors.append('First name is required')
        
        if not last_name:
            errors.append('Last name is required')
        
        if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            errors.append('Valid email is required')
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != faculty_to_edit.user_id:
                errors.append('Email already exists')
        
        if new_password and len(new_password) < 6:
            errors.append('New password must be at least 6 characters long')
        
        if not department:
            errors.append('Department is required')
        
        if not designation:
            errors.append('Designation is required')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/faculty_form.html', 
                                 faculty_to_edit=faculty_to_edit, 
                                 form_data=request.form, 
                                 mode='edit',
                                 user=current_user)
        
        # Update faculty and user
        try:
            # Update user
            faculty_to_edit.user.first_name = first_name
            faculty_to_edit.user.last_name = last_name
            faculty_to_edit.user.email = email
            faculty_to_edit.user.phone = phone if phone else None
            faculty_to_edit.user.is_active = is_active
            
            if new_password:
                faculty_to_edit.user.password_hash = generate_password_hash(new_password)
            
            # Update faculty profile
            faculty_to_edit.employee_id = employee_id
            faculty_to_edit.department = department
            faculty_to_edit.designation = designation
            faculty_to_edit.specialization = specialization if specialization else None
            faculty_to_edit.office_location = office_location if office_location else None
            faculty_to_edit.office_hours = office_hours if office_hours else None
            faculty_to_edit.bio = bio if bio else None
            faculty_to_edit.is_active = is_active
            faculty_to_edit.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Faculty member {first_name} {last_name} updated successfully!', 'success')
            return redirect(url_for('admin.manage_faculty'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating faculty member. Please try again.', 'error')
            return render_template('admin/faculty_form.html', 
                                 faculty_to_edit=faculty_to_edit, 
                                 form_data=request.form, 
                                 mode='edit',
                                 user=current_user)
    
    return render_template('admin/faculty_form.html', 
                         faculty_to_edit=faculty_to_edit, 
                         mode='edit', 
                         user=current_user)

@admin_bp.route('/faculty/<int:faculty_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_faculty(faculty_id):
    """Delete faculty member"""
    faculty_to_delete = Faculty.query.get_or_404(faculty_id)
    
    try:
        faculty_name = faculty_to_delete.name
        # Delete faculty (user will be deleted due to cascade)
        db.session.delete(faculty_to_delete.user)
        db.session.commit()
        
        flash(f'Faculty member {faculty_name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting faculty member. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_faculty'))

@admin_bp.route('/courses')
@login_required
@admin_required
def manage_courses():
    """List all courses with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    department_filter = request.args.get('department', '', type=str)
    
    per_page = 20
    
    # Build query with filters
    query = Course.query
    
    if search:
        query = query.filter(
            db.or_(
                Course.course_code.ilike(f'%{search}%'),
                Course.course_name.ilike(f'%{search}%'),
                Course.description.ilike(f'%{search}%'),
                Course.department.ilike(f'%{search}%')
            )
        )
    
    if department_filter:
        query = query.filter(Course.department == department_filter)
    
    courses = query.order_by(Course.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get unique departments for filter
    departments = db.session.query(Course.department).distinct().order_by(Course.department).all()
    departments = [dept[0] for dept in departments if dept[0]]
    
    return render_template('admin/courses.html', 
                         courses=courses, 
                         search=search, 
                         department_filter=department_filter,
                         departments=departments,
                         user=current_user)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    """Add new course"""
    if request.method == 'POST':
        # Get form data
        course_code = request.form.get('course_code', '').strip().upper()
        course_name = request.form.get('course_name', '').strip()
        description = request.form.get('description', '').strip()
        credits = request.form.get('credits', type=int)
        semester = request.form.get('semester', type=int)
        year = request.form.get('year', type=int)
        department = request.form.get('department', '').strip()
        faculty_id = request.form.get('faculty_id', type=int)
        
        # Validation
        errors = []
        
        if not course_code or len(course_code) < 2:
            errors.append('Course code must be at least 2 characters long')
        elif Course.query.filter_by(course_code=course_code).first():
            errors.append('Course code already exists')
        
        if not course_name or len(course_name) < 3:
            errors.append('Course name must be at least 3 characters long')
        
        if not credits or credits < 1 or credits > 10:
            errors.append('Credits must be between 1 and 10')
        
        if not semester or semester < 1 or semester > 8:
            errors.append('Semester must be between 1 and 8')
        
        if not year or year < 2020 or year > 2030:
            errors.append('Year must be between 2020 and 2030')
        
        if not department:
            errors.append('Department is required')
        
        if faculty_id:
            faculty = Faculty.query.get(faculty_id)
            if not faculty:
                errors.append('Invalid faculty selected')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            # Get faculty for form
            faculty_members = Faculty.query.join(User).filter(User.is_active == True).order_by(User.first_name, User.last_name).all()
            return render_template('admin/course_form.html', 
                                 form_data=request.form,
                                 faculty_members=faculty_members,
                                 mode='add',
                                 user=current_user)
        
        # Create new course
        try:
            new_course = Course(
                course_code=course_code,
                course_name=course_name,
                description=description if description else None,
                credits=credits,
                semester=semester,
                year=year,
                department=department,
                faculty_id=faculty_id if faculty_id else None,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_course)
            db.session.commit()
            
            flash(f'Course "{course_code} - {course_name}" created successfully!', 'success')
            return redirect(url_for('admin.manage_courses'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating course. Please try again.', 'error')
            # Get faculty for form
            faculty_members = Faculty.query.join(User).filter(User.is_active == True).order_by(User.first_name, User.last_name).all()
            return render_template('admin/course_form.html', 
                                 form_data=request.form,
                                 faculty_members=faculty_members,
                                 mode='add',
                                 user=current_user)
    
    # Get faculty for form
    faculty_members = Faculty.query.join(User).filter(User.is_active == True).order_by(User.first_name, User.last_name).all()
    return render_template('admin/course_form.html',
                         faculty_members=faculty_members,
                         mode='add',
                         user=current_user)

@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    """Edit existing course"""
    course_to_edit = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        # Get form data
        course_code = request.form.get('course_code', '').strip().upper()
        course_name = request.form.get('course_name', '').strip()
        description = request.form.get('description', '').strip()
        credits = request.form.get('credits', type=int)
        semester = request.form.get('semester', type=int)
        year = request.form.get('year', type=int)
        department = request.form.get('department', '').strip()
        faculty_id = request.form.get('faculty_id', type=int)
        is_active = 'is_active' in request.form
        
        # Validation
        errors = []
        
        if not course_code or len(course_code) < 2:
            errors.append('Course code must be at least 2 characters long')
        else:
            existing_course = Course.query.filter_by(course_code=course_code).first()
            if existing_course and existing_course.id != course_id:
                errors.append('Course code already exists')
        
        if not course_name or len(course_name) < 3:
            errors.append('Course name must be at least 3 characters long')
        
        if not credits or credits < 1 or credits > 10:
            errors.append('Credits must be between 1 and 10')
        
        if not semester or semester < 1 or semester > 8:
            errors.append('Semester must be between 1 and 8')
        
        if not year or year < 2020 or year > 2030:
            errors.append('Year must be between 2020 and 2030')
        
        if not department:
            errors.append('Department is required')
        
        if faculty_id:
            faculty = Faculty.query.get(faculty_id)
            if not faculty:
                errors.append('Invalid faculty selected')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            # Get faculty for form
            faculty_members = Faculty.query.join(User).filter(User.is_active == True).order_by(User.first_name, User.last_name).all()
            return render_template('admin/course_form.html', 
                                 course_to_edit=course_to_edit,
                                 form_data=request.form,
                                 faculty_members=faculty_members,
                                 mode='edit',
                                 user=current_user)
        
        # Update course
        try:
            course_to_edit.course_code = course_code
            course_to_edit.course_name = course_name
            course_to_edit.description = description if description else None
            course_to_edit.credits = credits
            course_to_edit.semester = semester
            course_to_edit.year = year
            course_to_edit.department = department
            course_to_edit.faculty_id = faculty_id if faculty_id else None
            course_to_edit.is_active = is_active
            course_to_edit.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Course "{course_code} - {course_name}" updated successfully!', 'success')
            return redirect(url_for('admin.manage_courses'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating course. Please try again.', 'error')
            # Get faculty for form
            faculty_members = Faculty.query.join(User).filter(User.is_active == True).order_by(User.first_name, User.last_name).all()
            return render_template('admin/course_form.html', 
                                 course_to_edit=course_to_edit,
                                 form_data=request.form,
                                 faculty_members=faculty_members,
                                 mode='edit',
                                 user=current_user)
    
    # Get faculty for form
    faculty_members = Faculty.query.join(User).filter(User.is_active == True).order_by(User.first_name, User.last_name).all()
    return render_template('admin/course_form.html', 
                         course_to_edit=course_to_edit,
                         faculty_members=faculty_members,
                         mode='edit',
                         user=current_user)

@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    """Delete course"""
    course_to_delete = Course.query.get_or_404(course_id)
    
    try:
        course_name = f"{course_to_delete.course_code} - {course_to_delete.course_name}"
        db.session.delete(course_to_delete)
        db.session.commit()
        
        flash(f'Course "{course_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting course. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_courses'))

@admin_bp.route('/courses/<int:course_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_course_status(course_id):
    """Toggle course active status"""
    course_to_toggle = Course.query.get_or_404(course_id)
    
    try:
        course_to_toggle.is_active = not course_to_toggle.is_active
        course_to_toggle.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activated' if course_to_toggle.is_active else 'deactivated'
        return jsonify({
            'success': True, 
            'message': f'Course "{course_to_toggle.course_code}" {status} successfully!',
            'is_active': course_to_toggle.is_active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating course status.'})

@admin_bp.route('/events')
@login_required
@admin_required
def manage_events():
    """List all events with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    event_type_filter = request.args.get('event_type', '', type=str)
    
    per_page = 20
    
    # Build query with filters
    query = Event.query
    
    if search:
        query = query.filter(
            db.or_(
                Event.title.ilike(f'%{search}%'),
                Event.description.ilike(f'%{search}%'),
                Event.location.ilike(f'%{search}%'),
                Event.organizer.ilike(f'%{search}%')
            )
        )
    
    if event_type_filter:
        query = query.filter(Event.event_type == event_type_filter)
    
    events = query.order_by(Event.start_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    event_types = ['academic', 'cultural', 'sports', 'holiday', 'exam', 'other']
    
    return render_template('admin/events.html', 
                         events=events, 
                         search=search, 
                         event_type_filter=event_type_filter,
                         event_types=event_types,
                         user=current_user)

@admin_bp.route('/events/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    """Add new event"""
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        event_type = request.form.get('event_type', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        location = request.form.get('location', '').strip()
        organizer = request.form.get('organizer', '').strip()
        is_holiday = 'is_holiday' in request.form
        
        # Validation
        errors = []
        
        if not title or len(title) < 3:
            errors.append('Event title must be at least 3 characters long')
        
        if not event_type or event_type not in ['academic', 'cultural', 'sports', 'holiday', 'exam', 'other']:
            errors.append('Valid event type is required')
        
        if not start_date_str:
            errors.append('Start date is required')
        
        # Parse dates and times
        start_date = None
        end_date = None
        start_time = None
        end_time = None
        
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if end_date < start_date:
                    errors.append('End date cannot be before start date')
            
            if start_time_str:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
            
            if end_time_str:
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
                
        except ValueError as e:
            errors.append('Invalid date or time format')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/event_form.html', 
                                 form_data=request.form, 
                                 mode='add',
                                 event_types=['academic', 'cultural', 'sports', 'holiday', 'exam', 'other'],
                                 user=current_user)
        
        # Create new event
        try:
            new_event = Event(
                title=title,
                description=description if description else None,
                event_type=event_type,
                start_date=start_date,
                end_date=end_date if end_date_str else None,
                start_time=start_time if start_time_str else None,
                end_time=end_time if end_time_str else None,
                location=location if location else None,
                organizer=organizer if organizer else None,
                is_holiday=is_holiday,
                is_active=True,
                created_by=current_user.id,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_event)
            db.session.commit()
            
            flash(f'Event "{title}" created successfully!', 'success')
            return redirect(url_for('admin.manage_events'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error creating event. Please try again.', 'error')
            return render_template('admin/event_form.html', 
                                 form_data=request.form, 
                                 mode='add',
                                 event_types=['academic', 'cultural', 'sports', 'holiday', 'exam', 'other'],
                                 user=current_user)
    
    return render_template('admin/event_form.html', 
                         mode='add',
                         event_types=['academic', 'cultural', 'sports', 'holiday', 'exam', 'other'],
                         user=current_user)

@admin_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    """Edit existing event"""
    event_to_edit = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        event_type = request.form.get('event_type', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        location = request.form.get('location', '').strip()
        organizer = request.form.get('organizer', '').strip()
        is_holiday = 'is_holiday' in request.form
        is_active = 'is_active' in request.form
        
        # Validation
        errors = []
        
        if not title or len(title) < 3:
            errors.append('Event title must be at least 3 characters long')
        
        if not event_type or event_type not in ['academic', 'cultural', 'sports', 'holiday', 'exam', 'other']:
            errors.append('Valid event type is required')
        
        if not start_date_str:
            errors.append('Start date is required')
        
        # Parse dates and times
        start_date = None
        end_date = None
        start_time = None
        end_time = None
        
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if end_date < start_date:
                    errors.append('End date cannot be before start date')
            
            if start_time_str:
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
            
            if end_time_str:
                end_time = datetime.strptime(end_time_str, '%H:%M').time()
                
        except ValueError as e:
            errors.append('Invalid date or time format')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/event_form.html', 
                                 event_to_edit=event_to_edit, 
                                 form_data=request.form, 
                                 mode='edit',
                                 event_types=['academic', 'cultural', 'sports', 'holiday', 'exam', 'other'],
                                 user=current_user)
        
        # Update event
        try:
            event_to_edit.title = title
            event_to_edit.description = description if description else None
            event_to_edit.event_type = event_type
            event_to_edit.start_date = start_date
            event_to_edit.end_date = end_date if end_date_str else None
            event_to_edit.start_time = start_time if start_time_str else None
            event_to_edit.end_time = end_time if end_time_str else None
            event_to_edit.location = location if location else None
            event_to_edit.organizer = organizer if organizer else None
            event_to_edit.is_holiday = is_holiday
            event_to_edit.is_active = is_active
            event_to_edit.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Event "{title}" updated successfully!', 'success')
            return redirect(url_for('admin.manage_events'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating event. Please try again.', 'error')
            return render_template('admin/event_form.html', 
                                 event_to_edit=event_to_edit, 
                                 form_data=request.form, 
                                 mode='edit',
                                 event_types=['academic', 'cultural', 'sports', 'holiday', 'exam', 'other'],
                                 user=current_user)
    
    return render_template('admin/event_form.html', 
                         event_to_edit=event_to_edit, 
                         mode='edit',
                         event_types=['academic', 'cultural', 'sports', 'holiday', 'exam', 'other'],
                         user=current_user)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    """Delete event"""
    event_to_delete = Event.query.get_or_404(event_id)
    
    try:
        event_title = event_to_delete.title
        db.session.delete(event_to_delete)
        db.session.commit()
        
        flash(f'Event "{event_title}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting event. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_events'))

@admin_bp.route('/events/<int:event_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_event_status(event_id):
    """Toggle event active status"""
    event_to_toggle = Event.query.get_or_404(event_id)
    
    try:
        event_to_toggle.is_active = not event_to_toggle.is_active
        event_to_toggle.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'activated' if event_to_toggle.is_active else 'deactivated'
        return jsonify({
            'success': True, 
            'message': f'Event "{event_to_toggle.title}" {status} successfully!',
            'is_active': event_to_toggle.is_active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error updating event status.'})

@admin_bp.route('/notes', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_notes():
    """Manage notes: view, add, and delete"""
    from app.forms import NoteForm

    form = NoteForm()
    
    # Get available courses for the form
    courses = Course.query.filter_by(is_active=True).order_by(Course.course_name).all()
    form.course_id.choices = [(0, 'Select a Course')] + [(course.id, f"{course.course_name} ({course.course_code})") for course in courses]

    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        course_id = form.course_id.data
        content = form.content.data
        topic = form.topic.data
        chapter = form.chapter.data
        uploaded_file = form.uploaded_file.data

        try:
            # Ensure upload directory exists
            upload_dir = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Generate secure filename
            filename = secure_filename(uploaded_file.filename)
            if not filename:
                flash('Invalid filename', 'error')
                return render_template('admin/notes.html', notes=Note.query.order_by(Note.created_at.desc()).all(), form=form, user=current_user)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            uploaded_file.save(file_path)

            # Create new note
            new_note = Note(
                course_id=course_id,
                title=title,
                content=content,
                topic=topic,
                chapter=chapter,
                file_name=filename,
                original_name=uploaded_file.filename,
                file_path=f'uploads/{filename}',  # Relative path for web access
                file_size=os.path.getsize(file_path),
                file_type=uploaded_file.content_type,
                uploaded_by=current_user.id
            )

            db.session.add(new_note)
            db.session.commit()

            flash('Note added successfully!', 'success')
            return redirect(url_for('admin.manage_notes'))
            
        except Exception as e:
            flash(f'Error uploading note: {str(e)}', 'error')
            db.session.rollback()

    # Get all notes with related data
    notes = Note.query.join(Course, Note.course_id == Course.id, isouter=True).order_by(Note.created_at.desc()).all()
    courses = Course.query.filter_by(is_active=True).all()
    
    return render_template('admin/notes.html', notes=notes, courses=courses, form=form, user=current_user)

@admin_bp.route('/attendance')
@login_required
@admin_required
def manage_attendance():
    """List all attendance records with pagination and search"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    date_filter = request.args.get('date', '', type=str)
    
    per_page = 20
    
    # Build query with filters
    query = Attendance.query.join(User, Attendance.student_id == User.id)
    
    if search:
        query = query.filter(
            db.or_(
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%'),
                User.student_id.ilike(f'%{search}%')
            )
        )
    
    if status_filter:
        query = query.filter(Attendance.status == status_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == filter_date)
        except ValueError:
            pass
    
    attendance_records = query.order_by(Attendance.date.desc(), Attendance.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/attendance.html', 
                         attendance_records=attendance_records, 
                         search=search, 
                         status_filter=status_filter,
                         date_filter=date_filter,
                         user=current_user)

@admin_bp.route('/attendance/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_attendance():
    """Add new attendance record"""
    if request.method == 'POST':
        # Get form data
        student_id = request.form.get('student_id', '', type=int)
        course_id = request.form.get('course_id', '', type=int)
        date_str = request.form.get('date', '').strip()
        status = request.form.get('status', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validation
        errors = []
        
        if not student_id:
            errors.append('Student is required')
        else:
            student = User.query.filter_by(id=student_id, role='student').first()
            if not student:
                errors.append('Invalid student selected')
        
        if not course_id:
            errors.append('Course is required')
        else:
            course = Course.query.get(course_id)
            if not course:
                errors.append('Invalid course selected')
        
        if not date_str:
            errors.append('Date is required')
        
        if not status or status not in ['present', 'absent', 'late']:
            errors.append('Valid status is required')
        
        # Parse date
        attendance_date = None
        try:
            if date_str:
                attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            errors.append('Invalid date format')
        
        # Check for duplicate attendance
        if not errors and student_id and course_id and attendance_date:
            existing = Attendance.query.filter_by(
                student_id=student_id,
                course_id=course_id,
                date=attendance_date
            ).first()
            if existing:
                errors.append('Attendance already recorded for this student, course, and date')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            # Get students and courses for form
            students = User.query.filter_by(role='student', is_active=True).order_by(User.first_name, User.last_name).all()
            courses = Course.query.filter_by(is_active=True).order_by(Course.name).all()
            return render_template('admin/attendance_form.html', 
                                 form_data=request.form,
                                 students=students,
                                 courses=courses,
                                 mode='add',
                                 user=current_user)
        
        # Create new attendance record
        try:
            new_attendance = Attendance(
                student_id=student_id,
                course_id=course_id,
                date=attendance_date,
                status=status,
                marked_by=current_user.id,
                notes=notes if notes else None,
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_attendance)
            db.session.commit()
            
            flash(f'Attendance recorded successfully!', 'success')
            return redirect(url_for('admin.manage_attendance'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error recording attendance. Please try again.', 'error')
            # Get students and courses for form
            students = User.query.filter_by(role='student', is_active=True).order_by(User.first_name, User.last_name).all()
            courses = Course.query.filter_by(is_active=True).order_by(Course.course_name).all()
            return render_template('admin/attendance_form.html', 
                                 form_data=request.form,
                                 students=students,
                                 courses=courses,
                                 mode='add',
                                 user=current_user)
    
    # Get students and courses for form
    students = User.query.filter_by(role='student', is_active=True).order_by(User.first_name, User.last_name).all()
    courses = Course.query.filter_by(is_active=True).order_by(Course.course_name).all()
    return render_template('admin/attendance_form.html',
                         students=students,
                         courses=courses,
                         mode='add',
                         user=current_user)

@admin_bp.route('/attendance/<int:attendance_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_attendance(attendance_id):
    """Edit existing attendance record"""
    attendance_to_edit = Attendance.query.get_or_404(attendance_id)
    
    if request.method == 'POST':
        # Get form data
        status = request.form.get('status', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validation
        errors = []
        
        if not status or status not in ['present', 'absent', 'late']:
            errors.append('Valid status is required')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/attendance_form.html', 
                                 attendance_to_edit=attendance_to_edit,
                                 form_data=request.form,
                                 mode='edit',
                                 user=current_user)
        
        # Update attendance record
        try:
            attendance_to_edit.status = status
            attendance_to_edit.notes = notes if notes else None
            attendance_to_edit.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Attendance updated successfully!', 'success')
            return redirect(url_for('admin.manage_attendance'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating attendance. Please try again.', 'error')
            return render_template('admin/attendance_form.html', 
                                 attendance_to_edit=attendance_to_edit,
                                 form_data=request.form,
                                 mode='edit',
                                 user=current_user)
    
    return render_template('admin/attendance_form.html', 
                         attendance_to_edit=attendance_to_edit,
                         mode='edit',
                         user=current_user)

@admin_bp.route('/attendance/<int:attendance_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_attendance(attendance_id):
    """Delete attendance record"""
    attendance_to_delete = Attendance.query.get_or_404(attendance_id)
    
    try:
        db.session.delete(attendance_to_delete)
        db.session.commit()
        
        flash(f'Attendance record deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting attendance record. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_attendance'))


@admin_bp.route('/quick_actions', methods=['GET'])
@login_required
@admin_required
def list_quick_actions():
    """List all quick actions"""
    quick_actions = QuickAction.query.all()
    return render_template('admin/quick_actions.html', quick_actions=quick_actions)


@admin_bp.route('/quick_actions/add', methods=['POST'])
@login_required
@admin_required
def add_quick_action():
    """Add a new quick action"""
    data = request.json
    quick_action = QuickAction(
        question=data.get('question'),
        response=data.get('response'),
        category=data.get('category'),
        keywords=data.get('keywords'),
        is_active=data.get('is_active', True),
        priority=data.get('priority', 5),
        created_by=current_user.id
    )
    db.session.add(quick_action)
    db.session.commit()
    return jsonify(success=True, message='Quick Action added successfully'), 201


@admin_bp.route('/quick_actions/edit/<int:qa_id>', methods=['PUT'])
@login_required
@admin_required
def edit_quick_action(qa_id):
    """Edit an existing quick action"""
    quick_action = QuickAction.query.get_or_404(qa_id)
    data = request.json
    quick_action.question = data.get('question', quick_action.question)
    quick_action.response = data.get('response', quick_action.response)
    quick_action.category = data.get('category', quick_action.category)
    quick_action.keywords = data.get('keywords', quick_action.keywords)
    quick_action.is_active = data.get('is_active', quick_action.is_active)
    quick_action.priority = data.get('priority', quick_action.priority)
    db.session.commit()
    return jsonify(success=True, message='Quick Action updated successfully')


@admin_bp.route('/quick_actions/<int:qa_id>', methods=['GET'])
@login_required
@admin_required
def get_quick_action(qa_id):
    """Get a single quick action for editing"""
    quick_action = QuickAction.query.get_or_404(qa_id)
    return jsonify(quick_action.to_dict())

@admin_bp.route('/quick_actions/delete/<int:qa_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_quick_action(qa_id):
    """Delete a quick action"""
    quick_action = QuickAction.query.get_or_404(qa_id)
    db.session.delete(quick_action)
    db.session.commit()
    return jsonify(success=True, message='Quick Action deleted successfully')

@admin_bp.route('/users/<int:user_id>/view-password')
@login_required
@admin_required
def view_user_password(user_id):
    """View user password (admin only)"""
    user_to_view = User.query.get_or_404(user_id)
    
    # For security, we'll show the hashed password and indicate it's hashed
    # In a real application, you might want to implement a different approach
    return jsonify({
        'success': True,
        'username': user_to_view.username,
        'password_note': 'Password is hashed for security. Use "Reset Password" to set a new one.',
        'password_hash': user_to_view.password_hash[:50] + '...' if user_to_view.password_hash else 'No password set'
    })

@admin_bp.route('/chat-analytics')
@login_required
@admin_required
def chat_analytics():
    """Chat Analytics Dashboard"""
    # Get date filters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Base query
    query = ChatLog.query
    
    # Apply date filters if provided
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(ChatLog.created_at >= start_date_obj)
        except ValueError:
            start_date = ''
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            # Add 23:59:59 to include the entire end date
            end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
            query = query.filter(ChatLog.created_at <= end_date_obj)
        except ValueError:
            end_date = ''
    
    # Basic statistics
    total_conversations = query.count()
    
    # Conversations by day (last 30 days or filtered range)
    conversations_by_day = db.session.query(
        func.date(ChatLog.created_at).label('date'),
        func.count(ChatLog.id).label('count')
    ).filter(ChatLog.created_at >= (datetime.now() - timedelta(days=30)))
    
    if start_date and end_date:
        conversations_by_day = conversations_by_day.filter(
            ChatLog.created_at >= datetime.strptime(start_date, '%Y-%m-%d')
        ).filter(
            ChatLog.created_at <= datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        )
    
    conversations_by_day = conversations_by_day.group_by(func.date(ChatLog.created_at)).order_by('date').all()
    
    # Most common intents
    top_intents = db.session.query(
        ChatLog.intent,
        func.count(ChatLog.id).label('count')
    ).filter(ChatLog.intent.isnot(None))
    
    if start_date:
        top_intents = top_intents.filter(ChatLog.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        top_intents = top_intents.filter(ChatLog.created_at <= datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
    
    top_intents = top_intents.group_by(ChatLog.intent).order_by(desc('count')).limit(10).all()
    
    # Active users (users who have chatted)
    active_users = db.session.query(
        ChatLog.user_id,
        func.count(ChatLog.id).label('message_count'),
        func.max(ChatLog.created_at).label('last_chat')
    )
    
    if start_date:
        active_users = active_users.filter(ChatLog.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        active_users = active_users.filter(ChatLog.created_at <= datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
    
    active_users = active_users.group_by(ChatLog.user_id).order_by(desc('message_count')).limit(10).all()
    
    # Average response time
    avg_response_time = db.session.query(
        func.avg(ChatLog.response_time_ms).label('avg_time')
    )
    
    if start_date:
        avg_response_time = avg_response_time.filter(ChatLog.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        avg_response_time = avg_response_time.filter(ChatLog.created_at <= datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
    
    avg_response_time = avg_response_time.filter(ChatLog.response_time_ms.isnot(None)).scalar()
    
    # Average confidence score
    avg_confidence = db.session.query(
        func.avg(ChatLog.confidence_score).label('avg_confidence')
    )
    
    if start_date:
        avg_confidence = avg_confidence.filter(ChatLog.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        avg_confidence = avg_confidence.filter(ChatLog.created_at <= datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
    
    avg_confidence = avg_confidence.filter(ChatLog.confidence_score.isnot(None)).scalar()
    
    # Hourly distribution (24 hours)
    hourly_distribution = db.session.query(
        func.extract('hour', ChatLog.created_at).label('hour'),
        func.count(ChatLog.id).label('count')
    )
    
    if start_date:
        hourly_distribution = hourly_distribution.filter(ChatLog.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        hourly_distribution = hourly_distribution.filter(ChatLog.created_at <= datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
    
    hourly_distribution = hourly_distribution.group_by(func.extract('hour', ChatLog.created_at)).order_by('hour').all()
    
    # Get user details for active users
    active_users_with_details = []
    for user_stat in active_users:
        user = User.query.get(user_stat.user_id)
        if user:
            active_users_with_details.append({
                'user': user,
                'message_count': user_stat.message_count,
                'last_chat': user_stat.last_chat
            })
    
    # Prepare data for charts
    chart_data = {
        'daily_conversations': {
            'labels': [str(item.date) for item in conversations_by_day],
            'data': [item.count for item in conversations_by_day]
        },
        'top_intents': {
            'labels': [item.intent or 'Unknown' for item in top_intents],
            'data': [item.count for item in top_intents]
        },
        'hourly_distribution': {
            'labels': [f'{int(item.hour):02d}:00' for item in hourly_distribution],
            'data': [item.count for item in hourly_distribution]
        }
    }
    
    return render_template('admin/chat_analytics.html',
                         user=current_user,
                         total_conversations=total_conversations,
                         active_users_count=len(active_users),
                         avg_response_time=round(avg_response_time) if avg_response_time else 0,
                         avg_confidence=round(avg_confidence * 100, 2) if avg_confidence else 0,
                         active_users=active_users_with_details,
                         chart_data=chart_data,
                         start_date=start_date,
                         end_date=end_date)
