from flask import Blueprint,render_template, flash, get_flashed_messages, request, redirect, url_for, session

from flask_login import login_required, current_user, logout_user

from app import app,login_manager
from app.models.hangman import Hangman
from app.models.user import User
from app.forms.game import GameForm
from app.forms.pending_game import PendingGameForm
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

'''
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
'''


@gui.route('/play')
@login_required
def play():
  
    try:
        games = APIInterface.getUserLastActiveGame(current_user.id)
    except RefreshTokenExpiredError as e:
        # Refresh token expired, we have to log in again
        flash('Session expired. Log in again','is-danger')
        return redirect(url_for('auth.logout'))
    except Exception as e:
        flash('Failed to retrieve last game. {}'.format(e),'is-danger')
        return render_template('home.html')

    # There are active games
    if len(games) > 0:
        # Games is a one game list
        game = games[0]
        form = PendingGameForm()
        form.game_id.data = game.get('id')
        return render_template('pending_game.html', game = game, form = form )

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

    game_form         = GameForm()
    pending_game_form = PendingGameForm()

    # True if game form submit button has been pressed
    if game_form.submit.data:
        # Validate form
        if game_form.validate():
            # Restore game from the session
            current_game = session.get('current_game')
            hangman = Hangman(**current_game)

            try:
                hangman.guessWord(user_guess_char = game_form.guess_character.data)
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
            for fieldName, errorMessages in game_form.errors.items():
                for errorMessage in errorMessages:
                    flash('{} - {}'.format(fieldName,errorMessage), 'is-danger')

    # If submit button from game_form not pressed then pending game form has been submitted
    elif pending_game_form.validate():
        new_game     = pending_game_form.new_game.data
        restore_game = pending_game_form.restore_game.data
        game_id      = pending_game_form.game_id.data

        # New game button pressed
        if new_game:
            flash('Starting new game', 'is-success')
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

        # Restore game button pressed
        elif restore_game:
            hangman = Hangman()
            hangman.loadGame(game_id)

    # Reset form
    game_form.guess_character.data = ''
    return render_template('play.html', hangman = hangman, form = game_form)