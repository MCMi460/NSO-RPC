# Created by Deltaion Lee (MCMi460) on Github

import flask, secrets, time, multiprocessing, gevent.pywsgi, random, sys
sys.path.insert(1, '../')
from api import FriendList

app = flask.Flask(__name__)

local = True

host = '127.0.0.1'
port = 2727

list = FriendList() # Create FriendList object
sys.exit()
list.populateList() # Query server and populate array

def loop():
    global list
    while True:
        time.sleep(1)
        if round(time.time()) % 600 == 0: # Check if epoch is 10 minutes from set
            list.populateList()
            continue

@app.route('/', methods = ['GET',])
def index():
    nsaId = flask.request.args.get('nsaId')
    if nsaId:
        print(str([ friend.description() for friend in list.friendList ]))
        return str([ friend.description() for friend in list.friendList if friend.nsaId == int(nsaId) ]) # Iterate through array and print Friend object description
    return 'None'

if __name__ == '__main__':
    multiprocessing.Process(target = loop, args = ()).start()
    if local:
        app.run(host, port = port, debug = local, use_reloader = False)
    else:
        server = gevent.pywsgi.WSGIServer((host, port), app)
        server.serve_forever()
