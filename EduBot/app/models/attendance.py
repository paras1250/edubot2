from datetime import datetime
from app import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('present', 'absent', 'late'), nullable=False, default='absent')
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id])
    marked_by_user = db.relationship('User', foreign_keys=[marked_by], backref='marked_attendance')
    
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', 'date', name='unique_attendance'),)
    
    def __repr__(self):
        return f'<Attendance {self.student_id} - {self.course_id} - {self.date}>'
