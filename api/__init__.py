# Created by Deltaion Lee (MCMi460) on Github

import requests
import json
import uuid
import time
import sys
from .private import *

class s2s():
    def __init__(self, id_token, timestamp):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'user_agent/version.num',
        }
        self.body = {
            'naIdToken': id_token,
            'timestamp': timestamp,
        }
        self.url = 'https://elifessler.com'

    def getHash(self):
        print(self.body)
        route = '/s2s/api/gen2'
        response = requests.post(self.url + route, headers = self.headers, json = self.body)
        print(response.content)
        sys.exit()
        return response.content

class Flapg():
    def __init__(self, id_token, timestamp):
        self.headers = {
            'x-token': id_token,
            'x-time': timestamp,
            'x-guid': uuid.uuid4(),
            'x-hash': s2s(id_token, timestamp).getHash(),
            'x-ver': 3,
            'x-iid': 'app',
        }

        self.url = 'https://flapg.com'

    def getF(self):
        route = '/ika2/api/login?public'

        response = requests.get(self.url + route)
        print(response.content)
        sys.exit()
        return response.content

class Nintendo():
    def __init__(self):
        self.headers = {
            'X-ProductVersion': '2.0.0',
            'X-Platform': 'iOS',
            'User-Agent': 'Coral/2.0.0 (com.nintendo.znca; build:1489; iOS 15.3.1) Alamofire/5.4.4',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'accounts.nintendo.com',
        }
        self.body = {
            'client_id': client_id,
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token',
            'session_token': session_token,
        }

        self.url = 'https://accounts.nintendo.com'

    def getServiceToken(self):
        route = '/connect/1.0.0/api/token'
        response = requests.post(self.url + route, headers = self.headers, json = self.body)
        return json.loads(response.content.decode('utf-8'))['id_token']

class Login():
    def __init__(self):
        self.headers = {
            'X-ProductVersion': '2.0.0',
            'X-Platform': 'iOS',
            'User-Agent': 'Coral/2.0.0 (com.nintendo.znca; build:1489; iOS 15.3.1) Alamofire/5.4.4',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'api-lp1.znc.srv.nintendo.net',
        }

        self.url = 'https://api-lp1.znc.srv.nintendo.net'
        self.timestamp = round(time.time())

        self.Nintendo = Nintendo()
        self.id_token = self.Nintendo.getServiceToken()

        self.flapg = Flapg(self.id_token, self.timestamp)
        self.f = self.flapg.getF()

    def loginToAccount(self):
        route = '/v1/Account/Login'
        body = {
        'language': 'en-US',
        'naBirthday': naBirthday,
        'naCountry': 'US',
        'naIdToken': '%s' % self.id_token,
        'requestId': '%s' % uuid.uuid4(),
        'timestamp': self.timestamp,
        'f': self.f,
        }
        response = requests.post(self.url + route, headers = self.headers, json = self.body)
        print(body)
        print(response.content)
        return response.content.decode('utf-8')

class API():
    def __init__(self):
        self.login = Login()

        self.headers = {
            'X-ProductVersion': '2.0.0',
            'X-Platform': 'iOS',
            'User-Agent': 'Coral/2.0.0 (com.nintendo.znca; build:1489; iOS 15.3.1) Alamofire/5.4.4',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'api-lp1.znc.srv.nintendo.net',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        self.url = 'https://api-lp1.znc.srv.nintendo.net'
        self.headers['Authorization'] = 'Bearer %s' % json.loads(self.login.loginToAccount())['accessToken'] # Add authorization token
        print(self.headers['Authorization'])

    def makeRequest(self, route):
        return requests.post(self.url + route, headers = self.headers)

class FriendList(API):
    def __init__(self):
        super().__init__()

        self.route = '/v3/Friend/List' # Define API route

        self.friendList = [] # List of Friend object(s)

    def populateList(self):
        response = self.makeRequest(self.route)
        arr = json.loads(response.content.decode('utf-8'))['result']['friends']
        self.friendList = [ Friend(friend) for friend in arr ]

class Friend():
    def __init__(self, f):
        self.id = f.get('id')
        self.nsaId = f.get('nsaId')
        self.imageUri = f.get('imageUri')
        self.name = f.get('name')
        self.isFriend = f.get('isFriend')
        self.isFavoriteFriend = f.get('isFavoriteFriend')
        self.isServiceUser = f.get('isServiceUser')
        self.friendCreatedAt = f.get('friendCreatedAt')
        self.presence = Presence(f.get('presence'))

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
