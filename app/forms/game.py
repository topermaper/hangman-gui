from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class GameForm(FlaskForm):
    guess_character = StringField('Your guess', validators=[
        Regexp('^[A-Za-z0-9]$', message="Only alphabet characters and digits"),
        DataRequired(),
        Length(max=1)])
    submit = SubmitField('Guess secret word')