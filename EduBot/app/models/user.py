from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('student', 'faculty', 'admin'), nullable=False, default='student')
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    course_id = db.Column(db.Integer, nullable=True)
    year_of_study = db.Column(db.Integer, nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    faculty_profile = db.relationship('Faculty', backref='user', uselist=False, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', foreign_keys='Attendance.student_id', lazy='dynamic', cascade='all, delete-orphan')
    chat_logs = db.relationship('ChatLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    created_groups = db.relationship('Group', foreign_keys='Group.created_by', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    group_memberships = db.relationship('GroupMember', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    group_messages = db.relationship('GroupMessage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, first_name, last_name, role='student', **kwargs):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_faculty(self):
        """Check if user is faculty"""
        return self.role == 'faculty'
    
    def is_student(self):
        """Check if user is student"""
        return self.role == 'student'
    
    def get_attendance_percentage(self, course_id=None):
        """Calculate attendance percentage for a specific course or overall"""
        from app.models.attendance import Attendance
        
        query = self.attendance_records
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        total_classes = query.count()
        if total_classes == 0:
            return 0
        
        present_classes = query.filter_by(status='present').count()
        return round((present_classes / total_classes) * 100, 2)
    
    def get_recent_chat_logs(self, limit=10):
        """Get recent chat logs for the user"""
        return self.chat_logs.order_by(db.desc('created_at')).limit(limit).all()
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'year_of_study': self.year_of_study,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
