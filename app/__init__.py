from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS
import os

from flask_login import LoginManager

db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

from .models import User  # Import models to ensure they are registered

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key-goes-here' # TODO: Change this in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    with app.app_context():
        # Check for schema updates (simple migration for dev)
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if inspector.has_table("user"):
            columns = [c['name'] for c in inspector.get_columns('user')]
            if 'name' not in columns:
                print("Detected missing 'name' column. Recreating database...")
                db.drop_all()
                
        db.create_all()

    return app
