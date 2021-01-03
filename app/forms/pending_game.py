from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Regexp


class PendingGameForm(FlaskForm):
    game_id      = HiddenField('Game id')
    new_game     = SubmitField('New game')
    restore_game = SubmitField('Restore last game')