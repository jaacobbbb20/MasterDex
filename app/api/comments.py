from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Comment, Binder, UserCard

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/', methods=['POST'])
@login_required
def create_comment():
    """Create a new comment on a binder or user card"""
    try:
        data = request.get_json()
        
        # Validate required fields
        content = data.get('content', '').strip()
        commentable_type = data.get('commentable_type')
        commentable_id = data.get('commentable_id')
        parent_comment_id = data.get('parent_comment_id')
        
        if not content:
            return jsonify({"error": "Comment content is required"}), 400
        
        if commentable_type not in ['binder', 'user_card']:
            return jsonify({"error": "Invalid commentable type"}), 400
        
        if not commentable_id:
            return jsonify({"error": "Commentable ID is required"}), 400
        
        if commentable_type == 'binder':
            target = Binder.query.get(commentable_id)
            if not target:
                return jsonify({"error": "Binder not found"}), 404
            if not target.is_public and target.user_id != current_user.id:
                return jsonify({"error": "Cannot comment on private binder"}), 403
                
        elif commentable_type == 'user_card':
            target = UserCard.query.get(commentable_id)
            if not target:
                return jsonify({"error": "Card not found"}), 404
        
        if parent_comment_id:
            parent_comment = Comment.query.get(parent_comment_id)
            if not parent_comment:
                return jsonify({"error": "Parent comment not found"}), 404
            if (parent_comment.commentable_type != commentable_type or 
                parent_comment.commentable_id != commentable_id):
                return jsonify({"error": "Invalid parent comment"}), 400
        
        # Create the comment
        comment = Comment(
            content=content,
            user_id=current_user.id,
            commentable_type=commentable_type,
            commentable_id=commentable_id,
            parent_comment_id=parent_comment_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            "message": "Comment created successfully",
            "comment": comment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@comments_bp.route('/<commentable_type>/<int:commentable_id>', methods=['GET'])
def get_comments(commentable_type, commentable_id):
    """Get all comments for a specific binder or user card"""
    try:
        if commentable_type not in ['binder', 'user_card']:
            return jsonify({"error": "Invalid commentable type"}), 400
        
        if commentable_type == 'binder':
            target = Binder.query.get(commentable_id)
            if not target:
                return jsonify({"error": "Binder not found"}), 404
            if not target.is_public and (not current_user.is_authenticated or target.user_id != current_user.id):
                return jsonify({"error": "Cannot view comments on private binder"}), 403
                
        elif commentable_type == 'user_card':
            target = UserCard.query.get(commentable_id)
            if not target:
                return jsonify({"error": "Card not found"}), 404
        
        comments = Comment.query.filter_by(
            commentable_type=commentable_type,
            commentable_id=commentable_id,
            parent_comment_id=None
        ).order_by(Comment.created_at.desc()).all()
        
        return jsonify({
            "comments": [comment.to_dict(include_replies=True) for comment in comments],
            "total_comments": Comment.query.filter_by(
                commentable_type=commentable_type,
                commentable_id=commentable_id
            ).count()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@login_required
def update_comment(comment_id):
    """Update a comment (only by the author)"""
    try:
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
        
        if not comment.can_edit(current_user):
            return jsonify({"error": "You can only edit your own comments"}), 403
        
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({"error": "Comment content is required"}), 400
        
        comment.content = content
        db.session.commit()
        
        return jsonify({
            "message": "Comment updated successfully",
            "comment": comment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    """Delete a comment (only by the author)"""
    try:
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return jsonify({"error": "Comment not found"}), 404
        
        if not comment.can_delete(current_user):
            return jsonify({"error": "You can only delete your own comments"}), 403
        

        Comment.query.filter_by(parent_comment_id=comment_id).delete()
        db.session.delete(comment)
        db.session.commit()
        
        return jsonify({"message": "Comment deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@comments_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_comments(user_id):
    """Get all comments by a specific user"""
    try:
        comments = Comment.query.filter_by(user_id=user_id).order_by(Comment.created_at.desc()).all()
        
        return jsonify({
            "comments": [comment.to_dict() for comment in comments],
            "total_comments": len(comments)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500