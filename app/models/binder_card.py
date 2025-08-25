from .db import db, environment, SCHEMA, add_prefix_for_prod

class BinderCard(db.Model):
    __tablename__ = "binder_cards"

    if environment == "production":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    binder_id = db.Column(
        db.Integer, db.ForeignKey(add_prefix_for_prod("binders.id")), nullable=False
    )
    card_id = db.Column(
        db.String, db.ForeignKey(add_prefix_for_prod("cards.id")), nullable=False
    )
    owned = db.Column(db.Boolean, default=False, nullable=False)

    binder = db.relationship("Binder", back_populates="binder_cards")
    card = db.relationship("Card", back_populates="binder_cards")