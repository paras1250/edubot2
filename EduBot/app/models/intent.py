from datetime import datetime
from app import db

class Intent(db.Model):
    __tablename__ = 'intents'
    id = db.Column(db.Integer, primary_key=True)
    intent_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    patterns = db.Column(db.Text, nullable=False)  # JSON array of regex patterns
    responses = db.Column(db.Text, nullable=False)  # JSON array of possible responses
    handler_function = db.Column(db.String(100), nullable=True)  # Python function to handle this intent
    priority = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
