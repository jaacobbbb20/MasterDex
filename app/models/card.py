from datetime import datetime
from .db import db, environment, SCHEMA, add_prefix_for_prod

class PokemonCard(db.Model):
    __tablename__ = 'pokemon_cards'
    
    if environment == "production":
        __table_args__ = {'schema': SCHEMA}
        
    # Primary key - Use String for Pokemon TCG API IDs
    id = db.Column(db.String(50), primary_key=True)  # API uses string IDs like "base1-4"
    
    # Basic card information, comes from the API
    name = db.Column(db.String(100), nullable=False)
    supertype = db.Column(db.String(50))  # Pokémon, Trainer, Energy
    subtypes = db.Column(db.String(200))  # Basic, Stage 1, etc. (comma-separated)
    
    # Set information
    set_id = db.Column(db.String(50))
    set_name = db.Column(db.String(100)) # e.g., "151", "Crown Zenith"
    set_series = db.Column(db.String(100)) # e.g., "Sword & Shield", "Scarlet & Violet"
    number = db.Column(db.String(20))  # Card number (e.g., "34/161")
    total_in_set = db.Column(db.Integer) # Total number of cards in the set
    
    # Rarity and value
    rarity = db.Column(db.String(50))
    artist = db.Column(db.String(100))
    
    # Images from API
    image_small = db.Column(db.String(500))  # Small image URL
    image_large = db.Column(db.String(500))  # Large image URL
    
    # Pokemon-specific data
    hp = db.Column(db.Integer)
    types = db.Column(db.String(100))  # Comma-separated types
    evolves_from = db.Column(db.String(100))
    
    # Market data
    market_price = db.Column(db.Float)
    last_price_update = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PokemonCard {self.name} ({self.id})>'
    
    def get_types_list(self):
        """Return types as a list"""
        if self.types:
            return [t.strip() for t in self.types.split(',')]
        return []
    
    def get_subtypes_list(self):
        """Return subtypes as a list"""
        if self.subtypes:
            return [s.strip() for s in self.subtypes.split(',')]
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'supertype': self.supertype,
            'subtypes': self.get_subtypes_list(),
            'set_id': self.set_id,
            'set_name': self.set_name,
            'set_series': self.set_series,
            'number': self.number,
            'total_in_set': self.total_in_set,
            'rarity': self.rarity,
            'artist': self.artist,
            'image_small': self.image_small,
            'image_large': self.image_large,
            'hp': self.hp,
            'types': self.get_types_list(),
            'evolves_from': self.evolves_from,
            'market_price': self.market_price,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UserCard(db.Model):
    """Junction table for user's card collection"""
    __tablename__ = 'user_cards'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys - Note: card_id should be String to match PokemonCard.id
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    card_id = db.Column(db.String(50), db.ForeignKey(add_prefix_for_prod('pokemon_cards.id')), nullable=False)
    
    # Collection details
    quantity = db.Column(db.Integer, default=1)
    condition = db.Column(db.String(20), default='near_mint')  # mint, near_mint, lightly_played, etc.
    is_favorite = db.Column(db.Boolean, default=False)
    
    # Purchase/acquisition info
    acquired_date = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_price = db.Column(db.Float)
    notes = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref='user_cards')
    card = db.relationship('PokemonCard', backref='owned_by_users')
    
    def __repr__(self):
        return f'<UserCard User:{self.user_id} Card:{self.card_id} (qty: {self.quantity})>'
    
    @property
    def total_value(self):
        """Calculate total value based on quantity and market price"""
        if self.card and self.card.market_price:
            return self.quantity * self.card.market_price
        return 0.0
    
    @property
    def comments(self):
        """Get all comments for this user card"""
        from .comment import Comment
        return Comment.query.filter_by(
            commentable_type='user_card',
            commentable_id=self.id,
            parent_comment_id=None
        ).order_by(Comment.created_at.desc()).all()
    
    @property
    def comment_count(self):
        """Get total number of comments (including replies)"""
        from .comment import Comment
        return Comment.query.filter_by(
            commentable_type='user_card',
            commentable_id=self.id
        ).count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'card_id': self.card_id,
            'quantity': self.quantity,
            'condition': self.condition,
            'is_favorite': self.is_favorite,
            'acquired_date': self.acquired_date.isoformat() if self.acquired_date else None,
            'purchase_price': self.purchase_price,
            'notes': self.notes,
            'total_value': self.total_value,
            'card': self.card.to_dict() if self.card else None,
            'comment_count': self.comment_count
        }

class Set(db.Model):
    """Pokemon TCG Sets"""
    __tablename__ = 'sets'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.String(50), primary_key=True)  # e.g., "base1"
    name = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(100))
    total_cards = db.Column(db.Integer)
    release_date = db.Column(db.String(20))
    # Images
    symbol_image = db.Column(db.String(500))
    logo_image = db.Column(db.String(500))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Set {self.name} ({self.id})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'series': self.series,
            'total_cards': self.total_cards,
            'release_date': self.release_date,
            'symbol_image': self.symbol_image,
            'logo_image': self.logo_image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }