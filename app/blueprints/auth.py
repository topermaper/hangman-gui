import requests
from urllib.parse import urljoin

from flask import make_response, Blueprint, render_template, redirect, url_for, request, flash,session
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.api.api_interface import APIInterface

from app import app,login_manager

auth = Blueprint('auth',__name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email    = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    try:
        login_response = APIInterface.login(email=email, password=password)
    except Exception as e:
        # if there is an error, we want to redirect back to login page so user can try again
        flash('Can not log in user: {}'.format(e), 'is-danger')
        return redirect(url_for('auth.login'))

    # If the above check passes, then we know the user has the right credentials
    access_token    = login_response.get('access_token')
    refresh_token   = login_response.get('refresh_token')
    user_id         = login_response.get('user',{}).get('id')
    name            = login_response.get('user',{}).get('name')
    email           = login_response.get('user',{}).get('email')

    # UserMixin object must be initialised with id attribute or attempting to log in raises an error
    user = User(id=user_id, name=name, email=email)
    login_user(user, remember=remember)

    # Include access and refresh token
    session['access_token']  = access_token
    session['refresh_token'] = refresh_token
    # Include user extra details
    session['user_name']  = name
    session['user_email'] = email

    resp = make_response(redirect(url_for('gui.home')))

    return resp


@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id,name=session.get('user_name'),email=session.get('user_email'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email    = request.form.get('email')
    name     = request.form.get('name')
    password = request.form.get('password')

    try:
        signup_response = APIInterface.signup(email = email, password = password, name = name)
    except Exception as e:
        # if there is an error, we want to redirect back to signup page so user can try again
        flash('Something went wrong: {}'.format(e), 'is-danger')
        return redirect(url_for('auth.signup'))

    # user successfully created, we want to redirect to the login page
    flash("User created successfully", 'is-success')
    return redirect(url_for('auth.login'))



@auth.route('/logout')
@login_required
def logout():
    resp = redirect(url_for('auth.login'))
    logout_user()
    return resp,302
