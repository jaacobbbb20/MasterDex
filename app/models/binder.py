from .db import db, environment, SCHEMA, add_prefix_for_prod
from .binder_card import BinderCard

class Binder(db.Model):
    __tablename__ = "binders"

    if environment == "production":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey(add_prefix_for_prod("users.id")), nullable=False
    )

    # Association object
    binder_cards = db.relationship("BinderCard", back_populates="binder", cascade="all, delete-orphan")

    # Access cards via BinderCard (no secondary=)
    cards = db.relationship(
        "Card", 
        secondary=BinderCard.__table__,
        back_populates="binders", 
        viewonly=True)

    comments = db.relationship("Comment", back_populates="binder", cascade="all, delete-orphan")

    set_id = db.Column(
        db.String,
        db.ForeignKey(add_prefix_for_prod("sets.id"), name="fk_binders_set_id"),
        nullable=False,
    )
    set = db.relationship("Set", back_populates="binders")

    def to_dict(self, include_cards=False, include_comments=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "user_id": self.user_id,
            "setId": self.set_id,
            "setName": self.set.name if self.set else None,
            "setSymbol": self.set.image if self.set else None,
            "setLogo": self.set.image if self.set else None,
            "printedTotal": getattr(self.set, "printed_total", None),
            "totalSetCards": getattr(self.set, "total_in_set", None),
        }
        if include_cards:
            data["cards"] = [c.to_dict() for c in self.cards]
        return data
