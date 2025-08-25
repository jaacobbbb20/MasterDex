from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import User, db

user_routes = Blueprint('users', __name__)

@user_routes.route("/")
@login_required
def users():
    users = User.query.all()
    return {"users": [user.to_dict() for user in users]}

@user_routes.route("/<int:id>")
@login_required
def user(id):
    u = User.query.get(id)
    if u:
        return {"user": u.to_dict(include_follow_data=True, viewer_id=current_user.id)}
    return {"errors": {"message": "User not found"}}, 404

@user_routes.route("/by-username/<string:username>")
@login_required
def user_by_username(username):
    u = User.query.filter(func.lower(User.username) == username.lower()).first()
    if not u:
        return {"errors": {"message": "User not found"}}, 404
    return {"user": u.to_dict(include_follow_data=True, viewer_id=current_user.id)}, 200

@user_routes.route("/by-username/<string:username>/binders")
@login_required
def binders_by_username(username):
    u = User.query.filter(func.lower(User.username) == username.lower()).first()
    if not u:
        return {"errors": {"message": "User not found"}}, 404

    binders = u.binders
    return {"binders": [b.to_dict() for b in binders]}, 200

@user_routes.route("/<int:id>", methods=["PUT"])
@login_required
def update_user(id):
    if current_user.id != id:
        return {"errors": {"message": "Unauthorized"}}, 403

    data = request.get_json()
    current_user.username = data.get("username", current_user.username)
    current_user.email = data.get("email", current_user.email)
    current_user.first_name = data.get("first_name", current_user.first_name)
    current_user.last_name = data.get("last_name", current_user.last_name)

    db.session.commit()
    return {"user": current_user.to_dict()}

@user_routes.route("/<int:id>", methods=["DELETE"])
@login_required
def delete_user(id):
    if current_user.id != id:
        return {"errors": {"message": "Unauthorized"}}, 403

    db.session.delete(current_user)
    db.session.commit()
    return {"message": "User deleted successfully"}
