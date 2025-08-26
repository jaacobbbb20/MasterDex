from ..models import db, Binder, BinderCard, User, Card, environment, SCHEMA
from sqlalchemy.sql import text

def seed_binders():
    demo = User.query.filter_by(username="Demo").first()
    marnie = User.query.filter_by(username="marnie").first()
    bobbie = User.query.filter_by(username="bobbie").first()

    cards = Card.query.all()

    default_set = {
        "set_id": "base1",
        "set_name": "Base Set",
        "set_symbol": None,
        "set_logo": None,
        "printed_total": 102,
        "total_in_set": 102,
    }

    binders = []

    def create_binder_if_missing(owner, name, description, card_slice):
        if not owner:
            return None
        existing = Binder.query.filter_by(name=name, user_id=owner.id).first()
        if existing:
            return existing
        binder = Binder(
            name=name,
            description=description,
            user_id=owner.id,
            **default_set,
        )
        db.session.add(binder)
        db.session.flush()

        for c in card_slice:
            db.session.add(BinderCard(binder_id=binder.id, card_id=c.id, owned=True))

        return binder

    if cards:
        demo_binder = create_binder_if_missing(
            demo, "Demo's Favorite Cards", "My most treasured Pokémon cards", cards[:3]
        )
        marnie_binder = create_binder_if_missing(
            marnie, "Marnie's Tournament Deck", "Cards I use for competitive play", cards[3:6]
        )
        bobbie_binder = create_binder_if_missing(
            bobbie, "Bobbie's Childhood Collection", "Cards from when I first started collecting", cards[6:9]
        )

        for b in [demo_binder, marnie_binder, bobbie_binder]:
            if b:
                binders.append(b)

    db.session.commit()
    print(f"Seeded or confirmed {len(binders)} binders.")



def undo_binders():
    if environment == "production":
        db.session.execute(text(f"DELETE FROM {SCHEMA}.binder_cards"))
        db.session.execute(text(f"DELETE FROM {SCHEMA}.binders"))
    else:
        db.session.execute(text("DELETE FROM binder_cards"))
        db.session.execute(text("DELETE FROM binders"))
    db.session.commit()
