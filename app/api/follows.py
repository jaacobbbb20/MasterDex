from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy import func, exists
from ..models.db import db
from ..models.follow import Follow
from ..models.user import User

follows_bp = Blueprint("follows", __name__)

# ---------- helpers ----------
def _counts_payload(viewer_id: int, target_id: int):
  """Return consistent follow state + counts for UI."""
  is_following = db.session.query(
      exists().where(
        (Follow.follower_id == viewer_id) &
        (Follow.following_id == target_id)
      )
    ).scalar()

  followers_count = db.session.query(func.count(Follow.id)).filter(
      Follow.following_id == target_id
    ).scalar()

  following_count = db.session.query(func.count(Follow.id)).filter(
      Follow.follower_id == target_id
    ).scalar()

  viewer_following_count = db.session.query(func.count(Follow.id)).filter(
      Follow.follower_id == viewer_id
    ).scalar()

  return {
    "user_id": target_id,
    "isFollowing": bool(is_following),            # does viewer follow target?
    "followersCount": int(followers_count),       # how many follow target
    "followingCount": int(following_count),       # how many target follows
    "viewerFollowingCount": int(viewer_following_count),  # how many viewer follows
  }

# ---------- toggle (POST follow / DELETE unfollow) ----------
@follows_bp.route("/<int:user_id>", methods=["POST", "DELETE"])
@login_required
def follow_toggle(user_id):
    if user_id == current_user.id:
        return {"errors": {"message": "You cannot follow yourself"}}, 400

    User.query.get_or_404(user_id)

    rel = Follow.query.filter_by(
        follower_id=current_user.id, following_id=user_id
    ).first()

    if request.method == "POST":
        if not rel:
            db.session.add(Follow(follower_id=current_user.id, following_id=user_id))
    else:
        if rel:
            db.session.delete(rel)

    db.session.commit()

    is_following = Follow.query.filter_by(
        follower_id=current_user.id, following_id=user_id
    ).first() is not None

    followers_count = Follow.query.filter_by(following_id=user_id).count()
    following_count = Follow.query.filter_by(follower_id=user_id).count()

    return {
        "user_id": user_id,
        "isFollowing": is_following,
        "followersCount": followers_count,
        "followingCount": following_count,
    }, 200

# ---------- lists ----------
@follows_bp.route("/<int:user_id>/followers", methods=["GET"])
@login_required
def get_followers(user_id):
  user = User.query.get_or_404(user_id)
  return {"followers": [f.follower.to_dict_basic() for f in user.followers]}

@follows_bp.route("/<int:user_id>/following", methods=["GET"])
@login_required
def get_following(user_id):
  user = User.query.get_or_404(user_id)
  return {"following": [f.following.to_dict_basic() for f in user.following]}
