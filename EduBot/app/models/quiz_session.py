from datetime import datetime
from app import db

class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # Chat session ID
    is_active = db.Column(db.Boolean, default=True)
    user_answer = db.Column(db.String(1), nullable=True)  # A, B, C, or D
    is_correct = db.Column(db.Boolean, nullable=True)
    points_earned = db.Column(db.Integer, default=0)
    answered_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='quiz_sessions')
    quiz = db.relationship('Quiz', backref='quiz_sessions')
    
    def __repr__(self):
        return f'<QuizSession {self.user_id} - Quiz {self.quiz_id}>'
