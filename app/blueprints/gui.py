from flask import Blueprint,render_template, flash, get_flashed_messages, request, redirect, url_for, session

from flask_login import login_required, current_user, logout_user

from app import app,login_manager
from app.models.hangman import Hangman
from app.models.user import User
from app.forms.game import GameForm
from app.errors.api import RefreshTokenExpiredError
from app.api.api_interface import APIInterface


gui = Blueprint('gui',__name__)


@gui.route('/')
@login_required
def home():
    return render_template('home.html')


@gui.route('/halloffame')
def halloffame():
    try:
        games = APIInterface.getHallOfFame()
    except RefreshTokenExpiredError as e:
        # Refresh token expired, we have to log in again
        flash('Session expired. Log in again','is-danger')
        return redirect(url_for('auth.logout'))
    except Exception as e:
        flash('Failed to retrieve Hall of Fame. {}'.format(e),'is-danger')
        return render_template('halloffame.html')

    return render_template('halloffame.html',games=games)


@gui.route('/play')
@login_required
def play():
    user = current_user
    hangman = Hangman()
    try:
        hangman.startGame()
    except RefreshTokenExpiredError as e:
        # Refresh token expired, we have to log in again
        flash('Session expired. Log in again','is-danger')
        return redirect(url_for('auth.logout'))
    except Exception as e:
        flash('Failed to start game. {}'.format(e),'is-danger')
        return render_template('home.html')
    
    return render_template('play.html', hangman = hangman, form = GameForm())


@gui.route('/play',methods=['POST'])
@login_required
def play_post():
    current_game = session.get('current_game')
    hangman = Hangman(**current_game)

    form = GameForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                hangman.guessWord(user_guess_char = form.guess_character.data)
            except RefreshTokenExpiredError as e:
                # Refresh token expired, we have to log in again
                flash('Session expired. Log in again','is-danger')
                return redirect(url_for('auth.logout'))
            except Exception as e:
                flash("Something went wrong submitting your guess character. {}".format(e), 'is-danger')

            if hangman.status == 'WON':
                flash('{}, you are awesome! You won the game scoring {} points.'.format(session.get('user_name'),hangman.score), 'is-success')
            elif hangman.status == 'LOST':
                flash('{}, you are a loser'.format(session.get('user_name')), 'is-danger')
        else:
            flash('We can not validate your guess:', 'is-danger')
            for fieldName, errorMessages in form.errors.items():
                for errorMessage in errorMessages:
                    flash("{} - {}".format(fieldName,errorMessage), 'is-danger')

        form.guess_character.data = ""
        return render_template('play.html', hangman=hangman, form=form)
        
    if hangman == None:
        flash('Starting new game', 'is-success')
        hangman = Hangman(current_user.id)
    else:
        flash('You had a previous unfinished game', 'is-danger')

    session['current_game'] = hangman.__dict__

    return render_template('play.html',hangman=hangman,form=form)