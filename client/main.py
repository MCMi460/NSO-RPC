# Created by Deltaion Lee (MCMi460) on Github

import sys, os
sys.path.insert(1, '../')
from api import *

if not os.path.isfile('./private.txt'):
    session = Session()
    session_token = session.run(*session.login())
else:
    with open('./private.txt', 'r') as file:
        session_token = json.loads(file.read())['session_token']
api = API(session_token)
