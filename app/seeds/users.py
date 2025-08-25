from ..models import db, User, environment, SCHEMA
from sqlalchemy.sql import text

# Adds a demo user, you can add other users here if you want
def seed_users():
    demo = User(
        first_name='Demo',
        last_name='User',
        username='Demo', 
        email='demo@aa.io', 
        password='password'
    )
    marnie = User(
        first_name='Marnie',
        last_name='Smith',
        username='marnie', 
        email='marnie@aa.io', 
        password='password'
    )
    bobbie = User(
        first_name='Bobbie',
        last_name='Johnson',
        username='bobbie', 
        email='bobbie@aa.io', 
        password='password'
    )
    alice = User(
        first_name='Alice',
        last_name='Williams',
        username='alice_tcg',
        email='alice@example.com',
        password='password'
    )
    charlie = User(
        first_name='Charlie',
        last_name='Brown',
        username='charlie_collector',
        email='charlie@example.com',
        password='password'
    )
    diana = User(
        first_name='Diana',
        last_name='Prince',
        username='diana_cards',
        email='diana@example.com',
        password='password'
    )
    ethan = User(
        first_name='Ethan',
        last_name='Hunt',
        username='ethan_trainer',
        email='ethan@example.com',
        password='password'
    )
    fiona = User(
        first_name='Fiona',
        last_name='Green',
        username='fiona_pokemon',
        email='fiona@example.com',
        password='password'
    )
    george = User(
        first_name='George',
        last_name='Miller',
        username='george_master',
        email='george@example.com',
        password='password'
    )
    hannah = User(
        first_name='Hannah',
        last_name='Davis',
        username='hannah_deck',
        email='hannah@example.com',
        password='password'
    )
    
    users = [demo, marnie, bobbie, alice, charlie, diana, ethan, fiona, george, hannah]
    for user in users:
        db.session.add(user)
    
    db.session.commit()


# Uses a raw SQL query to TRUNCATE or DELETE the users table. SQLAlchemy doesn't
# have a built in function to do this. With postgres in production TRUNCATE
# removes all the data from the table, and RESET IDENTITY resets the auto
# incrementing primary key, CASCADE deletes any dependent entities.  With
# sqlite3 in development you need to instead use DELETE to remove all data and
# it will reset the primary keys for you as well.
def undo_users():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.users RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM users"))
    db.session.commit()