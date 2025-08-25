from flask import Blueprint, jsonify, request
from app.models import db, Set, Card, Binder
from flask_login import login_required, current_user

sets_bp = Blueprint("sets", __name__)

# GET /api/sets
@sets_bp.route("/", methods=["GET"])
def get_sets():
    sets = Set.query.order_by(Set.release_date.desc()).all()
    return jsonify([s.to_dict() for s in sets])

# GET /api/sets/:id
@sets_bp.route("/<string:set_id>", methods=["GET"])
def get_set(set_id):
    s = Set.query.get(set_id)
    if not s:
        return {"error": "Set not found"}, 404
    return {
        **s.to_dict(),
        "cards": [c.to_dict() for c in s.cards]
    }

# ------------------------------
# GET /api/sets/<set_id>/cards
# Return cards in this set, ordered by card.number
# ------------------------------
@sets_bp.route("/<string:set_id>/cards")
@login_required
def get_cards_for_set(set_id):
    start = max(int(request.args.get("start", 1)), 1)
    end = int(request.args.get("end", 9))
    binder_id = request.args.get("binder_id")

    binder_cards = set()
    if binder_id:
        binder = Binder.query.get(binder_id)
        if binder and binder.user_id == current_user.id:
            binder_cards = {c.id for c in binder.cards}

    cards = (
        Card.query.filter(Card.set_id == set_id)
        .order_by(Card.number_int)
        .all()
    )

    # slice for pagination
    cards = cards[start - 1:end]

    return {
        "cards": [
            {**c.to_dict(), "owned": c.id in binder_cards}
            for c in cards
        ]
    }
