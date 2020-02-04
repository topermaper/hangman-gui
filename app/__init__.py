from flask import Flask, session
from flask_login import LoginManager
#from flask import Session

# Start Flask app
app = Flask(__name__)
app.config.from_object('configuration.DevelopmentConfig')

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Initialize session
#session = Session()
#sess.init_app(app)

from app.models.user import User
@login_manager.user_loader
def load_user(user_id):
    print(user_id)
    print(session)
    print(session.get('user_id'))
    return User(user_id)


# import blueprints
from app.blueprints.gui import gui
app.register_blueprint(gui)
from app.blueprints.auth import auth
app.register_blueprint(auth)
