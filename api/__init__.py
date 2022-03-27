# Created by Deltaion Lee (MCMi460) on Github

import requests
import json
import uuid
import time
import sys
import webbrowser
import base64
import os
import hashlib
import re

client_id = '71b963c1b7b6d119'
version = 0.1
nsoAppVersion = '2.0.0'

class API():
    def __init__(self, session_token):
        self.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Coral/2.0.0 (com.nintendo.znca; build:1489; iOS 15.3.1) Alamofire/5.4.4',
        }

        self.tokenResponse = Nintendo(session_token).getServiceToken()
        self.id_token = self.tokenResponse['id_token']
        self.accessToken = self.tokenResponse['access_token']
        self.guid = str(uuid.uuid4())

        self.headers['Authorization'] = 'Bearer %s' % self.accessToken # Add authorization token
        self.url = 'https://api-lp1.znc.srv.nintendo.net'

        self.userInfo = UsersMe(self.accessToken).get()

        self.login = Login(self.userInfo, self.accessToken, self.guid)
        self.login.loginToAccount()
        with open('./private.txt', 'w') as file:
            file.write(json.dumps({
                'session_token': session_token,
            }))

    def makeRequest(self, route):
        return requests.post(self.url + route, headers = self.headers)

class Nintendo():
    def __init__(self, sessionToken):
        self.headers = {
            'User-Agent': 'Coral/2.0.0 (com.nintendo.znca; build:1489; iOS 15.3.1) Alamofire/5.4.4',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
        }
        self.body = {
            'client_id': client_id,
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token',
            'session_token': sessionToken,
        }

        self.url = 'https://accounts.nintendo.com'

    def getServiceToken(self):
        route = '/connect/1.0.0/api/token'
        response = requests.post(self.url + route, headers = self.headers, json = self.body)
        return json.loads(response.text)

class UsersMe():
    def __init__(self, accessToken):
        self.headers = {
            'User-Agent': 'Coral/2.0.0 (com.nintendo.znca; build:1489; iOS 15.3.1) Alamofire/5.4.4',
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % accessToken,
            'Host': 'api.accounts.nintendo.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        self.url = 'https://api.accounts.nintendo.com'

    def get(self):
        route = '/2.0.0/users/me'

        response = requests.get(self.url + route, headers = self.headers)
        return json.loads(response.text)

class s2s():
    def __init__(self, id_token, timestamp):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'NSO-RPC/%s' % version,
        }
        self.body = {
            'naIdToken': id_token,
            'timestamp': timestamp,
        }
        self.url = 'https://elifessler.com'

    def getHash(self):
        route = '/s2s/api/gen2'
        response = requests.post(self.url + route, headers = self.headers, data = self.body)
        return json.loads(response.text)['hash']

class Flapg():
    def __init__(self, id_token, timestamp, guid):
        self.headers = {
            'x-token': id_token,
            'x-time': str(timestamp),
            'x-guid': guid,
            'x-hash': s2s(id_token, timestamp).getHash(),
            'x-ver': '3',
            'x-iid': 'nso',
        }

        self.url = 'https://flapg.com'

    def get(self):
        route = '/ika2/api/login?public'

        response = requests.get(self.url + route, headers = self.headers)
        return json.loads(response.text)['result']

class Login():
    def __init__(self, userInfo, accessToken, guid):
        self.headers = {
            'Host': 'api-lp1.znc.srv.nintendo.net',
            'Accept-Language': 'en-US',
            'User-Agent': 'com.nintendo.znca/' + nsoAppVersion + ' (Android/7.1.2)',
            'Accept': 'application/json',
            'X-ProductVersion': '2.0.0',
            'Content-Type': 'application/json; charset=utf-8',
            'Connection': 'Keep-Alive',
            'Authorization': 'Bearer',
            'X-Platform': 'Android',
            'Accept-Encoding': 'gzip'
        }

        self.url = 'https://api-lp1.znc.srv.nintendo.net'
        self.timestamp = int(time.time())
        self.guid = guid

        self.userInfo = userInfo
        self.accessToken = accessToken

        self.flapg = Flapg(self.accessToken, self.timestamp, self.guid).get()

        self.account = None

    def loginToAccount(self):
        route = '/v3/Account/Login'
        body = {
            'parameter': {
                'f': self.flapg['f'],
                'naIdToken': self.flapg['p1'],
                'timestamp': self.flapg['p2'],
                'requestId': self.flapg['p3'],
                'naCountry': self.userInfo['country'],
                'naBirthday': self.userInfo['birthday'],
                'language': self.userInfo['language'],
            },
        }
        response = requests.post(self.url + route, headers = self.headers, json = body)
        self.account = json.loads(response.text)
        return self.account

