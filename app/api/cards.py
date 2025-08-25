from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Card, Binder, BinderCard

cards_bp = Blueprint("cards", __name__)

# GET /api/cards?page=1&per_page=50
@cards_bp.route("/", methods=["GET"])
def get_cards():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    cards = Card.query.order_by(Card.number).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "cards": [c.to_dict() for c in cards.items],
        "page": page,
        "total_pages": cards.pages
    })


# GET /api/cards/:id
@cards_bp.route("/<string:card_id>", methods=["GET"])
def get_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return {"error": "Card not found"}, 404
    return card.to_dict()

# ------------------------------
# PUT /api/cards/<card_id>/toggle
# ------------------------------
@cards_bp.route("/<string:card_id>/toggle", methods=["PUT"])
@login_required
def toggle_card(card_id):
    data = request.get_json() or {}
    binder_id = data.get("binder_id")
    if not binder_id:
      return {"errors": {"message": "Missing binder_id"}}, 400

    binder = Binder.query.get(binder_id)
    if not binder or binder.user_id != current_user.id:
      return {"errors": {"message": "Binder not found or unauthorized"}}, 404

    card = Card.query.get(card_id)
    if not card:
      return {"errors": {"message": "Card not found"}}, 404

    bc = BinderCard.query.filter_by(binder_id=binder.id, card_id=card.id).one_or_none()
    if bc is None:
        bc = BinderCard(binder_id=binder.id, card_id=card.id, owned=True)
        db.session.add(bc)
    else:
        bc.owned = not bc.owned

    db.session.commit()

    payload = card.to_dict()
    if "set" not in payload and getattr(card, "set_id", None):
        payload["set"] = {"id": card.set_id}

    return {"card": payload, "owned": bc.owned}