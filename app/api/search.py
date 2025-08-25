from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import or_, func, select
from ..models import db, Binder, Card, User

search_bp = Blueprint("search", __name__, url_prefix="/api/search")

def like(q): return f"%{q.strip()}%"

@search_bp.route("", methods=["GET"])
@login_required
def search_all():
    q = (request.args.get("q") or "").strip()
    if not q:
        return {"binders": [], "cards": [], "users": []}, 200

    binders = (
        db.session.query(Binder)
        .filter(Binder.user_id == current_user.id)
        .filter(or_(Binder.name.ilike(like(q)), func.cast(Binder.id, db.String).ilike(like(q))))
        .limit(10).all()
    )
    binders_out = [{"id": b.id, "name": b.name, "setName": getattr(b, "set_name", None), "setImage": getattr(b, "set_image", None), "set_id": b.set_id} for b in binders]

    cards = (
        db.session.query(Card)
        .filter(or_(Card.name.ilike(like(q)), Card.number.ilike(like(q))))
        .limit(10).all()
    )
    cards_out = [{"id": c.id, "name": c.name, "number": c.number, "set_id": c.set_id} for c in cards]

    users = (
        db.session.query(User)
        .filter(User.id != current_user.id)
        .filter(or_(User.username.ilike(like(q)), User.first_name.ilike(like(q)), User.last_name.ilike(like(q))))
        .limit(10).all()
    )
    users_out = [{"id": u.id, "username": u.username, "firstName": u.first_name, "lastName": u.last_name, "profileImage": getattr(u, "profile_image", None)} for u in users]

    return {"binders": binders_out, "cards": cards_out, "users": users_out}, 200