class FriendList(API):
    def __init__(self):
        super().__init__()

        self.route = '/v3/Friend/List' # Define API route

        self.friendList = [] # List of Friend object(s)

    def populateList(self):
        response = self.makeRequest(self.route)
        arr = json.loads(response.text)['result']['friends']
        self.friendList = [ Friend(friend) for friend in arr ]

class User():
    def __init__(self, f):
        self.id = f.get('id')
        self.nsaId = f.get('nsaId')
        self.imageUri = f.get('imageUri')
        self.name = f.get('name')
        self.supportId = f.get('supportId')
        self.isChildRestricted = f.get('isChildRestricted')
        self.etag = f.get('etag')
        self.links = f.get('links')
        self.permissions = f.get('permissions')
        self.presence = Presence(f.get('presence'))

    def description(self):
        return ('%s (id: %s, nsaId: %s):\n' % (self.name, self.id, self.nsaId)
        + '   - Profile Picture: %s\n' % self.imageUri
        + '   - Status: %s\n' % self.presence.description()
        )

class Friend(User):
    def __init__(self, f):
        super().__init__(f)
        self.isFriend = f.get('isFriend')
        self.isFavoriteFriend = f.get('isFavoriteFriend')
        self.isServiceUser = f.get('isServiceUser')
        self.friendCreatedAt = f.get('friendCreatedAt')

    def description(self):
        return ('%s (id: %s, nsaId: %s):\n' % (self.name, self.id, self.nsaId)
        + '   - Profile Picture: %s\n' % self.imageUri
        + '   - Friend Creation Date: %s\n' % self.friendCreatedAt
        + '   - Status: %s\n' % self.presence.description()
        )

class Presence():
    def __init__(self, f):
        self.state = f.get('state')
        self.updatedAt = f.get('updatedAt')
        self.logoutAt = f.get('logoutAt')
        self.game = Game(f.get('game'))

    def description(self):
        return ('%s (updatedAt: %s, logoutAt: %s)\n' % (self.state, self.updatedAt, self.logoutAt)
        + '   - Game: %s' % self.game.description()
        )

class Game():
    def __init__(self, f):
        self.name = f.get('name')
        self.imageUri = f.get('imageUri')
        self.shopUri = f.get('shopUri')
        self.totalPlayTime = f.get('totalPlayTime')
        self.firstPlayedAt = f.get('firstPlayedAt')
        self.sysDescription = f.get('sysDescription')

    def description(self):
        return ('%s (sysDescription: %s)\n' % (self.name, self.sysDescription)
        + '   - Game Icon: %s\n' % self.imageUri
        + '   - Shop Uri: %s\n' % self.shopUri
        + '   - Total Play Time: %s\n' % self.totalPlayTime
        + '   - First Played At: %s' % self.firstPlayedAt
        )

class Session():
    def __init__(self):
        self.headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'OnlineLounge/%s NASDKAPI Android' % nsoAppVersion,
        }
        self.Session = requests.Session()

    def login(self):
        state = base64.urlsafe_b64encode(os.urandom(36))
        verify = base64.urlsafe_b64encode(os.urandom(32))
        authHash = hashlib.sha256()
        authHash.update(verify.replace(b'=', b''))
        authCodeChallenge = base64.urlsafe_b64encode(authHash.digest())

        url = 'https://accounts.nintendo.com/connect/1.0.0/authorize'
        params = {
            'client_id': client_id,
            'redirect_uri': 'npf%s://auth' % client_id,
            'response_type': 'session_token_code',
            'scope': 'openid user user.birthday user.mii user.screenName',
            'session_token_code_challenge': authCodeChallenge.replace(b'=', b''),
            'session_token_code_challenge_method': 'S256',
            'state': state,
            'theme': 'login_form'
        }
        response = self.Session.get(url, headers = self.headers, params = params)

        webbrowser.open(response.history[0].url)
        tokenPattern = re.compile(r'(eyJhbGciOiJIUzI1NiJ9\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)')
        code = tokenPattern.findall(input('After logging in, please copy the link from \'Select this account\' and enter it here:\n'))[0]

        url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'

        return code, verify

    def run(self, code, verify):
        url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'
        headers = self.headers
        headers.update({
            'Accept-Language': 'en-US',
            'Accept':          'application/json',
            'Content-Type':    'application/x-www-form-urlencoded',
            'Content-Length':  '540',
            'Host':            'accounts.nintendo.com',
            'Connection':      'Keep-Alive',
        })
        body = {
            'client_id': client_id,
            'session_token_code': code,
            'session_token_code_verifier': verify.replace(b'=', b''),
        }
        response = self.Session.post(url, data = body, headers = headers)
        return json.loads(response.text)['session_token']
