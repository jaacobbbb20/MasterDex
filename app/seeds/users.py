from ..models import db, User, environment, SCHEMA
from sqlalchemy.sql import text

def seed_users():
    users_data = [
        dict(first_name="Demo", last_name="User", username="Demo", email="demo@aa.io"),
        dict(first_name="Marnie", last_name="Smith", username="marnie", email="marnie@aa.io"),
        dict(first_name="Bobbie", last_name="Johnson", username="bobbie", email="bobbie@aa.io"),
        dict(first_name="Alice", last_name="Williams", username="alice_tcg", email="alice@example.com"),
        dict(first_name="Charlie", last_name="Brown", username="charlie_collector", email="charlie@example.com"),
        dict(first_name="Diana", last_name="Prince", username="diana_cards", email="diana@example.com"),
        dict(first_name="Ethan", last_name="Hunt", username="ethan_trainer", email="ethan@example.com"),
        dict(first_name="Fiona", last_name="Green", username="fiona_pokemon", email="fiona@example.com"),
        dict(first_name="George", last_name="Miller", username="george_master", email="george@example.com"),
        dict(first_name="Hannah", last_name="Davis", username="hannah_deck", email="hannah@example.com"),
    ]

    inserted, updated = 0, 0

    for u in users_data:
        existing = User.query.filter_by(username=u["username"]).first()
        if existing:
            updated += 1
            existing.first_name = u["first_name"]
            existing.last_name = u["last_name"]
            existing.email = u["email"]
            existing.password = "password"  # reset to known value
        else:
            inserted += 1
            db.session.add(User(**u, password="password"))

    db.session.commit()
    print(f"Users seeded → {inserted} inserted, {updated} updated")


def undo_users():
    if environment == "production":
        db.session.execute(
            text(f"TRUNCATE table {SCHEMA}.users RESTART IDENTITY CASCADE;")
        )
    else:
        db.session.execute(text("DELETE FROM users"))
    db.session.commit()
