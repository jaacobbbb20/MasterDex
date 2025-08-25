from .db import db, environment, SCHEMA, add_prefix_for_prod
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'
    
    if environment == "production":
        __table_args__ = {'schema': SCHEMA}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    binder_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('binders.id')), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    user = db.relationship('User', back_populates='comments')
    binder = db.relationship('Binder', back_populates='comments')

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'binderId': self.binder_id,
            'content': self.content,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'firstName': self.user.first_name,
                'lastName': self.user.last_name
            } if self.user else None,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }
