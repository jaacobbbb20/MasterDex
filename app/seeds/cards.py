from ..models import db, Card
from pokemontcgsdk import Card as TCGCard
from sqlalchemy.sql import text
from time import sleep

def seed_cards():
    page = 1
    page_size = 50
    total_seeded = 0
    retries = 3

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
                break  # success → exit retry loop
            except Exception as e:
                if isinstance(e, (bytes, bytearray)):
                    err_msg = e.decode("utf-8", errors="ignore")
                elif hasattr(e, "args") and e.args and isinstance(e.args[0], (bytes, bytearray)):
                    err_msg = e.args[0].decode("utf-8", errors="ignore")
                else:
                    try:
                        err_msg = str(e)
                    except Exception:
                        err_msg = repr(e)

                print(f"Error fetching page {page} (attempt {attempt}/{retries}): {err_msg}")
                if attempt < retries:
                    print("Retrying in 5s...")
                    sleep(5)
                    attempt += 1
                else:
                    print(f"Failed to fetch page {page} after {retries} attempts. Stopping.")
                    return
        else:
            # retries exceeded
            break

        if not cards:
            break

        for c in cards:
            card = Card(
                id=c.id,
                name=c.name,
                image=getattr(c.images, "large", None),
                rarity=c.rarity,
                number=c.number,
                set_id=c.set.id if c.set else None,
            )
            db.session.merge(card)  # merge = insert or update

        db.session.commit()
        total_seeded += len(cards)
        print(f"Seeded {len(cards)} cards (total: {total_seeded})")

        # small delay before next page
        sleep(0.5)
        page += 1

    print(f"Done seeding {total_seeded} Scarlet & Violet cards!")


def undo_cards():
    db.session.execute(text("DELETE FROM cards"))
    db.session.commit()
