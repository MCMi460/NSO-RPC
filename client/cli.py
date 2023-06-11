# Created by Deltaion Lee (MCMi460) on Github

import sys
import os
import time
import pypresence
import threading
from api import *

applicationPath = getAppPath()


class Discord():
    def __init__(self, session_token = None, user_lang = None, rpc = False, targetID = None, version = None):
        self.rpc = None
        if rpc:
            if not self.connect()[0]:
                sys.exit("Failed to connect to Discord")
        self.running = False
        self.api = None
        self.gui = False
        if session_token and user_lang:
            self.createCTX(session_token, user_lang, targetID, version)

        self.currentGame = None
        self.start = int(time.time())

    def createCTX(self, session_token, user_lang, targetID = None, version = None):
        try:
            if not version:
                version = getVersion()
                if not version:
                    version = input('What is the current version of the Nintendo Switch Online Mobile app? The App Store says it is %s (Please enter like X.X.X)\n> ' % version)
            self.api = API(session_token, user_lang, targetID, version)
        except Exception as e:
            sys.exit(log(e))
        self.running = True

    def connect(self):
        try:
            self.rpc = pypresence.Presence('637692124539650048')
        except Exception as e:
            self.rpc = None
            return (False, e)
        fails = 0
        while True:
            # Attempt to connect to Discord. Will wait until it connects
            try:
                self.rpc.connect()
                print(log("Successfully Connected to Discord."))
                break
            except Exception as e:
                fails += 1
                if fails > 500:
                    print(log('Error, failed after 500 attempts\n\'%s\'' % e))
                    self.rpc = None
                    return (False, e)
                continue
        return (True,)

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
                if not self.api.targetID and not self.gui:
                    if not self.api.friends:
                        self.api.getFriends()
                    self.api.targetID = input('Which user are you?\n-----\n%s\n-----\nPlease enter the ID here: ' % '\n-----\n'.join(['%s (%s)' % (x.name, x.nsaId) for x in client.api.friends]))
                    if not self.api.targetID in (x.nsaId for x in client.api.friends):
                        sys.exit(log('Unknown ID input by user'))
                    with open(os.path.join(applicationPath, 'private.txt'), 'w') as file:
                        file.write(json.dumps({
                            'session_token': self.api.session_token,
                            'user_lang': self.api.user_lang,
                            'targetID': self.api.targetID,
                        }))
                self.api.getSelf()
                break
            except Exception as e:
                log(e)
                if i > 0 or time.time() - self.api.login['time'] < 7170:
                    raise Exception('Cannot get session token properly')
                self.api.updateLogin()
                continue
        self.user = self.api.user

        presence = self.user.presence
        if self.rpc:
            if presence.game.name:  # Please file an issue if this happens to fail
                if self.currentGame != presence.game.name:
                    self.currentGame = presence.game.name
                    self.start = int(time.time())
                state = presence.game.sysDescription
                if not state:
                    state = 'Played for %s hours or more' % (int(presence.game.totalPlayTime / 60 / 5) * 5)
                    if presence.game.totalPlayTime / 60 < 5:
                        state = 'Played for a little while'
                try:
                    self.rpc.update(details = presence.game.name, large_image = presence.game.imageUri, large_text = presence.game.name, state = state, start = self.start, buttons = [{'label': 'Nintendo eShop', 'url': presence.game.shopUri},])
                except pypresence.exceptions.PipeClosed:
                    print(log("Discord pipe is closed, Attempting to reconnect."))
                    self.connect()
            else:
                self.currentGame = None
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
        if os.path.isfile(os.path.join(applicationPath, 'private.txt')):
            try:
                os.remove(os.path.join(applicationPath, 'private.txt'))
            except:
                pass
            try:
                os.remove(os.path.join(applicationPath, 'settings.txt'))
            except:
                pass
            sys.exit()


def getToken(manual = True, path: str = os.path.join(applicationPath, 'private.txt')):
    session_token, user_lang, targetID = None, None, None
    if os.path.isfile(path):
        with open(path, 'r') as file:
            try:
                data = json.loads(file.read())
                session_token = data['session_token']
                user_lang = data['user_lang']
                targetID = data['targetID']
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
    tempToken = os.path.join(applicationPath, 'tempToken.txt')
    if not os.path.isfile(path) and os.path.isfile(tempToken):
        os.remove(tempToken)
    return session_token, user_lang, targetID


if __name__ == '__main__':
    try:
        session_token, user_lang, targetID = getToken()
    except Exception as e:
        sys.exit(log(e))

    try:
        client = Discord(session_token, user_lang, True, targetID)
        client.background()
    except Exception as e:
        log(e)
        raise e
