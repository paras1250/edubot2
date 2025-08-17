from datetime import datetime
from app import db

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=True)
    option_d = db.Column(db.String(255), nullable=True)
    correct_answer = db.Column(db.Enum('A', 'B', 'C', 'D'), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.Enum('easy', 'medium', 'hard'), nullable=False, default='medium')
    category = db.Column(db.Enum('general', 'computer_science', 'mathematics', 'science', 'history', 'literature'), nullable=False, default='general')
    points = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d
            },
            'subject': self.subject,
            'difficulty': self.difficulty,
            'category': self.category,
            'points': self.points
        }
    
    def check_answer(self, user_answer):
        return user_answer.upper() == self.correct_answer
