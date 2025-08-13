from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Binder

binder_routes = Blueprint('binders', __name__)

@binder_routes.route('/binders', methods=['GET'])
@login_required
def get_user_binders():
    binders = Binder.query.filter_by(user_id=current_user.get_id()).all()
    return jsonify([binder.to_dict() for binder in binders])

@binder_routes.route('/binders', methods=['POST'])
@login_required
def create_binder():
    data = request.json
    new_binder = Binder(
        name=data['name'],
        description=data['description'],
        is_public=data.get('is_public', False),
        user_id=current_user.get_id()
    )
    db.session.add(new_binder)
    db.session.commit()
    return jsonify(new_binder.to_dict()), 201

@binder_routes.route('/binders/<int:binder_id>', methods=['GET'])
@login_required
def get_binder(binder_id):
    binder = Binder.query.get_or_404(binder_id)
    if binder.user_id != current_user.get_id():
        return jsonify({"msg": "Unauthorized"}), 403
    return jsonify(binder.to_dict())

@binder_routes.route('/binders/<int:binder_id>/cards', methods=['GET'])
@login_required
def get_binder_cards(binder_id):
    binder = Binder.query.get_or_404(binder_id)
    if binder.user_id != current_user.get_id():
        return jsonify({"msg": "Unauthorized"}), 403
    cards = binder.binder_cards.all()
    return jsonify([card.to_dict() for card in cards])