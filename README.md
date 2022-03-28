# Nintendo Switch Online Rich Presence

*Display your Nintendo Switch game status on Discord!*

This README will be split into two sections:
  - [The quickstart guide](#quick)
  - [In-depth guide](#depth)

This project runs using the Nintendo Switch Online Mobile App API.  
I'd like to thank the [NintendoSwitchRESTAPI](https://github.com/ZekeSnider/NintendoSwitchRESTAPI) developer(s) for very useful blueprint designs.  
And especially, I'd like to thank [frozenpandaman](https://github.com/frozenpandaman) and his [s2s](https://github.com/frozenpandaman/splatnet2statink/wiki/api-docs) API  
Also, [blackgear](https://github.com/blackgear)'s [NSOnline_API](https://github.com/blackgear/NSOnline_API) was integral to my understanding of `session_token` authentication.

<h1 id = 'quick'>Quickstart Guide</h1>

Download the app from the [latest release](https://github.com/MCMi460/NSO-RPC/releases) and run!  
Once ran, the app will ask for you to log into your Nintendo account on a web browser. There is no malicious code with intent to steal your information, but it's best to [review the code][api] for yourself.

1. Open Discord first, then NSO-RPC

2. Log in to your Nintendo account when prompted

3. Right click on 'Select this account' and press 'Copy Link'

![link](/resources/link.png)

4. Paste the link in the pop-up's form and click 'Log In'

5. Control your rich presence from the system tray icon

![display](/resources/display.png)

## FAQ

***Q: Do you need a Nintendo Switch Online subscription to use this app?***  
**A:** No, you do not. This app works whether or not you have access to online services. You will, however, need to link your Nintendo account to your user profile on your Switch.

***Q: My computer says that this app might have a virus! Does it?***  
**A:** No. Your computer is saying that because it's a foreign executable file downloaded from the internet, so you should always be cautious about it. If you'd like, you can [build your own `exe`](#building).

***Q: You're not stealing my account, are you?***  
**A:** Not me, personally. You'll have to ask [frozenpandaman (s2s)](https://github.com/frozenpandaman) and [@NexusMine (flapg)](https://twitter.com/NexusMine). They are responsible for some of the authentication steps. [Read more here](#understanding), and be weary of any possible theft.

***Q: Do I need Discord open on my PC to use this application?***  
**A:** Yes, Discord needs to be open for this application to even run in the first place.

***Q: I can't get the program to run, what's wrong with it?!***  
**A:** Run the [cli.py][cli] program and get the error data, then make an [issue](https://github.com/MCMi460/NSO-RPC/issues) on Github and I'll investigate it.

***Q: I want to switch Nintendo Accounts/I can't link my Nintendo Account. What do I do?***  
**A:** First, try and delete the NSO-RPC folder in your Documents folder. If it still doesn't work, then refer to the question above.

*I am not liable for any sort of rate limiting Nintendo may hammer upon your network*

<h1 id = 'depth'>In-depth guide</h1>

<h2 id = 'building'>Building</h2>

For Windows, run
```bat
cd client
python -m pip install -r requirements.txt pyinstaller
pyinstaller --onefile --clean --noconsole --add-data "icon.png;." --icon=icon.ico app.py
start dist
```
For MacOS, run
```sh
cd client
python3 -m pip install -r requirements.txt py2app
py2applet --make-setup app.py icon.icns "icon.png"
python3 setup.py py2app
open dist
```

<h2 id = 'understanding'>Understanding</h2>

This is going to be a detailed explanation on everything that I do here and exactly what is going on. If you're into that sort of stuff, keep reading. If not, feel free to skim and get a general idea of the procedures.  
I'm going to be explaining my [cli.py][cli] as it isn't as complicated as the [GUI (app.py)](/client/app.py).  
(You can follow along with the guide [here][api] and [here][cli])

<details>
  <summary><h3>1. Getting your <code>session_token</code></h3></summary>

  First things first, we need to get access to your Nintendo account. What we need to get is your `session_token`, which is a unique identifier that confirms to Nintendo servers *you are you*. This is the code that gets your `session_token`.  
  [cli.py][cli]:
  ```python
  path = os.path.expanduser('~/Documents/NSO-RPC/private.txt')
    if not os.path.isfile(path):
        session = Session()
        session_token = session.run(*session.login(session.inputManually))
    else:
        with open(path, 'r') as file:
            session_token = json.loads(file.read())['session_token']
  ```
  First, it checks if you already have a `session_token` saved. If so, then it just uses that.  
  If not, then it will create a `Session()` object and call `Session().login()` (passing `Session().inputManually`) `Session().run()`.  
  That's all fine and dandy, but what does it do behind the `Session().login()` and `Session.run()` functions?  
  Glad you asked.

  - `Session().__init__()`:

    First, it sets some default headers and creates a `requests.Session()` (this is from the common Python library, [requests](https://github.com/psf/requests)).
    ```python
    self.headers = {
      'Accept-Encoding': 'gzip',
      'User-Agent': 'OnlineLounge/%s NASDKAPI Android' % nsoAppVersion,
    }
    self.Session = requests.Session()
    ```

  - `Session().login()`:

    Now, we create some variables (as dictated from [s2s](https://github.com/frozenpandaman/splatnet2statink/blob/master/iksm.py)) for authorization. Basically just a bunch of random characters, but your guess is honestly as good as mine when it comes down to it, as I'm not an expert on oauth authentication.
    ```python
    state = base64.urlsafe_b64encode(os.urandom(36))
    verify = base64.urlsafe_b64encode(os.urandom(32))
    authHash = hashlib.sha256()
    authHash.update(verify.replace(b'=', b''))
    authCodeChallenge = base64.urlsafe_b64encode(authHash.digest())
    ```
    Here, it sets up authentication form, queries it, gets the URL, and opens it in the user's web browser.
    ```python
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
    ```
    Finally, it comes to the user's input. We `re.compile()` the proper format of a return token (thank you, [blackgear](https://github.com/blackgear)). Then, using the input method specified in `Session().login()`, we receive the user's URL and `re.findall()` for the proper code.  
    We'll then return the `code` and `verify` variables.
    ```python
    tokenPattern = re.compile(r'(eyJhbGciOiJIUzI1NiJ9\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)')
    code = tokenPattern.findall(receiveInput())[0]

    return code, verify
    ```

  - `Session().inputManually()`:

    `Session().inputManually()` is literally just a redirect of the Python `input()` function:
    ```python
    def inputManually(self):
      return input('After logging in, please copy the link from \'Select this account\' and enter it here:\n')
    ```

  - `Session().run()`:

    `Session().run()` returns the `session_token` in a finally usable format:
    ```python
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
    ```

</details>

<details>
  <summary><h3>2. Connecting to Discord</h3></summary>

  We create a `Discord()` object and pass the newly obtained `session_token` to it. This does not involve sending your `session_token` to Discord.  
  [cli.py][cli]:
  ```python
  client = Discord(session_token)
  client.background()
  ```

  - `Discord().__init__()`:

    First, it creates a `pypresence.Presence()` object (thanks [pypresence](https://github.com/qwertyquerty/pypresence)!) and passes it my Discord Application ID (this has nothing important other than the name 'Nintendo Switch'; you can replace it with your own ID if you want)  
    Then, it calls `Discord().connect()` to connect to the Discord client.  
    We set the `Discord().running` variable to `False`, then if the parameter `session_token` is passed, it will call `Discord().createCTX()`.
    ```python
    self.rpc = pypresence.Presence('637692124539650048')
    self.connect()
    self.running = False
    if session_token:
      self.createCTX(session_token)
    ```

  - `Discord().createCTX()`:

    This function just creates an `API()` object and sets it to `Discord().api`. It also sets `Discord().running` to `True`.  
    It requires a `session_token` to be passed.
    ```python
    self.api = API(session_token)
    self.running = True
    ```

  - `Discord().connect()`:

    If this errors over 500 times, the application closes.
    ```python
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
    ```

  - `Discord().update()`:

    This updates the user's Discord Rich Presence. Will error if an `API()` object is not defined at `Discord().api`  
    It basically just calls the API to login to your account, grab the user's info, then if they are not currently offline, it will update the `Discord().rpc`.  
    If they are offline, then it will clear their status.  
    If a `Game().sysDescription` is available, it will display that as the Discord state instead of hours played.
    ```python
    def update(self):
      self.api.updateLogin()
      self.nickname = self.api.userInfo['nickname']
      self.user = User(self.api.login.account['result'].get('user'))

      presence = self.user.presence
      if presence.state != 'INACTIVE':
        state = presence.game.sysDescription
        if not state:
          state = 'Played for %s hours or more' % (int(presence.game.totalPlayTime / 60 / 5) * 5)
          if presence.game.totalPlayTime / 60 < 5:
            state = 'Played for a little while'
        self.rpc.update(details = presence.game.name, large_image = presence.game.imageUri, large_text = presence.game.name, state = state)
      else:
        self.rpc.clear()
    ```

  - `Discord().background()`:

    This is the background task that runs the entire application. What we do here is that we update the user's status once every 60 seconds. And, uh, that's pretty much it. If `Discord().running` is not `True` then it will set the next update to be 5 seconds after `Discord().running` becomes `True` again (whenever you toggle the Discord option in the taskbar, this is what happens).
    ```python
    def background(self):
      second = 60
      while True:
        if self.running:
          if second == 60:
            try:
              self.update()
            except KeyError:
              pass
            second = 0
          second += 1
        else:
          second = 55
        time.sleep(1)
    ```

</details>

<details>
  <summary><h3>3. Nintendo's API</h3></summary>

  Oh boy.

  Alright, this gets complicated, but I'll try and cover it all quickly.  
  *For code snippets, see [api/\_\_init\_\_.py][api]

  - `API()`:

    Has three functions: `API().__init__()`, `API().makeRequest()`, and `API().updateLogin()`.  
    `API().makeRequest()` is deprecated now, as only `FriendList()` calls it, and `FriendList()` is unused.

    - `API().__init__()`:

      This sets some headers to `API().headers` and assigns `Nintendo().getServiceToken()` to `API().tokenResponse` after passing `session_token` to it.  
      Of all of the important things it retrieves, we only use `API().tokenResponse['access_token']`. We assign that to the 'Authorization' header.
      ```python
      self.headers['Authorization'] = 'Bearer %s' % self.accessToken # Add authorization token
      ```
      We also create a GUID (`uuid.uuid4()`)  
      We set the default URL that isn't really used, then we set `API().userInfo` to `UsersMe().get()`, which used in `API().updateLogin()`.  
      After that, we store the token in plaintext form in your `Documents/NSO-RPC` folder (WHY??? CHANGE THIS!!)

    - `API().makeRequest()`:

      Deprecated and not in use.
      ```python
      def makeRequest(self, route):
        return requests.post(self.url + route, headers = self.headers)
      ```

    - `API().updateLogin()`:

      All this does is create/refresh your `Login()` - and checks to see if your `s2sHash` is older than 2 minutes.  
      See `Login()` for more information.
      ```python
      if time.time() - self.s2sHash['time'] >= 120:
        self.s2sHash = {
          'hash': None,
          'time': time.time(),
        }
      self.login = Login(self.userInfo, self.accessToken, self.guid, self.s2sHash['hash'])
      self.login.loginToAccount()
      ```

  - `Nintendo()`:

    This just makes an API call to Nintendo for a token. Read more [here](https://github.com/ZekeSnider/NintendoSwitchRESTAPI/blob/master/NintendoAccountBlueprint.md#service-token-connect100apitoken)

    - `Nintendo().__init__()`:

      Set a bunch of headers and the body of our request. Requires `session_token`.

    - `Nintendo().getServiceToken()`:

      Actually make the request, and return it in `JSON`.

  - `UsersMe()`:

    This gets vital information for the `Login()` class. It's one step before actually logging in.

    - `UsersMe().__init__()`:

      Sets headers and host url. Takes `accessToken` (different from `session_token`).

    - `UsersMe().get()`:

      Very original function name, but it just makes the request. It returns necessary information in `JSON` format, including the user's date of birth, country, and language.

  - `Login()`:

    - `Login().__init__()`:

      Takes `userInfo, accessToken, guid, s2sHash`.  
      Sets headers, URL, GUID, user's info, `accessToken`, `Flapg()` API, and the user's account.

      Please take extreme caution and note of this piece of code.
      ```python
      self.flapg = Flapg(self.accessToken, self.timestamp, self.guid, s2sHash).get()
      ```

    - `Login().loginToAccount()`:

      Pretty neat. `/v3` is necessary for the Presence information.
      ```python
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
      ```

  - `Flapg()`:

    [Learn more about this here](https://github.com/frozenpandaman/splatnet2statink/wiki/api-docs#the-flapg-api)  
    This is where it can get risky. We are sending off the user's `accessToken` (a temporary token) to not one, but two third-party APIs. This is what I mentioned in the FAQ about being weary to use this program. It is ran by [@NexusMine on Twitter](https://twitter.com/NexusMine).  
    It is, however, necessary in order to call the `/v3/Account/Login` API, as it retrieves an important factor: The `f` token.  
    Take particular notice of the `s2s()` call.

    - `Flapg().__init__()`:

      Takes `id_token, timestamp, guid, s2sHash`.
      ```python
      if s2sHash:
        hash = s2sHash
      else:
        hash = s2s(id_token, timestamp).getHash()
      self.headers = {
        'x-token': id_token,
        'x-time': str(timestamp),
        'x-guid': guid,
        'x-hash': hash,
        'x-ver': '3',
        'x-iid': 'nso',
      }

      self.url = 'https://flapg.com'
      ```

    - `Flapg().get()`:

      This just connects to the flapg API and returns the result.
      ```python
      def get(self):
        route = '/ika2/api/login?public'

        response = requests.get(self.url + route, headers = self.headers)
        return json.loads(response.text)['result']
      ```

  - `s2s()`:

    [Learn more about this here](https://github.com/frozenpandaman/splatnet2statink/wiki/api-docs)  

    - `s2s().__init__()`:

      Takes `id_token, timestamp`.
      ```python
      self.headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'NSO-RPC/%s' % version,
      }
      self.body = {
        'naIdToken': id_token,
        'timestamp': timestamp,
      }
      self.url = 'https://elifessler.com'
      ```

    - `s2s().getHash()`:

      ```python
      route = '/s2s/api/gen2'
      response = requests.post(self.url + route, headers = self.headers, data = self.body)
      return json.loads(response.text)['hash']
      ```

  - `FriendList()`:

    This is unused and deprecated, but `FriendList().populateList()` queries the user's friends list and stores it as an array of `Friend()` objects.

  - `User()`:

    This creates an easy-to-use object with the user's data sorted and everything! It's purely for ease-of-use for me.

    - `User().__init__()`:

      Assigns variables from the `JSON` value it accepts as `f`.  
      Calls `Presence()`

    - `User().description()`:

      Unused.  
      Returns a Python string with a quick description of the `User()` object.

  - `Friend()`:

    An object used in tandem with `FriendList()`. Imagine a retexture of the `User()` class.

  - `Presence()`:

    Creates a presence state.  
    Calls `Game()`

  - `Game()`:

    Sorts game data into a neat little class.

</details>

<details>
  <summary><h3>4. The <code>f</code> token</h3></summary>

  This hurts me. This is the reason why we have to call third-party APIs in order to 'login' to Nintendo. It essentially just verifies that you are connecting from a real Nintendo Switch Online Mobile app (ineffectively, obviously).  
  Since what's required to generate it is potentially incriminating, we have to generate it using third-party APIs (namely [s2s](https://github.com/frozenpandaman/splatnet2statink/wiki/api-docs) and [flapg](https://github.com/frozenpandaman/splatnet2statink/wiki/api-docs#the-flapg-api)).

</details>

[cli]: /client/cli.py
[api]: /client/api/__init__.py
