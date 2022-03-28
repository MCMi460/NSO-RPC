# NSO-RPC

*Display your Nintendo Switch game status on Discord!*

This README will be split into two sections:
  - [The quickstart guide](#quick)
  - [In-depth guide](#depth)

This project runs off of the Nintendo Switch Online Mobile App API.  
I'd like to thank the [NintendoSwitchRESTAPI](https://github.com/ZekeSnider/NintendoSwitchRESTAPI) developer(s) for very useful blueprint designs.  
And especially, I'd like to thank [frozenpandaman](https://github.com/frozenpandaman) and his [s2s](https://github.com/frozenpandaman/splatnet2statink/wiki/api-docs) API  
Also, [blackgear](https://github.com/blackgear)'s [NSOnline_API](https://github.com/blackgear/NSOnline_API) was integral to my understanding of `session_token` authentication.

<h1 id = 'quick'>Quickstart Guide</h1>

Download the app from the [latest release](https://github.com/MCMi460/NSO-RPC/releases) and run!  
Once ran, the app will ask for you to log into your Nintendo account on a web browser. There is no malicious code with intent to steal your information, but it's best to [review the code](/api/__init__.py) for yourself.

1. Open Discord first, then NSO-RPC

2. Log in to your Nintendo account when prompted

3. Right click on 'Select this account' and press 'Copy Link'

4. Paste the link in the pop-up's form and click 'Log In'

5. Control your rich presence from the system tray icon

## FAQ

***Q: Do you need a Nintendo Switch Online subscription to use this app?***  
**A:** No, you do not. This app works whether or not you have access to online services. You will, however, need to link your Nintendo account to your user profile on your Switch.

***Q: My computer says that this app might have a virus! Does it?***  
**A:** No. Your computer is saying that because it's a foreign executable file downloaded from the internet, so you should always be cautious about it. If you'd like, you can [build your own `exe`](#building).

***Q: You're not stealing my account, are you?***  
**A:** Not me, personally. You'll have to ask [frozenpandaman (s2s)](https://github.com/frozenpandaman) and [@NexusMine (flapg)](https://twitter.com/NexusMine).

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

## Understanding
