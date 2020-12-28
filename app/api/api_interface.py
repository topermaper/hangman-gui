import requests
import json

from flask import request, session
from urllib.parse import urljoin
from app import app

class APIInterface(object):
    
    GAME_URL      = urljoin(app.config['API_BASE_URL'], app.config['API_GAMES_URL'])
    TOKEN_URL     = urljoin(app.config['API_BASE_URL'], app.config['API_TOKENS_URL'])
    LOGIN_URL     = urljoin(app.config['API_BASE_URL'], app.config['API_LOGIN_URL'])
    USER_URL      = urljoin(app.config['API_BASE_URL'], app.config['API_USERS_URL'])

    def refreshToken():
        try:
            req = requests.post(url = APIInterface.TOKEN_URL, headers = {"Authorization":"Bearer " + session.get('refresh_token')})
        except Exception as e:
            return False
  
        if req.status_code != 200:
            return False

        session['access_token'] = req.json().get('access_token')

        return True

    def createGame(reattempt = False):

        # session user_id is Unicode
        json={"user_id" : int(session['user_id'])}

        #Send API request
        try:
            req = requests.post(url = APIInterface.GAME_URL, headers = {"Authorization":"Bearer " + session.get('access_token')}, json = json)
        except Exception as e:
            return False
        
        # Game created successfully
        if req.status_code == 201:
            return req.json()

        # Already refreshed token and failed again
        if reattempt:
            return False

        # Attempt to refresh token
        if not APIInterface.refreshToken():
            return False

        # Recursive call after getting new access token
        if req.status_code == 201:
            return APIInterface.createGame(reattempt=True)
        else:
            raise Exception("API returned not expected status {}".format(req.status_code))


    def guessWord(game_id, user_guess, reattempt = False):
        # Build request
        url     = APIInterface.GAME_URL+'/'+str(game_id)
        headers = {"Authorization":"Bearer " + session.get('access_token')}
        json    = {"user_guess": user_guess}
        
        # Send API request
        try:
            req = requests.patch(url = url, headers = headers, json = json)
        except Exception as e:
            print(e)
            return False
        
        # Game created successfully
        if req.status_code == 200:
            return req.json()

        # Already refreshed token and failed again
        if reattempt:
            return False

        # Attempt to refresh token
        if not APIInterface.refreshToken():
            return False

        # Recursive call after getting new access token
        if req.status_code == 200:
            return APIInterface.guessWord(game_id = game_id, user_guess = user_guess, reattempt = True)
        else:
            raise Exception("API returned not expected status {}".format(req.status_code))


    def getHallOfFame(reattempt = False):
        # Build request params
        url      = APIInterface.GAME_URL
        headers  = {"Authorization":"Bearer " + session.get('access_token')}
        order_by = [dict(field='score', direction='desc')]
        filters  = [dict(name='status', op= '==', val='WON')]

        params   = dict(q=json.dumps(dict(filters=filters, order_by=order_by, limit=10)))

        # Send API request
        req = requests.get(url = url, headers = headers, params=params)
        
        # Game created successfully
        if req.status_code == 200:
            return req.json().get('objects')

        # Already refreshed token and failed again
        if reattempt:
            return False

        # Attempt to refresh token
        if not APIInterface.refreshToken():
            return False

        # Recursive call after getting new access token
        if req.status_code == 201:
            return APIInterface.getHallOfFame(reattempt=True)
        else:
            raise Exception("API returned not expected status {}".format(req.status_code))


    def getUser(user_id, reattempt = False):
        url = "{}/{}".format(APIInterface.USER_URL,str(user_id))
        headers = {"Authorization":"Bearer " + session.get('access_token')}

        #Send API request
        try:
            req = requests.get(url = url, headers = headers)
        except Exception as e:
            return False

        # User retrieved successfully
        if req.status_code == 200:
            response_json = req.json()
            return {
                "id"    : response_json.get('id'),
                "email" : response_json.get('email'),
                "name"  : response_json.get('name')            
            }

        # Already refreshed token and failed again
        if reattempt:
            return False

        # Attempt to refresh token
        if not APIInterface.refreshToken():
            return False

        # Recursive call after getting new access token
        if req.status_code == 200:
            return APIInterface.getUser(reattempt=True)
        else:
            raise Exception("Could not get retrieve user information. Got HTTP status {}".format(req.status_code))


    def login(email, password):
        # Build request
        url     = APIInterface.LOGIN_URL
        json    = {"email":email, "password":password}
        
        # Send API request
        req = requests.post(url = url, json = json)

        if req.status_code != 200:
            message = req.json().get('message')
            raise Exception(message)

        user          = req.json().get('user')
        access_token  = req.json().get('access_token')
        refresh_token = req.json().get('refresh_token')
        
        response = {
            "user"          : user,
            "access_token"  : access_token,
            "refresh_token" : refresh_token,
        }

        return response