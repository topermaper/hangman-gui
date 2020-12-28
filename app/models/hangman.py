import requests
from urllib.parse import urljoin
from app import app
from app.models.user import User
from flask import session
from app.api.api_interface import APIInterface

class Hangman(object):

    def __init__(self, **kwargs):
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

    # Main method, new_user_guess has to be a list
    def set_user_guess(self, new_user_guess):

        if not self.validate_user_guess(new_user_guess):
            return False

        self.user_guess = ''.join(new_user_guess)

        if new_user_guess[-1] not in self.secret_word:
            self.misses += 1
            self.update_user_score(False)
        else:
            self.update_user_score(True)
 
        # Update the game status
        self.update_game_status()

        return True

    def get_user_guess(self):
        return list(self.user_guess)

    def get_word_mask(self):
        word_mask = []
        for i in range(len(self.secret_word)):
            if self.secret_word[i] not in self.user_guess:
                word_mask.append(i)

        return word_mask

    def startGame(self):
        response_json = APIInterface.createGame()

        self.id          = response_json.get('id')
        self.misses      = response_json.get('misses')
        self.score       = response_json.get('score')
        self.multiplier  = response_json.get('multiplier')
        self.secret_word = response_json.get('secret_word')
        self.status      = response_json.get('status')
        self.user_guess  = response_json.get('user_guess')

        # Store current game in the session
        session['current_game'] = self.__dict__
        return True

    def getHallOfFame():
        return APIInterface.getHallOfFame()

    def guessWord(self, user_guess_char):
        response_json = APIInterface.guessWord(game_id = self.id , user_guess = self.user_guess + user_guess_char )

        self.id          = response_json.get('id')
        self.misses      = response_json.get('misses')
        self.score       = response_json.get('score')
        self.secret_word = response_json.get('secret_word')
        self.status      = response_json.get('status')
        self.user_guess  = response_json.get('user_guess')
        self.multiplier  = response_json.get('multiplier')

        # Store current game in the session
        session['current_game'] = self.__dict__

        return True


    def __repr__(self):
        return "Game:{}, status:{}, score:{}, guesses:'{}', misses:{}".format(self.id,self.status,self.score,self.user_guess,self.misses)
