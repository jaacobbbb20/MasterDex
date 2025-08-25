from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import cast, Integer
from .db import db, environment, SCHEMA, add_prefix_for_prod

class Card(db.Model):
    __tablename__ = "cards"

    if environment == "production":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String)
    rarity = db.Column(db.String)
    number = db.Column(db.String)
    set_id = db.Column(db.String, db.ForeignKey(add_prefix_for_prod("sets.id")), nullable=True)

    set = db.relationship("Set", back_populates="cards")

    # Association object
    binder_cards = db.relationship("BinderCard", back_populates="card", cascade="all, delete-orphan")

    # Access binders via BinderCard (no secondary=)
    binders = db.relationship("Binder", back_populates="cards", viewonly=True)

    # ----------------------------
    # Hybrid property for sorting
    # ----------------------------
    @hybrid_property
    def number_int(self):
        """Extract numeric part of number (e.g., '23a' -> 23, 'TG13' -> 13)."""
        try:
            return int("".join(filter(str.isdigit, self.number or "")))
        except ValueError:
            return None

    @number_int.expression
    def number_int(cls):
        return cast(cls.number, Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "rarity": self.rarity,
            "number": self.number,
            "setId": self.set_id
        }
