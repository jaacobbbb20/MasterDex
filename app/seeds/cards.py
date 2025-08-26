from ..models import db, Card, Set, environment, SCHEMA
from pokemontcgsdk import Card as TCGCard
from sqlalchemy.sql import text
from time import sleep

def seed_cards():
    page = 1
    page_size = 50
    total_seeded = 0
    retries = 3

    # Fetch valid set IDs from DB first
    valid_set_ids = {s.id for s in db.session.query(Set.id).all()}
    print(f"Valid sets in DB: {valid_set_ids}")

    while True:
        print(f"Fetching page {page}...")
        attempt = 1
        while attempt <= retries:
            try:
                cards = TCGCard.where(
                    q='set.series:"Scarlet & Violet"',
                    page=page,
                    pageSize=page_size
                )
                break
            except Exception as e:
                print(f"Error fetching page {page} (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    print("Retrying in 5s...")
                    sleep(5)
                    attempt += 1
                else:
                    print(f"Failed to fetch page {page} after {retries} attempts. Stopping.")
                    return

        if not cards:
            break

        added = 0
        for c in cards:
            set_id = c.set.id if c.set else None
            if set_id not in valid_set_ids:
                print(f"Skipping card {c.id} (set {set_id} not found in DB)")
                continue  # skip instead of crashing

            card = Card(
                id=c.id,
                name=c.name,
                image=getattr(c.images, "large", None),
                rarity=c.rarity,
                number=c.number,
                set_id=set_id,
            )
            db.session.merge(card)
            added += 1

        db.session.commit()
        total_seeded += added
        print(f"✅ Seeded {added} cards (total: {total_seeded})")

        # Delay before next page
        sleep(0.5)
        page += 1

    print(f"Done seeding {total_seeded} Scarlet & Violet cards!")


def undo_cards():
    if environment == "production":
        db.session.execute(
            text(f"TRUNCATE table {SCHEMA}.cards RESTART IDENTITY CASCADE;")
        )
    else:
        db.session.execute(text("DELETE FROM cards"))
    db.session.commit()
