import requests
from urllib.parse import urljoin

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User

from app import app

auth = Blueprint('auth',__name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    # Build API request
    login_json={"email":email, "password":password}
    login_url = urljoin(app.config['API_BASE_URL'],'login')

    try:
        req = requests.post(url=login_url,json=login_json)
    except:
        # if there is an error, we want to redirect back to login page so user can try again
        flash('Can not contact the server', 'is-danger')
        return redirect(url_for('auth.login'))

    response_message = req.json().get('message')
    
    if req.status_code != 200:
        flash(response_message,'is-danger')
        # API does not authenticate the user, reload the page
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(User(email), remember=remember)
    return redirect(url_for('gui.home'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():

    email    = request.form.get('email')
    name     = request.form.get('name')
    password = request.form.get('password')

    # Build API request
    signup_json={"email":email, "name":name, "password":password}
    login_url = urljoin(app.config['API_BASE_URL'],'users')

    try:
        req = requests.post(url=login_url,json=signup_json)
    except:
        # if there is an error, we want to redirect back to signup page so user can try again
        flash('Can not contact the server', 'is-danger')
        return redirect(url_for('auth.signup'))

    response_message = req.json().get('message')
    
    if req.status_code == 201:
        # user successfully created, we want to redirect to the login page
        flash(response_message, 'is-success')
        return redirect(url_for('auth.login'))
    else:
        # if there is an error, we want to redirect back to signup page so user can try again
        flash(response_message, 'is-danger')
        return redirect(url_for('auth.signup'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('gui.home'))