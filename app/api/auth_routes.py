from flask import Blueprint, request
from app.models import User, db
from flask_login import current_user, login_user, logout_user

auth_routes = Blueprint("auth", __name__)

@auth_routes.route("/")
def authenticate():
    """
    Checks if the user is authenticated
    """
    if current_user.is_authenticated:
        return {
            "user": current_user.to_dict(
                include_follow_data=True,
                viewer_id=current_user.id
            )
        }
    return {"user": None}

@auth_routes.route("/login", methods=["POST"])
def login():
    """
    Logs in a user using their email and password
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter(User.email.ilike(email)).first()
    if user and user.check_password(password):
        login_user(user)
        return {
            "user": user.to_dict(
                include_follow_data=True,
                viewer_id=user.id
            )
        }, 200
    return {"errors": {"message": "Invalid credentials"}}, 401

@auth_routes.route("/signup", methods=["POST"])
def sign_up():
    """
    Registers a new user
    """
    data = request.get_json()

    if data["password"] != data["confirmPassword"]:
        return {"errors": {"confirmPassword": "Passwords must match"}}, 400

    try:
        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data["firstName"],
            last_name=data["lastName"],
            password=data["password"],
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return {
            "user": user.to_dict(
                include_follow_data=True,
                viewer_id=user.id
            )
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"errors": {"server": str(e)}}, 400

@auth_routes.route("/logout", methods=["POST"])
def logout():
    """
    Logs out the current user
    """
    logout_user()
    return {"message": "User logged out"}

@auth_routes.route("/unauthorized")
def unauthorized():
    """
    Response given when a user access a protected route without logging in
    """
    return {"errors": {"message": "Unauthorized"}}, 401
