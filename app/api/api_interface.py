import requests
import json

from flask import request, session
from urllib.parse import urljoin
from app import app
from app.errors.api import RefreshTokenExpiredError
from flask import flash,redirect, url_for

class APIInterface(object):
    
    GAME_URL   = urljoin(app.config['API_BASE_URL'], app.config['API_GAME_URL'])
    TOKEN_URL  = urljoin(app.config['API_BASE_URL'], app.config['API_TOKEN_URL'])
    LOGIN_URL  = urljoin(app.config['API_BASE_URL'], app.config['API_LOGIN_URL'])
    USER_URL   = urljoin(app.config['API_BASE_URL'], app.config['API_USER_URL'])


    def refreshToken():
        # Build request params
        url = APIInterface.TOKEN_URL
        headers  = {'Authorization':'Bearer {}'.format(session.get('refresh_token'))}
    
        # Send token refresh request
        req = requests.post(url = url, headers = headers)
  
        if req.status_code == 200:
            session['access_token'] = req.json().get('access_token')
            return True
        elif req.status_code == 401:
            raise RefreshTokenExpiredError('Refresh token expired')
        else:
            raise Exception('Could not refresh JWT access token. HTTP status {}'.format(req.status_code))
            

    def createGame(reattempt = False):
        # Build request params
        payload  = {'user_id' : int(session['user_id'])} # session user_id is Unicode
        headers  = {'Authorization':'Bearer {}'.format(session.get('access_token'))}

        #Send API request
        req = requests.post(url = APIInterface.GAME_URL, headers = headers, json = payload)
        
        # Game created successfully
        if req.status_code == 201:
            return req.json()
        elif req.status_code != 401 or reattempt == True:
                raise Exception('Can not create game. HTTP status {}'.format(req.status_code))
        
        # Attempt to refresh token
        APIInterface.refreshToken()    

        # Recursive call after getting new access token
        return APIInterface.createGame(reattempt=True)


    def guessWord(game_id, user_guess, reattempt = False):
        # Build request params
        url     = APIInterface.GAME_URL+'/'+str(game_id)
        headers = {'Authorization':'Bearer {}'.format(session.get('access_token'))}
        payload = {'user_guess': user_guess}
        
        # Send API request
        req = requests.patch(url = url, headers = headers, json = payload)
        
        # Game created successfully
        if req.status_code == 200:
            return req.json()
        elif req.status_code != 401 or reattempt == True:
            raise Exception('Can not play game. HTTP status {}'.format(req.status_code))

        # Attempt to refresh token
        APIInterface.refreshToken()

        # Recursive call after getting new access token
        return APIInterface.guessWord(game_id = game_id, user_guess = user_guess, reattempt = True)


    def getHallOfFame(reattempt = False):
        # Build request params
        url      = APIInterface.GAME_URL
        headers  = {'Authorization':'Bearer {}'.format(session.get('access_token'))}
        order_by = [dict(field='score', direction='desc')]
        filters  = [dict(name='status', op= '==', val='WON')]

        params   = dict(q=json.dumps(dict(filters=filters, order_by=order_by, limit=10)))

        # Send API request
        req = requests.get(url = url, headers = headers, params=params)

        # Game created successfully
        if req.status_code == 200:
            return req.json().get('objects')

        # Attempt to refresh token
        APIInterface.refreshToken()

        # Recursive call after getting new access token
        return APIInterface.getHallOfFame(reattempt=True)


    def login(email, password):
        # Build request params
        url  = APIInterface.LOGIN_URL
        payload = {
            'email'    : email,
            'password' : password
        }
        
        # Send API request
        req = requests.post(url = url, json = payload)

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


    def signup(email, password, name):
        # Build request params
        url = APIInterface.USER_URL
        payload = {'email' : email, 'password' : password, 'name' : name}
        
        # Send API request
        req = requests.post(url = url, json = payload)

        if req.status_code != 201:
            message = req.json().get('message')
            raise Exception(message)

        id = req.json().get('id')
        
        response = {
            "id" : id
        }

        return 
        
    
    def getHallOfFame(reattempt = False):
        # Build request params
        url      = APIInterface.GAME_URL
        headers  = {'Authorization':'Bearer {}'.format(session.get('access_token'))}
        order_by = [dict(field='score', direction='desc')]
        filters  = [dict(name='status', op= '==', val='WON')]

        params   = dict(q=json.dumps(dict(filters=filters, order_by=order_by, limit=10)))

        # Send API request
        req = requests.get(url = url, headers = headers, params=params)

        # Game created successfully
        if req.status_code == 200:
            return req.json().get('objects')

        # Attempt to refresh token
        APIInterface.refreshToken()

        # Recursive call after getting new access token
        return APIInterface.getHallOfFame(reattempt=True)


    def getGames(params={}, reattempt = False):
        # Build request params
        url      = APIInterface.GAME_URL
        headers  = {'Authorization':'Bearer {}'.format(session.get('access_token'))}

        # Send API request
        req = requests.get(url = url, headers = headers, params = params)

        # Game created successfully
        if req.status_code == 200:
            return req.json().get('objects')

        # Attempt to refresh token
        APIInterface.refreshToken()

        # Recursive call after getting new access token
        return APIInterface.getGames(params = params, reattempt = True)


    def getGame(game_id, reattempt = False):
        # Build request params
        url      = '{url}/{game_id}'.format(url = APIInterface.GAME_URL, game_id = str(game_id))
        headers  = {'Authorization':'Bearer {}'.format(session.get('access_token'))}

        # Send API request
        req = requests.get(url = url, headers = headers)

        # Game created successfully
        if req.status_code == 200:
            return req.json()

        # Attempt to refresh token
        APIInterface.refreshToken()

        # Recursive call after getting new access token
        return APIInterface.getGame(game_id = game_id, reattempt = True)


    def getUserLastActiveGame(user_id):
        # Build query params
        order_by = [dict(field='id', direction='desc')]
        filters  = [dict(name='status', op= '==', val='ACTIVE')]

        params   = dict(q=json.dumps(dict(filters=filters, order_by=order_by, limit=1)))

        return APIInterface.getGames(params = params)

  