from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db, limiter
from app.models.user import User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Home page route - Force fresh login for direct access"""
    # Only clear session if user is authenticated and accessing root directly
    if current_user.is_authenticated:
        logout_user()
        session.clear()
        flash('Please log in to continue.', 'info')
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    """User login route"""
    # Don't redirect authenticated users to avoid loops
    # Just proceed with login form
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        # Validation
        if not username or not password:
            flash('Please provide both username and password.', 'error')
            return render_template('auth/login.html')
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=False)  # Never remember login
            session.permanent = False  # Never make session permanent
            
            # Redirect to intended page or default
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            
            # Role-based redirect
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('chat.chat_interface'))
        else:
            flash('Invalid username/email or password.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip().title()
        last_name = request.form.get('last_name', '').strip().title()
        student_id = request.form.get('student_id', '').strip()
        year_of_study = request.form.get('year_of_study')
        phone = request.form.get('phone', '').strip()
        
        # Validation
        errors = []
        
        # Required fields
        if not all([username, email, password, confirm_password, first_name, last_name]):
            errors.append('All required fields must be filled.')
        
        # Username validation
        if len(username) < 3 or len(username) > 50:
            errors.append('Username must be between 3 and 50 characters.')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors.append('Username can only contain letters, numbers, and underscores.')
        
        # Email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Please provide a valid email address.')
        
        # Password validation
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check for existing users
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        
        if student_id and User.query.filter_by(student_id=student_id).first():
            errors.append('Student ID already registered.')
        
        # Year of study validation
        if year_of_study:
            try:
                year_of_study = int(year_of_study)
                if year_of_study < 1 or year_of_study > 6:
                    errors.append('Year of study must be between 1 and 6.')
            except ValueError:
                errors.append('Invalid year of study.')
        else:
            year_of_study = None
        
        # Phone validation
        if phone and not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone):
            errors.append('Please provide a valid phone number.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='student',
                student_id=student_id if student_id else None,
                year_of_study=year_of_study,
                phone=phone if phone else None
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            print(f"Registration error: {e}")
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/force-logout')
def force_logout():
    """Force logout route - clears session without login requirement"""
    logout_user()
    session.clear()
    flash('Session cleared. Please log in.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@limiter.limit("3 per minute")
def change_password():
    """Change password route"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('auth/change_password.html')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('auth/change_password.html')
        
        # Update password
        try:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to change password. Please try again.', 'error')
            print(f"Password change error: {e}")
    
    return render_template('auth/change_password.html')

def is_safe_url(target):
    """Check if URL is safe for redirect"""
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
