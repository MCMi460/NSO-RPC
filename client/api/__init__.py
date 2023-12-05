# Created by Deltaion Lee (MCMi460) on Github

import requests
import json
import uuid
import time
import sys
import webbrowser
import base64
import os
import platform
import hashlib
import re
import pickle


def getAppPath():
    # Check for macOS platform and NSO-RPC freeze status
    if sys.platform.startswith('darwin') and hasattr(sys, 'frozen') and sys.frozen == 'macosx_app':
        app_root_folder = os.path.dirname(re.search(r'(.*/NSO-RPC\.app)/', os.path.abspath(__file__)).group(1))

        # Check if NSO-RPC_Data exists
        potential_data_path = os.path.join(app_root_folder, 'NSO-RPC_Data')
        if os.path.isdir(potential_data_path):
            return potential_data_path
        else:
            return os.path.expanduser('~/Documents/NSO-RPC')

    # Windows allows you to move your UserProfile subfolders, Such as Documents, Videos, Music etc.
    # However os.path.expanduser does not actually check and assumes its in the default location.
    # This tries to correctly resolve the Documents path and fallbacks to default if it fails.
    application_path = os.path.expanduser('~/Documents/NSO-RPC')
    if platform.system() == 'Windows':
        try:
            import ctypes.wintypes
            CSIDL_PERSONAL = 5  # My Documents
            SHGFP_TYPE_CURRENT = 0  # Get current, not default value
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
            application_path = os.path.join(buf.value, 'NSO-RPC')
        except:
            pass

    # Use Portable path if it exists, else use Default path
    portable_data_path = os.path.join(os.getcwd(), 'NSO-RPC_Data')
    return portable_data_path if os.path.isdir(portable_data_path) else application_path


def Restart_NSORPC():
    args = [sys.executable] + sys.argv
    os.execl(sys.executable, *args)


def log(info, time = time.time()):
    path = getAppPath()
    if not os.path.isdir(path):
        os.mkdir(path)
    with open(os.path.join(path, 'logs.txt'), 'a') as file:
        file.write('%s: %s\n' % (time, info))
    return info


def getVersion():
    for i in range(5):
        try:
            r = requests.get('https://apps.apple.com/us/app/nintendo-switch-online/id1234806557', timeout = 10)
            break
        except requests.RequestException as e:
            log(f'Failed to get Apple\'s store page. Retrying... Error: {str(e)}')
    else:
        log('Failed to get Apple\'s store page after multiple retries.')
    if r:
        searchPattern = re.compile(r'Version\s*(\d\.\d\.\d)+')
        version = searchPattern.search(r.text)
        if version:
            return version.group(1)
    return ''


client_id = '71b963c1b7b6d119'
version = 0.3
nsoAppVersion = None
languages = [  # ISO Language codes
    'en-US',
    'es-MX',
    'fr-CA',
    'ja-JP',
    'en-GB',
    'es-ES',
    'fr-FR',
    'de-DE',
    'it-IT',
    'nl-NL',
    'ru-RU'
]


