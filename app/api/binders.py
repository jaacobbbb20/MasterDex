from flask import Blueprint, request
from flask_login import login_required, current_user
from ..models import Binder, Card, BinderCard, db
from sqlalchemy import func, case

binders_bp = Blueprint("binders", __name__)

#-------------------------------------------------------------
#  BINDER ROUTES BEGIN HERE
#-------------------------------------------------------------

# ------------------------------
# GET /api/binders
# Get of the current user's binders
# ------------------------------
@binders_bp.route("", methods=["GET"])
@login_required
def get_binders():
    # Sum of owned=True per binder
    owned_subq = (
        db.session.query(
            BinderCard.binder_id.label("binder_id"),
            func.coalesce(
                func.sum(case((BinderCard.owned == True, 1), else_=0)),
                0
            ).label("ownedCount")
        )
        .group_by(BinderCard.binder_id)
        .subquery()
    )

    rows = (
        db.session.query(
            Binder,
            func.coalesce(owned_subq.c.ownedCount, 0).label("ownedCount")
        )
        .outerjoin(owned_subq, owned_subq.c.binder_id == Binder.id)
        .filter(Binder.user_id == current_user.id)
        .all()
    )

    def serialize(binder, owned_count):
        # start from your existing serializer
        d = binder.to_dict() if hasattr(binder, "to_dict") else {"id": binder.id, "name": binder.name}

        # normalize lightweight list payload
        d.pop("cards", None)
        d.pop("binder_cards", None)

        # Add counts the frontend expects
        d["ownedCount"] = int(owned_count or 0)
        d["totalSetCards"] = int(
            getattr(binder, "total_in_set", 0)
            or getattr(binder, "totalSetCards", 0)
            or 0
        )
        return d

    return {"binders": [serialize(b, oc) for (b, oc) in rows]}


# ------------------------------
# GET /api/binders/<binder_id>
# Get a single binder
# ------------------------------
@binders_bp.route("/<int:binder_id>", methods=["GET"])
@login_required
def get_binder(binder_id):
    binder = Binder.query.get(binder_id)
    if not binder:
        return {"errors": {"message": "Not found"}}, 404

    payload = binder.to_dict(include_cards=True)  # includes cards for display
    payload["isOwner"] = (binder.user_id == current_user.id)  # tells the frontend
    return {"binder": payload}, 200

# ------------------------------
# GET /api/binders/<binder_id>/progress
# Returns cards collected out of the selected set in a percent
# ------------------------------
@binders_bp.route("/<int:binder_id>/progress", methods=["GET"])
@login_required
def binder_progress(binder_id):
    binder = Binder.query.get(binder_id)
    if not binder or binder.user_id != current_user.id:
        return {"errors": {"message": "Not found"}}, 404

    collected = db.session.query(func.count(BinderCard.card_id)).filter_by(
        binder_id=binder.id, owned=True  # only owned binder's card
    ).scalar()

    total = int(getattr(binder, "total_in_set", 0) or 0)
    progress = (collected / total * 100) if total > 0 else 0

    return {
        "binder_id": binder.id,
        "collected": int(collected),
        "total": total,
        "progress": round(progress, 2),
    }

# ------------------------------
# POST /api/binders
# Create a new binder
# ------------------------------
@binders_bp.route("", methods=["POST"])
@login_required
def create_binder():
    data = request.get_json()
    name = data.get("name")
    set_id = data.get("set_id")

    if not name or not set_id:
        return {"errors": {"message": "name, set_id, and set_name are required"}}, 400

    binder = Binder(
        name=name,
        description=data.get("description", ""),
        user_id=current_user.id,
        set_id=set_id,
    )

    db.session.add(binder)
    db.session.commit()

    return {"binder": binder.to_dict(include_cards=True)}, 201


# ------------------------------
# PUT /api/binders/<binder_id>
# Update a binder
# ------------------------------
@binders_bp.route("/<int:binder_id>", methods=["PUT"])
@login_required
def update_binder(binder_id):
    binder = Binder.query.get_or_404(binder_id)

    if binder.user_id != current_user.id:
        return {"errors": {"message": "You are not allowed to edit this binder"}}, 403

    data = request.get_json()
    binder.name = data.get("name", binder.name)
    binder.description = data.get("description", binder.description)

    db.session.commit()
    return binder.to_dict()

# ------------------------------
# DELETE /api/binders/<binder_id>
# Delete a binder
# ------------------------------
@binders_bp.route("/<int:binder_id>", methods=["DELETE"])
@login_required
def delete_binder(binder_id):
    binder = Binder.query.get_or_404(binder_id)

    if binder.user_id != current_user.id:
        return {"errors": {"message": "You are not allowed to delete this binder"}}, 403

    db.session.delete(binder)
    db.session.commit()
    return {"message": "Binder deleted successfully"}

#-------------------------------------------------------------
#  BINDER ROUTES END HERE
#-------------------------------------------------------------

#-------------------------------------------------------------
#  CARDS ROUTES BEGIN HERE
#-------------------------------------------------------------


# ------------------------------
# GET /api/binders/<binder_id>/cards
# ------------------------------
@binders_bp.route("/<int:binder_id>/cards", methods=["GET"])
@login_required
def get_cards_in_binder(binder_id):
    binder = Binder.query.get(binder_id)
    if not binder or binder.user_id != current_user.id:
        return {"errors": {"message": "Not found"}}, 404

    page = max(int(request.args.get("page", 1)), 1)
    per_page = 9

    query = (
        Card.query.join(BinderCard, BinderCard.card_id == Card.id)
        .filter(BinderCard.binder_id == binder.id)
        .order_by(Card.number)
    )

    total_cards = query.count()
    total_pages = (total_cards + per_page - 1) // per_page

    results = (
        db.session.query(Card, BinderCard.owned)
        .join(BinderCard, BinderCard.card_id == Card.id)
        .filter(BinderCard.binder_id == binder.id)
        .order_by(Card.number)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    cards = []
    for card, owned in results:
        card_dict = card.to_dict()
        card_dict["owned"] = owned
        cards.append(card_dict)

    return {
        "binder_id": binder.id,
        "page": page,
        "per_page": per_page,
        "total_cards": total_cards,
        "total_pages": total_pages,
        "cards": cards,
    }, 200

# ------------------------------
# PUT /api/binders/<binder_id>/cards/<card_id>/toggle
# ------------------------------
@binders_bp.route("/<int:binder_id>/cards/<string:card_id>/toggle", methods=["PUT"])
@login_required
def toggle_card_ownership(binder_id, card_id):
    binder = Binder.query.get_or_404(binder_id)
    if binder.user_id != current_user.id:
        return {"errors": {"message": "Unauthorized"}}, 403

    assoc = BinderCard.query.filter_by(binder_id=binder.id, card_id=card_id).first()
    if not assoc:
        return {"errors": {"message": "Card not found in this binder"}}, 404

    assoc.owned = not assoc.owned
    db.session.commit()

    return {"card_id": card_id, "owned": assoc.owned}