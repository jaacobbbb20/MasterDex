from ..models import db, Set, environment, SCHEMA
from pokemontcgsdk import Set as TcgSet
from sqlalchemy.sql import text
import time

def seed_sets():
    series = ["Scarlet & Violet"]  # keep expandable later
    retries = 3

    for ser in series:
        for attempt in range(1, retries + 1):
            try:
                print(f"Fetching sets for {ser} (attempt {attempt})")
                sets = TcgSet.where(q=f'series:"{ser}"')

                inserted, updated = 0, 0
                for s in sets:
                    existing = Set.query.get(s.id)
                    if existing:
                        updated += 1
                        existing.name = s.name
                        existing.release_date = getattr(s, "releaseDate", None)
                        existing.image = getattr(s.images, "logo", None)
                        existing.printed_total = getattr(s, "printedTotal", None)
                        existing.total_in_set = getattr(s, "total", None)
                        existing.series = getattr(s, "series", None)
                    else:
                        inserted += 1
                        new_set = Set(
                            id=s.id,
                            name=s.name,
                            release_date=getattr(s, "releaseDate", None),
                            image=getattr(s.images, "logo", None),
                            printed_total=getattr(s, "printedTotal", None),
                            total_in_set=getattr(s, "total", None),
                            series=getattr(s, "series", None),
                        )
                        db.session.add(new_set)

                db.session.commit()
                print(f"Seeded {ser} sets → {inserted} inserted, {updated} updated")
                break
            except Exception as e:
                # consistent error handling
                err_msg = (
                    e.decode("utf-8", errors="ignore") if isinstance(e, (bytes, bytearray))
                    else str(e) if not isinstance(e, Exception) else repr(e)
                )
                print(f"Error fetching sets for {ser}: {err_msg}")
                if attempt < retries:
                    print("Retrying in 5s...")
                    time.sleep(5)
                else:
                    print(f"Failed to fetch sets for {ser} after {retries} attempts")
                    raise

def undo_sets():
    if environment == "production":
        db.session.execute(text(f"DELETE FROM {SCHEMA}.sets"))
    else:
        db.session.execute(text("DELETE FROM sets"))
    db.session.commit()
