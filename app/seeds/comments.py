from ..models import db, Comment, User, Binder, environment, SCHEMA
from sqlalchemy.sql import text

def seed_comments():
    demo = User.query.filter_by(username="Demo").first()
    marnie = User.query.filter_by(username="marnie").first()
    bobbie = User.query.filter_by(username="bobbie").first()

    demo_binder = Binder.query.filter_by(name="Demo's Favorite Cards").first()
    marnie_binder = Binder.query.filter_by(name="Marnie's Tournament Deck").first()
    bobbie_binder = Binder.query.filter_by(name="Bobbie's Childhood Collection").first()

    comments = []

    if demo and marnie_binder:
        comments.append(Comment(
            content="Great binder! I love your card selection, Marnie.",
            user_id=demo.id,
            binder_id=marnie_binder.id
        ))
    if demo and bobbie_binder:
        comments.append(Comment(
            content="Nostalgic collection! Takes me back to my childhood too.",
            user_id=demo.id,
            binder_id=bobbie_binder.id
        ))

    if marnie and demo_binder:
        comments.append(Comment(
            content="Your collection is amazing, Demo! So many rare cards.",
            user_id=marnie.id,
            binder_id=demo_binder.id
        ))

    if bobbie and demo_binder:
        comments.append(Comment(
            content="Wow Demo, your collection has grown so much!",
            user_id=bobbie.id,
            binder_id=demo_binder.id
        ))

    db.session.add_all(comments)
    db.session.commit()
    print(f"Seeded {len(comments)} comments.")

def undo_comments():
    if environment == "production":
        db.session.execute(text("TRUNCATE table comments RESTART IDENTITY CASCADE;"))
    else:
        db.session.execute(text("DELETE FROM comments"))
    db.session.commit()