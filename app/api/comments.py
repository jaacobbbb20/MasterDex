from flask import Blueprint, request
from flask_login import login_required, current_user
from ..models.db import db
from ..models.comment import Comment
from ..models.binder import Binder

comments_bp = Blueprint("comments", __name__)

# ------------------------------
# Get all comments for a binder
# ------------------------------
@comments_bp.route("/binders/<int:binder_id>/comments", methods=["GET"])
def get_comments_for_binder(binder_id):
    binder = Binder.query.get(binder_id)
    
    if not binder:
        return {"errors": {"message": "Binder not found"}}, 404

    comments = (
        Comment.query
        .filter_by(binder_id=binder_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return {"comments": [c.to_dict() for c in comments]}, 200

# ------------------------------
# Add a comment to a binder
# ------------------------------
@comments_bp.route("/binders/<int:binder_id>/comments", methods=["POST"])
@login_required
def add_comment_to_binder(binder_id):
    binder = Binder.query.get_or_404(binder_id)

    if binder.user_id == current_user.id:
        return {"errors": {"message": "You cannot comment on your own binder"}}, 403

    data = request.get_json()
    content = (data.get("content") or "").strip()
    if not content:
        return {"errors": {"message": "Content is required"}}, 400

    comment = Comment(
        content=content,
        user_id=current_user.id,
        binder_id=binder_id
    )
    db.session.add(comment)
    db.session.commit()
    return comment.to_dict(), 201

# ------------------------------
# Update a comment (only author)
# ------------------------------
@comments_bp.route("/comments/<int:comment_id>", methods=["PUT"])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return {"errors": {"message": "Unauthorized"}}, 403

    data = request.get_json()
    content = (data.get("content") or "").strip()
    if not content:
        return {"errors": {"message": "Content is required"}}, 400

    comment.content = content
    db.session.commit()
    return comment.to_dict()

# ------------------------------
# Delete a comment (only author)
# ------------------------------
@comments_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return {"errors": {"message": "Unauthorized"}}, 403

    db.session.delete(comment)
    db.session.commit()
    return {"message": "Comment deleted successfully"}