class API():
    def __init__(self, session_token, user_lang, targetID, version):
        pattern = re.compile(r'(\d.\d.\d)')
        if not version or not re.search(pattern, version):
            raise Exception('missing app version')
        global nsoAppVersion
        nsoAppVersion = version
        self.headers = {
            'X-ProductVersion': nsoAppVersion,
            'X-Platform': 'iOS',
            'User-Agent': 'Coral/%s (com.nintendo.znca; build:1999; iOS 15.5.0) Alamofire/5.4.4' % nsoAppVersion,
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Host': 'api-lp1.znc.srv.nintendo.net',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }

        self.user_lang = user_lang
        self.session_token = session_token
        self.targetID = targetID
        self.refreshAccessToken()
        self.guid = str(uuid.uuid4())

        self.url = 'https://api-lp1.znc.srv.nintendo.net'

        self.userInfo = UsersMe(self.accessToken, self.user_lang).get()
        self.login = {
            'login': None,
            'time': 0,
        }

        self.friends = []

        path = getAppPath()
        if not os.path.isdir(path):
            os.mkdir(path)
        with open(os.path.join(path, 'private.txt'), 'w') as file:
            file.write(json.dumps({
                'session_token': self.session_token,
                'user_lang': self.user_lang,
                'targetID': self.targetID,
            }))

    def makeRequest(self, route):
        return requests.post(self.url + route, headers = self.headers)

    def refreshAccessToken(self):
        self.tokenResponse = Nintendo(self.session_token, self.user_lang).getServiceToken()
        self.id_token = self.tokenResponse['id_token']
        self.accessToken = self.tokenResponse['access_token']
        self.refreshLast = time.time()
        return self.accessToken

    def updateLogin(self):
        path = os.path.join(getAppPath(), 'tempToken.txt')
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                self.login = pickle.loads(file.read())
                try:
                    self.headers['Authorization'] = 'Bearer %s' % self.login['login'].account['result'].get('webApiServerCredential').get('accessToken')
                except Exception as e:
                    log('Failure with authorization: %s\nLogin returns %s' % (e, self.login['login'].account))
                    raise e
                log('Login from file')
        if time.time() - self.login['time'] < 7170:
            return
        if time.time() - self.refreshLast > 120:
            self.refreshAccessToken()
        login = Login(self.userInfo, self.user_lang, self.accessToken, self.guid)
        login.loginToAccount()
        try:
            self.headers['Authorization'] = 'Bearer %s' % login.account['result'].get('webApiServerCredential').get('accessToken')  # Add authorization token
        except Exception as e:
            raise Exception('Failure with authorization: %s\nLogin returns %s' % (e, login.account))
        self.login = {
            'login': login,
            'time': time.time(),
        }
        with open(path, 'wb') as file:
            file.write(pickle.dumps(self.login))

    def getSelf(self):
        self.getFriends()

        if not self.targetID:
            route = '/v3/User/ShowSelf'

            response = self.makeRequest(route)
            self.user = User(json.loads(response.text)['result'])
        else:
            response = next(x for x in self.friends if x.nsaId == self.targetID)
            self.user = response

    def getFriends(self):
        list = FriendList()
        list.populateList(self)
        self.friends = list.friendList


class Nintendo():
    def __init__(self, sessionToken, userLang):
        self.headers = {
            'User-Agent': 'Coral/%s (com.nintendo.znca; build:1999; iOS 15.5.0) Alamofire/5.4.4' % nsoAppVersion,
            'Accept': 'application/json',
            'Accept-Language': userLang,
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
    def __init__(self, accessToken, userLang):
        self.headers = {
            'User-Agent': 'Coral/%s (com.nintendo.znca; build:1999; iOS 15.5.0) Alamofire/5.4.4' % nsoAppVersion,
            'Accept': 'application/json',
            'Accept-Language': userLang,
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


class imink():
    def __init__(self, na_id, id_token, timestamp, guid, iteration):
        self.headers = {
            'User-Agent': 'NSO-RPC/%s' % version,
            'Content-Type': 'application/json; charset=utf-8',
        }
        self.body = {
            'token': id_token,
            'hash_method': str(iteration),
            'na_id': na_id,
        }

        self.url = 'https://api.imink.app'

    def get(self):
        log('Login from imink')
        route = '/f'

        response = requests.post(self.url + route, headers = self.headers, data = json.dumps(self.body))
        return json.loads(response.text)


class Login():
    def __init__(self, userInfo, userLang, accessToken, guid):
        self.headers = {
            'Host': 'api-lp1.znc.srv.nintendo.net',
            'Accept-Language': userLang,
            'User-Agent': 'com.nintendo.znca/' + nsoAppVersion + ' (Android/7.1.2)',
            'Accept': 'application/json',
            'X-ProductVersion': nsoAppVersion,
            'Content-Type': 'application/json; charset=utf-8',
            'Connection': 'Keep-Alive',
            'Authorization': 'Bearer',
            'X-Platform': 'Android',
            'Accept-Encoding': 'gzip'
        }

        self.url = 'https://api-lp1.znc.srv.nintendo.net'
        self.timestamp = int(time.time()) * 1000  # Convert from iOS to Android
        self.guid = guid

        self.userInfo = userInfo
        self.accessToken = accessToken
        self.na_id = userInfo['id']

        self.imink = imink(self.na_id, self.accessToken, self.timestamp, self.guid, 1).get()
        self.timestamp = int(self.imink['timestamp'])
        self.guid = self.imink['request_id']

        self.account = None

    def loginToAccount(self):
        route = '/v3/Account/Login'
        body = {
            'parameter': {
                'f': self.imink['f'],
                'naIdToken': self.accessToken,
                'timestamp': self.timestamp,
                'requestId': self.guid,
                'naCountry': self.userInfo['country'],
                'naBirthday': self.userInfo['birthday'],
                'language': self.userInfo['language'],
            },
        }
        response = requests.post(self.url + route, headers = self.headers, json = body)
        self.account = json.loads(response.text)
        return self.account


class User():
    def __init__(self, f):
        self.id = f.get('id')
        self.nsaId = f.get('nsaId')
        self.imageUri = f.get('imageUri')
        self.image = None
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
                + '   - Is Favorite: %s\n' % self.isFavoriteFriend
                + '   - Friend Creation Date: %s\n' % self.friendCreatedAt
                + '   - Status: %s\n' % self.presence.description()
                )


class FriendList():
    def __init__(self):
        self.route = '/v3/Friend/List'  # Define API route

        self.friendList = []  # List of Friend object(s)

    def populateList(self, API: API):
        response = API.makeRequest(self.route)
        try:
            arr = json.loads(response.text)['result']['friends']
        except Exception as e:
            log('Failure with authorization: %s\Friends returns %s' % (e, response.text))
            raise e
        self.friendList = [Friend(friend) for friend in arr]


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

    def login(self, receiveInput, *, altLink = None):
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

        try:
            webbrowser.open(response.history[0].url)
        except Exception as e:
            print(log(e))
        print('Open this link: %s' % response.history[0].url)
        if altLink:
            altLink('<a href="%s" style="color: cyan;">Click here if your browser didn\'t open</a>' % response.history[0].url)
        tokenPattern = re.compile(r'(eyJhbGciOiJIUzI1NiJ9\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)')
        code = tokenPattern.findall(receiveInput())[0]

        return code, verify

    def inputManually(self):
        return input('After logging in, please copy the link from \'Select this account\' and enter it here:\n')

    def run(self, code, verify):
        url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'
        headers = self.headers
        headers.update({
            'Accept-Language': 'en-US',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '540',
            'Host': 'accounts.nintendo.com',
            'Connection': 'Keep-Alive',
        })
        body = {
            'client_id': client_id,
            'session_token_code': code,
            'session_token_code_verifier': verify.replace(b'=', b''),
        }
        response = self.Session.post(url, data = body, headers = headers)
        return json.loads(response.text)['session_token']
