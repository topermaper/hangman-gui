from flask import Flask
from flask_login import LoginManager
from flask_session import Session

# Start Flask app
app = Flask(__name__)
app.config.from_object('configuration.DevelopmentConfig')

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Initialize session
session = Session()
session.init_app(app)

# import blueprints
from app.blueprints.gui import gui
app.register_blueprint(gui)
from app.blueprints.auth import auth
app.register_blueprint(auth)
