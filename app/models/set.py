from .db import db, environment, SCHEMA, add_prefix_for_prod

class Set(db.Model):
    __tablename__ = "sets"

    if environment == "production":
        __table_args__ = {"schema": SCHEMA}

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    series = db.Column(db.String)
    release_date = db.Column(db.String)
    image = db.Column(db.String)

    printed_total = db.Column(db.Integer)
    total_in_set = db.Column(db.Integer)

    cards = db.relationship("Card", back_populates="set", cascade="all, delete-orphan")
    binders = db.relationship("Binder", back_populates="set", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "release_date": self.release_date,
            "image": self.image,
            "printed_total": self.printed_total,
            "total_in_set": self.total_in_set,
        }
