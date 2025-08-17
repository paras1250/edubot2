from datetime import datetime
from app import db

class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.Text, nullable=True)
    office_location = db.Column(db.String(100), nullable=True)
    office_hours = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    courses = db.relationship('Course', backref='faculty', lazy='dynamic')
    
    def __init__(self, employee_id, department, designation, **kwargs):
        self.employee_id = employee_id
        self.department = department
        self.designation = designation
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def name(self):
        """Return faculty name from user relationship"""
        if self.user:
            return self.user.full_name
        return "Unknown Faculty"
    
    @property
    def email(self):
        """Return faculty email from user relationship"""
        if self.user:
            return self.user.email
        return None
    
    @property
    def phone(self):
        """Return faculty phone from user relationship"""
        if self.user:
            return self.user.phone
        return None
    
    def get_courses_count(self):
        """Get total number of courses taught by this faculty"""
        return self.courses.filter_by(is_active=True).count()
    
    def get_active_courses(self):
        """Get all active courses taught by this faculty"""
        return self.courses.filter_by(is_active=True).all()
    
    def to_dict(self):
        """Convert faculty object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_id': self.employee_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'designation': self.designation,
            'specialization': self.specialization,
            'office_location': self.office_location,
            'office_hours': self.office_hours,
            'bio': self.bio,
            'image_url': self.image_url,
            'is_active': self.is_active,
            'courses_count': self.get_courses_count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Faculty {self.employee_id} - {self.name}>'
