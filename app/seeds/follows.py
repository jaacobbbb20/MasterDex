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

    follows_to_add = []
    for follower_name, following_name in follow_relationships:
        follower = users.get(follower_name)
        following = users.get(following_name)

        # Ensure both users exist
        if follower and following:
            follows_to_add.append(
                Follow(follower_id=follower.id, following_id=following.id)
            )

    db.session.add_all(follows_to_add)
    db.session.commit()
    print(f"Seeded {len(follows_to_add)} follow relationships.")

def undo_follows():
    if environment == "production":
        db.session.execute(text("TRUNCATE table follows RESTART IDENTITY CASCADE;"))
    else:
        db.session.execute(text("DELETE FROM follows"))
    db.session.commit()
