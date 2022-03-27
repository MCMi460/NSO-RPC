# Created by Deltaion Lee (MCMi460) on Github

import sys
import os
import time
import pypresence
sys.path.insert(1, '../')
from api import *

class Discord():
    def __init__(self):
        self.rpc = pypresence.Presence('637692124539650048')
        self.connect()
        self.update()

    def connect(self):
        fails = 0
        while True:
            # Attempt to connect to Discord. Will wait until it connects
            try:
                self.rpc.connect()
                break
            except Exception as e:
                time.sleep(0.1)
                fails += 1
                if fails > 500:
                    sys.exit('Error, failed after 500 attempts\n\'%s\'' % e)
                continue

    def update(self):
        self.api = API(session_token)
        self.nickname = self.api.userInfo['nickname']
        self.user = User(self.api.login.account['result'].get('user'))

        presence = self.user.presence
        if presence.state != 'INACTIVE':
            self.rpc.update(details = presence.game.name, large_image = presence.game.imageUri)
        else:
            self.rpc.clear()

    def background(self):
        while True:
            time.sleep(60)
            self.update()

if not os.path.isfile('./private.txt'):
    session = Session()
    session_token = session.run(*session.login())
else:
    with open('./private.txt', 'r') as file:
        session_token = json.loads(file.read())['session_token']

if __name__ == '__main__':
    client = Discord()
    client.background()
