from ..models import db, Binder, User, Card, environment, SCHEMA
from sqlalchemy.sql import text

def seed_binders():
    demo = User.query.filter_by(username='Demo').first()
    marnie = User.query.filter_by(username='marnie').first()
    bobbie = User.query.filter_by(username='bobbie').first()

    cards = Card.query.all()

    default_set = {
        "set_id": "base1",
        "set_name": "Base Set",
        "set_symbol": None,
        "set_logo": None,
        "printed_total": 102,
        "total_in_set": 102
    }

    binders = []

    if demo:
        demo_binder = Binder(
            name="Demo's Favorite Cards",
            description="My most treasured Pokémon cards",
            user_id=demo.id,
            **default_set
        )
        if cards:
            demo_binder.cards.extend(cards[:3])
        binders.append(demo_binder)

    if marnie:
        marnie_binder = Binder(
            name="Marnie's Tournament Deck",
            description="Cards I use for competitive play",
            user_id=marnie.id,
            **default_set
        )
        if len(cards) > 3:
            marnie_binder.cards.extend(cards[3:6])
        binders.append(marnie_binder)

    if bobbie:
        bobbie_binder = Binder(
            name="Bobbie's Childhood Collection",
            description="Cards from when I first started collecting",
            user_id=bobbie.id,
            **default_set
        )
        if len(cards) > 6:
            bobbie_binder.cards.extend(cards[6:9])
        binders.append(bobbie_binder)

    db.session.add_all(binders)
    db.session.commit()
    print(f"Seeded {len(binders)} binders with card associations.")

def undo_binders():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.binder_cards RESTART IDENTITY CASCADE;")
        db.session.execute(f"TRUNCATE table {SCHEMA}.binders RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM binder_cards"))
        db.session.execute(text("DELETE FROM binders"))
    db.session.commit()