from .db import db, environment, SCHEMA, add_prefix_for_prod
from datetime import datetime
from sqlalchemy import UniqueConstraint

class Follow(db.Model):
    __tablename__ = "follows"

    if environment == "production":
        __table_args__ = {"schema": SCHEMA}
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_follow'),
    )

    follower_id = db.Column(
        db.Integer, db.ForeignKey(add_prefix_for_prod("users.id")), primary_key=True
    )
    following_id = db.Column(
        db.Integer, db.ForeignKey(add_prefix_for_prod("users.id")), primary_key=True
    )
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    follower = db.relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = db.relationship("User", foreign_keys=[following_id], back_populates="followers")

    def to_dict(self):
        return {
            "follower_id": self.follower_id,
            "following_id": self.following_id,
            "follower_username": self.follower.username if self.follower else None,
            "following_username": self.following.username if self.following else None,
            "created_at": self.created_at.isoformat(),
        }
        