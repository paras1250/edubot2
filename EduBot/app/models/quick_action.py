from datetime import datetime
from app import db

class QuickAction(db.Model):
    __tablename__ = 'quick_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    keywords = db.Column(db.Text, nullable=True)  # Comma-separated keywords for matching
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=5)  # Higher number = higher priority
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usage_count = db.Column(db.Integer, default=0)  # Track how often this Q&A is used
    
    # Relationships
    creator = db.relationship('User', backref='quick_actions_created', lazy='select')
    
    def __init__(self, question, response, **kwargs):
        self.question = question
        self.response = response
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def increment_usage(self):
        """Increment usage count when this Q&A is used"""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_keywords_list(self):
        """Get keywords as a list"""
        if not self.keywords:
            return []
        return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]
    
    def set_keywords_from_list(self, keywords_list):
        """Set keywords from a list"""
        if keywords_list:
            self.keywords = ', '.join([k.strip() for k in keywords_list if k.strip()])
        else:
            self.keywords = None
    
    def matches_query(self, query):
        """Check if this Q&A matches the user query"""
        query_lower = query.lower().strip()
        
        # Check if query matches question
        if query_lower in self.question.lower():
            return True
        
        # Check if query matches any keywords
        for keyword in self.get_keywords_list():
            if keyword in query_lower or query_lower in keyword:
                return True
        
        return False
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'question': self.question,
            'response': self.response,
            'category': self.category,
            'keywords': self.keywords,
            'keywords_list': self.get_keywords_list(),
            'is_active': self.is_active,
            'priority': self.priority,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'usage_count': self.usage_count
        }
    
    @staticmethod
    def search_for_answer(query, limit=5):
        """Search for matching Q&A pairs for a given query"""
        # Get all active quick actions ordered by priority
        quick_actions = QuickAction.query.filter_by(is_active=True).order_by(
            QuickAction.priority.desc(),
            QuickAction.usage_count.desc()
        ).all()
        
        matches = []
        for qa in quick_actions:
            if qa.matches_query(query):
                matches.append(qa)
                if len(matches) >= limit:
                    break
        
        return matches
    
    @staticmethod
    def get_by_category(category):
        """Get all Q&A pairs in a specific category"""
        return QuickAction.query.filter_by(
            category=category, 
            is_active=True
        ).order_by(QuickAction.priority.desc()).all()
    
    @staticmethod
    def get_popular_questions(limit=10):
        """Get most frequently used questions"""
        return QuickAction.query.filter_by(is_active=True).order_by(
            QuickAction.usage_count.desc()
        ).limit(limit).all()
    
    def __repr__(self):
        return f'<QuickAction {self.id}: {self.question[:50]}...>'
