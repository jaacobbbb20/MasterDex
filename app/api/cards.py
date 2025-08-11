import requests
import os
from flask import Blueprint, request, jsonify

cards_bp = Blueprint('cards', __name__)

BASE_URL = "https://api.pokemontcg.io/v2"

def get_headers():
    """THIS IS A HELPER FUNCTION THAT GETS NECESSARY API HEADERS"""
    headers = {}
    api_key = os.environ.get('POKEMON_TCG_API_KEY')
    if api_key:
        headers['X-Api-Key'] = api_key
    return headers

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