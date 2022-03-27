# Created by Deltaion Lee (MCMi460) on Github

import sys
import os
import time
import pypresence
sys.path.insert(1, '../')
from api import *

class Discord():
    def __init__(self, session_token = None):
        self.rpc = pypresence.Presence('637692124539650048')
        self.connect()
        self.running = False
        if session_token:
            self.createCTX(session_token)

    def createCTX(self, session_token):
        self.api = API(session_token)
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
        self.api.updateLogin()
        self.nickname = self.api.userInfo['nickname']
        self.user = User(self.api.login.account['result'].get('user'))

        presence = self.user.presence
        if presence.state != 'INACTIVE':
            self.rpc.update(details = presence.game.name, large_image = presence.game.imageUri, large_text = presence.game.name, state = 'Played for %s hours or more' % (int(presence.game.totalPlayTime / 60 / 5) * 5))
        else:
            self.rpc.clear()

    def background(self):
        second = 60
        while True:
            if self.running:
                if second == 60:
                    self.update()
                    second = 0
                second += 1
            else:
                second = 55
            time.sleep(1)

if __name__ == '__main__':
    path = os.path.expanduser('~/Documents/NSO-RPC/private.txt')
    if not os.path.isfile(path):
        session = Session()
        session_token = session.run(*session.login(session.inputManually))
    else:
        with open(path, 'r') as file:
            session_token = json.loads(file.read())['session_token']

    client = Discord(session_token)
    client.background()
