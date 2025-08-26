import os
from flask import Flask, request, redirect, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from .models import db, User
from app.seeds import seed_commands
from .config import Config

# ----------------------------
# Initialize Flask app
# ----------------------------
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
app.config.from_object(Config)

if os.environ.get("FLASK_ENV") == "production":
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ----------------------------
# Extensions
# ----------------------------
db.init_app(app)
Migrate(app, db)

# Comment this out if you don’t need CSRF yet
# csrf = CSRFProtect(app)

if os.environ.get('FLASK_ENV') == 'development':
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
else:
    CORS(app, supports_credentials=True)

# ----------------------------
# Login manager (optional)
# ----------------------------
login = LoginManager(app)
login.login_view = 'auth.unauthorized'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# ----------------------------
# CLI commands
# ----------------------------
app.cli.add_command(seed_commands)

# ----------------------------
# Blueprints (add one by one when debugging)
# ----------------------------
from .api.auth_routes import auth_routes
app.register_blueprint(auth_routes, url_prefix="/api/auth")
from .api.user_routes import user_routes
app.register_blueprint(user_routes, url_prefix='/api/users')
from .api.binders import binders_bp
app.register_blueprint(binders_bp, url_prefix="/api/binders")
from .api.comments import comments_bp
app.register_blueprint(comments_bp, url_prefix="/api")
from .api.follows import follows_bp
app.register_blueprint(follows_bp, url_prefix="/api/follows")
from .api.cards import cards_bp
app.register_blueprint(cards_bp, url_prefix="/api/cards")
from .api.sets import sets_bp
app.register_blueprint(sets_bp, url_prefix="/api/sets")
from .api.search import search_bp
app.register_blueprint(search_bp, url_prefix="/api/search")
# ----------------------------
# Middleware (prod only)
# ----------------------------
@app.before_request
def https_redirect():
    if os.environ.get('FLASK_ENV') == 'production':
        if request.headers.get('X-Forwarded-Proto') == 'http':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
        
# ----------------------------
# Routes
# ----------------------------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render assigns PORT
    app.run(host="0.0.0.0", port=port)
