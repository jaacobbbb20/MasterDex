from ..models import db, Follow, User, environment, SCHEMA
from sqlalchemy.sql import text

def seed_follows():
    # Lookup users by username
    users = {u.username: u for u in User.query.all()}

    # Define relationships as (follower_username, following_username)
    follow_relationships = [
        ("Demo", "marnie"),
        ("Demo", "alice_tcg"),
        ("Demo", "charlie_collector"),
        ("Demo", "diana_cards"),

        ("marnie", "Demo"),
        ("marnie", "bobbie"),
        ("marnie", "fiona_pokemon"),

        ("bobbie", "marnie"),
        ("bobbie", "ethan_trainer"),
        ("bobbie", "george_master"),

        ("alice_tcg", "Demo"),
        ("alice_tcg", "hannah_deck"),
        ("alice_tcg", "diana_cards"),

        ("charlie_collector", "Demo"),
        ("charlie_collector", "fiona_pokemon"),
        ("charlie_collector", "george_master"),

        ("diana_cards", "Demo"),
        ("diana_cards", "alice_tcg"),
        ("diana_cards", "hannah_deck"),

        ("ethan_trainer", "bobbie"),
        ("ethan_trainer", "george_master"),

        ("fiona_pokemon", "marnie"),
        ("fiona_pokemon", "charlie_collector"),
        ("fiona_pokemon", "hannah_deck"),

        ("george_master", "bobbie"),
        ("george_master", "charlie_collector"),
        ("george_master", "ethan_trainer"),

        ("hannah_deck", "alice_tcg"),
        ("hannah_deck", "diana_cards"),
        ("hannah_deck", "fiona_pokemon"),
    ]

    created = 0
    for follower_name, following_name in follow_relationships:
        follower = users.get(follower_name)
        following = users.get(following_name)

        if follower and following:
            # Prevent duplicates → check if the follow already exists
            existing = Follow.query.filter_by(
                follower_id=follower.id, following_id=following.id
            ).first()
            if not existing:
                db.session.add(
                    Follow(follower_id=follower.id, following_id=following.id)
                )
                created += 1

    db.session.commit()
    print(f"Seeded {created} new follow relationships.")

def undo_follows():
    if environment == "production":
        db.session.execute(
            text(f"DELETE FROM {SCHEMA}.follows")
        )
    else:
        db.session.execute(text("DELETE FROM follows"))
    db.session.commit()
