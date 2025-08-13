from datetime import datetime
from .db import db, environment, SCHEMA, add_prefix_for_prod

class Comment(db.Model):
    """Comments on binders and cards"""
    __tablename__ = 'comments'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    commentable_type = db.Column(db.String(50), nullable=False)
    commentable_id = db.Column(db.Integer, nullable=False)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('comments.id')), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='comments')
    parent_comment = db.relationship('Comment', remote_side=[id], backref='replies')
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.user.username} on {self.commentable_type}:{self.commentable_id}>'
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent_comment_id is not None
    
    @property
    def reply_count(self):
        """Get number of replies to this comment"""
        return len(self.replies)
    
    def can_edit(self, user):
        """Check if user can edit this comment"""
        return self.user_id == user.id
    
    def can_delete(self, user):
        """Check if user can delete this comment"""
        return self.user_id == user.id
    
    def to_dict(self, include_replies=False):
        result = {
            'id': self.id,
            'content': self.content,
            'user_id': self.user_id,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'full_name': self.user.full_name
            } if self.user else None,
            'commentable_type': self.commentable_type,
            'commentable_id': self.commentable_id,
            'parent_comment_id': self.parent_comment_id,
            'is_reply': self.is_reply,
            'reply_count': self.reply_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_replies and self.replies:
            result['replies'] = [reply.to_dict() for reply in self.replies]
        
        return result