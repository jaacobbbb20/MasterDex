import requests
import os
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, PokemonCard, UserCard

cards_bp = Blueprint('cards', __name__)

BASE_URL = "https://api.pokemontcg.io/v2"

def get_headers():
    """Helper function that gets necessary API headers"""
    headers = {}
    api_key = os.environ.get('POKEMON_TCG_API_KEY')
    if api_key:
        headers['X-Api-Key'] = api_key
    return headers

def save_card_to_db(card_data):
    """Helper function to save card data to database"""
    try:
        # Check if card already exists
        existing_card = PokemonCard.query.filter_by(id=card_data['id']).first()
        if existing_card:
            return existing_card
        
        # Create new card
        new_card = PokemonCard(
            id=card_data['id'],
            name=card_data['name'],
            supertype=card_data.get('supertype'),
            subtypes=','.join(card_data.get('subtypes', [])),
            set_id=card_data['set']['id'],
            set_name=card_data['set']['name'],
            set_series=card_data['set']['series'],
            number=card_data.get('number'),
            total_in_set=card_data['set'].get('total'),
            rarity=card_data.get('rarity'),
            artist=card_data.get('artist'),
            image_small=card_data['images']['small'],
            image_large=card_data['images']['large'],
            hp=card_data.get('hp'),
            types=','.join(card_data.get('types', [])),
            evolves_from=card_data.get('evolvesFrom')
        )
        
        db.session.add(new_card)
        db.session.commit()
        return new_card
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving card to database: {e}")
        return None

@cards_bp.route('/cards', methods=['GET'])
def search_cards():
    """Search/Filter Pokemon Cards"""
    try:
        query_params = request.args.to_dict()
        
        if 'pageSize' not in query_params:
            query_params['pageSize'] = '20'

        response = requests.get(
            f"{BASE_URL}/cards",
            params=query_params,
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch cards"}), response.status_code
        
        return jsonify(response.json())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/cards/<card_id>', methods=['GET'])
def get_card_details(card_id):
    """Get details for a specific card"""
    try:
        response = requests.get(
            f"{BASE_URL}/cards/{card_id}",
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code == 404:
            return jsonify({"error": "Card not found"}), 404
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch card details"}), response.status_code
        
        return jsonify(response.json())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/sets', methods=['GET'])
def get_sets():
    """Get all available sets"""
    try:
        query_params = request.args.to_dict()
        
        response = requests.get(
            f"{BASE_URL}/sets",
            params=query_params,
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch sets"}), response.status_code
        
        return jsonify(response.json())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW ROUTES FOR BINDER FUNCTIONALITY

@cards_bp.route('/binder/add', methods=['POST'])
@login_required
def add_card_to_binder():
    """Add a card to user's binder"""
    try:
        data = request.get_json()
        card_id = data.get('card_id')
        quantity = data.get('quantity', 1)
        condition = data.get('condition', 'near_mint')
        purchase_price = data.get('purchase_price')
        
        if not card_id:
            return jsonify({"error": "Card ID is required"}), 400
        
        # First, get card data from API and save to database
        response = requests.get(
            f"{BASE_URL}/cards/{card_id}",
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({"error": "Card not found in API"}), 404
        
        card_data = response.json()['data']
        saved_card = save_card_to_db(card_data)
        
        if not saved_card:
            return jsonify({"error": "Failed to save card"}), 500
        
        # Check if user already has this card
        existing_user_card = UserCard.query.filter_by(
            user_id=current_user.id,
            card_id=saved_card.id
        ).first()
        
        if existing_user_card:
            existing_user_card.quantity += quantity
            if purchase_price:
                existing_user_card.purchase_price = purchase_price
        else:
            new_user_card = UserCard(
                user_id=current_user.id,
                card_id=saved_card.id,
                quantity=quantity,
                condition=condition,
                purchase_price=purchase_price
            )
            db.session.add(new_user_card)
        
        db.session.commit()
        
        return jsonify({
            "message": "Card added to binder successfully",
            "card": saved_card.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/binder', methods=['GET'])
@login_required
def get_user_binder():
    """Get user's card collection"""
    try:
        user_cards = UserCard.query.filter_by(user_id=current_user.id).all()
        
        binder_data = []
        for user_card in user_cards:
            card_dict = user_card.to_dict()
            binder_data.append(card_dict)
        
        return jsonify({
            "binder": binder_data,
            "total_cards": len(user_cards),
            "total_value": sum(uc.total_value for uc in user_cards)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/binder/<int:user_card_id>', methods=['DELETE'])
@login_required
def remove_card_from_binder(user_card_id):
    """Remove a card from user's binder"""
    try:
        user_card = UserCard.query.filter_by(
            id=user_card_id,
            user_id=current_user.id
        ).first()
        
        if not user_card:
            return jsonify({"error": "Card not found in your binder"}), 404
        
        db.session.delete(user_card)
        db.session.commit()
        
        return jsonify({"message": "Card removed from binder"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@cards_bp.route('/binder/<int:user_card_id>/favorite', methods=['PATCH'])
@login_required
def toggle_favorite(user_card_id):
    """Toggle favorite status of a card"""
    try:
        user_card = UserCard.query.filter_by(
            id=user_card_id,
            user_id=current_user.id
        ).first()
        
        if not user_card:
            return jsonify({"error": "Card not found in your binder"}), 404
        
        user_card.is_favorite = not user_card.is_favorite
        db.session.commit()
        
        return jsonify({
            "message": "Favorite status updated",
            "is_favorite": user_card.is_favorite
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500