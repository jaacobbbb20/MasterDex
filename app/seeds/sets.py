# app/seeds/sets.py
from ..models import db, Set, environment, SCHEMA
from pokemontcgsdk import Set as TcgSet
from sqlalchemy.sql import text
import time

def seed_sets():
    series = ["Scarlet & Violet"]  # keep expandable later
    retries = 3

    for ser in series:
        for attempt in range(1, retries+1):
            try:
                print(f"Fetching sets for {ser} (attempt {attempt})")
                sets = TcgSet.where(q=f'series:"{ser}"')

                for s in sets:
                    new_set = Set(
                        id=s.id,
                        name=s.name,
                        release_date=getattr(s, "releaseDate", None),
                        image=getattr(s.images, "logo", None),
                        printed_total=getattr(s, "printedTotal", None),
                        total_in_set=getattr(s, "total", None),
                        series=getattr(s, "series", None),
                    )
                    db.session.merge(new_set)

                db.session.commit()
                print(f"✅ Seeded {len(sets)} sets for {ser}")
                break
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

                print(f"Error fetching sets for {ser}: {err_msg}")
                if attempt < retries:
                    print("Retrying in 5s...")
                    time.sleep(5)
                else:
                    print(f"Failed to fetch sets for {ser} after retries")
                    raise


def undo_sets():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.sets RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM sets"))
    db.session.commit()
