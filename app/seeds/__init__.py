from flask.cli import AppGroup
from .users import seed_users, undo_users
from .binders import seed_binders, undo_binders
from .follows import seed_follows, undo_follows
from .comments import seed_comments, undo_comments
from .sets import seed_sets, undo_sets
from .cards import seed_cards, undo_cards
from app.models.db import environment

seed_commands = AppGroup("seed")


@seed_commands.command("all")
def seed():
    if environment == "production":
        # undo in reverse dependency order (comments depend on users/cards/binders)
        undo_comments()
        undo_follows()
        undo_binders()
        undo_cards()
        undo_sets()
        undo_users()

    # seed in dependency order
    seed_users()
    seed_sets()
    seed_cards()
    seed_binders()
    seed_follows()
    seed_comments()


@seed_commands.command("undo")
def undo():
    if environment == "production":
        # production uses TRUNCATE + CASCADE for safety
        undo_comments()
        undo_follows()
        undo_binders()
        undo_cards()
        undo_sets()
        undo_users()
    else:
        # development can just DELETE
        undo_comments()
        undo_follows()
        undo_binders()
        undo_cards()
        undo_sets()
        undo_users()
