from datetime import datetime
from .db import db, environment, SCHEMA, add_prefix_for_prod

class Binder(db.Model):
    """User's card binders/collections"""
    __tablename__ = 'binders'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Binder information
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)  # Can others view this binder?
    
    # User ownership
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='binders')
    
    def __repr__(self):
        return f'<Binder {self.name} (User: {self.user_id})>'
    
    @property
    def card_count(self):
        """Get total number of cards in this binder"""
        return sum(bc.quantity for bc in self.binder_cards)
    
    @property
    def total_value(self):
        """Calculate total value of cards in this binder"""
        return sum(bc.total_value for bc in self.binder_cards)
    
    @property
    def comments(self):
        """Get all comments for this binder"""
        # Import here to avoid circular imports
        from .comment import Comment
        return Comment.query.filter_by(
            commentable_type='binder',
            commentable_id=self.id,
            parent_comment_id=None  # Only top-level comments
        ).order_by(Comment.created_at.desc()).all()
    
    @property
    def comment_count(self):
        """Get total number of comments (including replies)"""
        # Import here to avoid circular imports
        from .comment import Comment
        return Comment.query.filter_by(
            commentable_type='binder',
            commentable_id=self.id
        ).count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_public': self.is_public,
            'user_id': self.user_id,
            'card_count': self.card_count,
            'total_value': round(self.total_value, 2),
            'comment_count': self.comment_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BinderCard(db.Model):
    """Junction table linking binders to cards with organization info"""
    __tablename__ = 'binder_cards'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    binder_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('binders.id')), nullable=False)
    user_card_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('user_cards.id')), nullable=False)
    
    # Organization within binder
    page_number = db.Column(db.Integer, default=1)  # Which page in the binder
    position = db.Column(db.Integer, default=1)     # Position on the page
    quantity = db.Column(db.Integer, default=1)     # How many of this card in this binder
    
    # Notes specific to this card in this binder
    notes = db.Column(db.Text)
    
    # Timestamps
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    binder = db.relationship('Binder', backref='binder_cards')
    user_card = db.relationship('UserCard', backref='in_binders')
    
    def __repr__(self):
        return f'<BinderCard Binder:{self.binder_id} Card:{self.user_card_id}>'
    
    @property
    def total_value(self):
        """Calculate value of this card entry in the binder"""
        if self.user_card and self.user_card.card and self.user_card.card.market_price:
            return self.quantity * self.user_card.card.market_price
        return 0.0
    
    def to_dict(self):
        return {
            'id': self.id,
            'binder_id': self.binder_id,
            'user_card_id': self.user_card_id,
            'page_number': self.page_number,
            'position': self.position,
            'quantity': self.quantity,
            'notes': self.notes,
            'total_value': round(self.total_value, 2),
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'card': self.user_card.to_dict() if self.user_card else None
        }