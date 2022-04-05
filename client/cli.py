# Created by Deltaion Lee (MCMi460) on Github

import sys
import os
import time
import pypresence
from api import *

class Discord():
    def __init__(self, session_token = None, user_lang = None):
        self.rpc = pypresence.Presence('637692124539650048')
        self.connect()
        self.running = False
        if session_token and user_lang:
            self.createCTX(session_token, user_lang)

    def createCTX(self, session_token, user_lang):
        self.api = API(session_token, user_lang)
        self.running = True

    def connect(self):
        fails = 0
        while True:
            # Attempt to connect to Discord. Will wait until it connects
            try:
                self.rpc.connect()
                break
            except Exception as e:
                fails += 1
                if fails > 500:
                    sys.exit('Error, failed after 500 attempts\n\'%s\'' % e)
                continue

    def update(self):
        for i in range(2):
            try:
                self.api.getSelf()
                break
            except:
                if i > 0 or time.time() - self.api.login['time'] < 3600:
                    raise Exception('Cannot get session token properly')
                self.api.updateLogin()
                continue
        self.nickname = self.api.userInfo['nickname']
        self.user = self.api.user

        presence = self.user.presence
        if presence.state == 'ONLINE':
            state = presence.game.sysDescription
            if not state:
                state = 'Played for %s hours or more' % (int(presence.game.totalPlayTime / 60 / 5) * 5)
                if presence.game.totalPlayTime / 60 < 5:
                    state = 'Played for a little while'
            self.rpc.update(details = presence.game.name, large_image = presence.game.imageUri, large_text = presence.game.name, state = state)
        else:
            self.rpc.clear()

    def background(self):
        second = 30
        while True:
            if self.running:
                if second == 30:
                    try:
                        self.update()
                    except KeyError:
                        pass
                    second = 0
                second += 1
            else:
                second = 25
            time.sleep(1)

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
            except:
                os.remove(path)
                sys.exit()
    elif manual:
        session = Session()
        session_token = session.run(*session.login(session.inputManually))
        user_lang = input('Please enter your language from the list below:\n%s\n> ' % ('\n'.join(languages)))
        if not user_lang in languages:
            raise Exception('invalid user language')
    return session_token, user_lang

if __name__ == '__main__':
    session_token, user_lang = getToken()

    client = Discord(session_token, user_lang)
    client.background()
