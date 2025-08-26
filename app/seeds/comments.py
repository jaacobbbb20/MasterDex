from ..models import db, Comment, User, Binder, environment, SCHEMA
from sqlalchemy.sql import text

def seed_comments():
    demo = User.query.filter_by(username="Demo").first()
    marnie = User.query.filter_by(username="marnie").first()
    bobbie = User.query.filter_by(username="bobbie").first()

    demo_binder = Binder.query.filter_by(name="Demo's Favorite Cards").first()
    marnie_binder = Binder.query.filter_by(name="Marnie's Tournament Deck").first()
    bobbie_binder = Binder.query.filter_by(name="Bobbie's Childhood Collection").first()

    comments_data = [
        (demo, marnie_binder, "Great binder! I love your card selection, Marnie."),
        (demo, bobbie_binder, "Nostalgic collection! Takes me back to my childhood too."),
        (marnie, demo_binder, "Your collection is amazing, Demo! So many rare cards."),
        (bobbie, demo_binder, "Wow Demo, your collection has grown so much!"),
    ]

    created = 0
    for user, binder, content in comments_data:
        if user and binder:
            # Prevent duplicates → only insert if it doesn't already exist
            existing = Comment.query.filter_by(
                user_id=user.id,
                binder_id=binder.id,
                content=content
            ).first()
            if not existing:
                db.session.add(Comment(
                    content=content,
                    user_id=user.id,
                    binder_id=binder.id
                ))
                created += 1

    db.session.commit()
    print(f"Seeded {created} new comments.")

def undo_comments():
    if environment == "production":
        db.session.execute(
            text(f"DELETE FROM {SCHEMA}.comments")
        )
    else:
        db.session.execute(text("DELETE FROM comments"))
    db.session.commit()
