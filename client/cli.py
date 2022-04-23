# Created by Deltaion Lee (MCMi460) on Github

import sys
import os
import time
import pypresence
import threading
from api import *

class Discord():
    def __init__(self, session_token = None, user_lang = None, rpc = False):
        self.rpc = None
        if rpc:
            if not self.connect():
                sys.exit()
        self.running = False
        self.api = None
        self.gui = False
        if session_token and user_lang:
            self.createCTX(session_token, user_lang)

    def createCTX(self, session_token, user_lang):
        try:
            self.api = API(session_token, user_lang)
        except Exception as e:
            sys.exit(log(e))
        self.running = True

    def connect(self):
        try:
            self.rpc = pypresence.Presence('637692124539650048')
        except:
            self.rpc = None
            return False
        fails = 0
        while True:
            # Attempt to connect to Discord. Will wait until it connects
            try:
                self.rpc.connect()
                break
            except Exception as e:
                fails += 1
                if fails > 500:
                    print(log('Error, failed after 500 attempts\n\'%s\'' % e))
                    self.rpc = None
                    return False
                continue
        return True

    def disconnect(self):
        if self.rpc:
            self.rpc.close()
        self.rpc = None

    def setApp(self, function):
        self.app = function
        self.gui = True

    def update(self):
        for i in range(2):
            try:
                self.api.getSelf()
                break
            except Exception as e:
                log(e)
                if i > 0 or time.time() - self.api.login['time'] < 7170:
                    raise Exception('Cannot get session token properly')
                self.api.updateLogin()
                continue
        self.nickname = self.api.userInfo['nickname']
        self.user = self.api.user

        presence = self.user.presence
        if self.rpc:
            if presence.game.name: # Please file an issue if this happens to fail
                state = presence.game.sysDescription
                if not state:
                    state = 'Played for %s hours or more' % (int(presence.game.totalPlayTime / 60 / 5) * 5)
                    if presence.game.totalPlayTime / 60 < 5:
                        state = 'Played for a little while'
                self.rpc.update(details = presence.game.name, large_image = presence.game.imageUri, large_text = presence.game.name, state = state)
            else:
                self.rpc.clear()
        # Set GUI
        if self.gui:
            self.app(self.user)

    def background(self):
        second = 30
        while True:
            if self.running:
                if second == 30:
                    try:
                        self.update()
                    except Exception as e:
                        sys.exit(log(e))
                    second = 0
                second += 1
            else:
                second = 25
            time.sleep(1)

    def logout(self):
        path = os.path.expanduser('~/Documents/NSO-RPC')
        if os.path.isfile(os.path.join(path, 'private.txt')):
            try:os.remove(os.path.join(path, 'private.txt'))
            except:pass
            try:os.remove(os.path.join(path, 'settings.txt'))
            except:pass
            sys.exit()

def getToken(manual = True, path:str = os.path.expanduser('~/Documents/NSO-RPC/private.txt')):
    session_token, user_lang = None, None
    if os.path.isfile(path):
        with open(path, 'r') as file:
            try:
                data = json.loads(file.read())
                session_token = data['session_token']
                user_lang = data['user_lang']
                if not user_lang in languages:
                    raise Exception('invalid user language')
            except Exception as e:
                os.remove(path)
                sys.exit(log(e))
    elif manual:
        session = Session()
        session_token = session.run(*session.login(session.inputManually))
        user_lang = input('Please enter your language from the list below:\n%s\n> ' % ('\n'.join(languages)))
        if not user_lang in languages:
            raise Exception('invalid user language')
    tempToken = os.path.expanduser('~/Documents/NSO-RPC/tempToken.txt')
    if not os.path.isfile(path) and os.path.isfile(tempToken):
        os.remove(tempToken)
    return session_token, user_lang

if __name__ == '__main__':
    try:
        session_token, user_lang = getToken()
    except Exception as e:
        sys.exit(log(e))

    client = Discord(session_token, user_lang, True)
    client.background()
