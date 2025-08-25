from .db import db, environment, SCHEMA, add_prefix_for_prod
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func
from .follow import Follow


class User(db.Model, UserMixin):
    __tablename__ = "users"

    if environment == "production":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashed_password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    comments = db.relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    binders = db.relationship("Binder", backref="user", cascade="all, delete-orphan")

    # Follow relationships (through association table)
    following = db.relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan"
    )
    followers = db.relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan"
    )

    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict_basic(self):
        return {
            "id": self.id,
            "username": self.username,
            "firstName": self.first_name,
            "lastName": self.last_name,
        }

    def to_dict(self, include_follow_data=False, viewer_id=None):
        data = {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username": self.username,
            "email": self.email,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_follow_data:
            data["followersCount"] = Follow.query.filter_by(following_id=self.id).count()
            data["followingCount"] = Follow.query.filter_by(follower_id=self.id).count()

        if viewer_id is not None:
            data["isFollowing"] = (
                Follow.query.filter_by(
                    follower_id=viewer_id, following_id=self.id
                ).first() is not None
            )

        return data