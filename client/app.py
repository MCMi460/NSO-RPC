# Created by Deltaion Lee (MCMi460) on Github

from qtpy.QtCore import *
from qtpy.QtWidgets import *
from qtpy.QtGui import *
from layout import Ui_MainWindow

import sys
import threading
import requests
import time
from qtwidgets import Toggle, AnimatedToggle
from cli import *

# PyQt5 Initialization
app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)
app.setApplicationName("NSO-RPC")
MainWindow = QMainWindow()
# NSO Variables
session_token, user_lang, targetID = getToken(False)
version = getVersion()
while not version:
    version, ok = QInputDialog.getText(MainWindow, 'Version Number', 'What is the current version of the Nintendo Switch Online Mobile app?\nThe App Store says it is %s (Please enter like X.X.X)\nEnter nothing and press Okay to be sent to the app store\'s website.' % version)
    if not ok:
        quit()
    if ok and not version:
        webbrowser.open('https://apps.apple.com/us/app/nintendo-switch-online/id1234806557')
try:
    client = Discord(session_token, user_lang, False, targetID, version)
except Exception as e:
    log(e)
    raise e

# Helpful Wrapper code for handling autostart dependencies
if getattr(sys, 'frozen', False):
    isScriptBundled = True
else:
    isScriptBundled = False
if not isScriptBundled:
    if platform.system() == 'Windows':
        try:
            import win32com.client
            import winshell
        except:
            print('Trying to Install required modules: "pypiwin32" and "winshell"\n')
            os.system(" ".join([sys.executable, "-m pip install pypiwin32 winshell"]))
        from win32com.client import Dispatch
        from winshell import Shortcut

# PyQt5 Variables
style = """
QWidget {
  background-color: #F2F2F2;
}
QGroupBox {
  background-color: #fff;
  border: 1px solid #dfdfdf;
  border-radius: 8px;
}
QLineEdit {
  color: #888c94;
  background-color: #F2F2F2;
}
QLabel {
  background-color: #F2F2F2;
  color: #3c3c3c;
  text-align: center;
}
QComboBox {
  background-color: #F2F2F2;
  color: #3c3c3c;
  border: 1px solid #dfdfdf;
  text-align: center;
}
QPushButton {
  color: #ffffff;
  background-color: #e60012;
  border-radius: 10px;
  text-align: center;
}
QPushButton:disabled {
  background-color: #706465;
}
QMenu::item {
  color: #393939;
}
QScrollBar:vertical {
    border: 0px;
    background-color: transparent;
}
QScrollBar::handle:vertical {
    background-color: #393939;
    border-radius: 4px;
}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
    background: none;
    border: none;
}
QScrollBar::add-line, QScrollBar::sub-line {
    background: none;
    border: none;
}
"""
darkMode = style.replace('#F2F2F2', '#2b2828').replace('#dfdfdf', '#383333').replace('#ffffff', '#e6e6e6').replace('#fff', '#1e2024').replace('#393939', '#c4bebe').replace('#3c3c3c', '#fff')
# self.mode = 1 is for token
# self.mode = 2 is for full


def getPath(path):
    try:
        root = sys._MEIPASS
    except Exception:
        root = os.path.abspath('.')

    return os.path.join(root, path)


def loadPix(url):
    _pixmap = QPixmap()
    _pixmap.loadFromData(requests.get(url).content)
    return _pixmap


def up(_label, image):
    _label.clear()
    if isinstance(image, str):
        image = loadPix(image)
    _label.setPixmap(image)


def timeSince(epoch: int):
    if epoch == 0:
        return ''
    offset = time.time() - epoch
    array = {
        'minute': 60,
        'hour': 60,
        'day': 24,
        'year': 365,
        'decade': 10,
    }
    unit = 'second'
    for i in array:
        if offset >= array[i]:
            offset = offset / array[i]
            unit = i
        else:
            break
    return 'Last online %s %s%s ago' % (int(offset), unit, ('' if int(offset) == 1 else 's'))


applicationPath = getAppPath()
settingsFile = os.path.join(applicationPath, 'settings.txt')
settings = {
    'dark': False,
    'startInSystemTray': False,
    'startOnLaunch': False,
}
userSelected = ''


def writeSettings():
    try:
        os.mkdir(os.path.dirname(settingsFile))
    except:
        pass
    with open(settingsFile, 'w') as file:
        file.write(json.dumps(settings))


def readSettings():
    global settings
    with open(settingsFile, 'r') as file:
        settings = json.loads(file.read())


friendTime = time.time()
iconsStorage = {}


class GUI(Ui_MainWindow):
    def __init__(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setFixedSize(600, 600)

    def setMode(self, mode):
        global settings
        settings['dark'] = mode
        writeSettings()
        if settings['dark']:
            self.MainWindow.setStyleSheet(darkMode)
        else:
            self.MainWindow.setStyleSheet(style)
        self.assignVariables()
        if self.mode == 2:
            self.updateFriends()

    def setVisibility(self, mode):
        global settings
        settings['startInSystemTray'] = mode
        writeSettings()

    def setLaunchMode(self, mode):
        global settings
        try:
            if platform.system() == 'Windows':
                from win32com.client import Dispatch
                from winshell import Shortcut
                StartupFolder = os.path.join(os.getenv('APPDATA'), "Microsoft\Windows\Start Menu\Programs\Startup")
                shell = Dispatch("WScript.Shell")
                Shortcut = shell.CreateShortCut(os.path.join(StartupFolder, "NSO-RPC.lnk"))
                Shortcut.Targetpath = sys.executable
                Shortcut.WorkingDirectory = os.getcwd()
                Shortcut.IconLocation = sys.executable
                if not isScriptBundled:
                    runningPath = os.getcwd()
                    Shortcut.IconLocation = os.path.join(runningPath, "client\icon.ico")
                    Shortcut.Arguments = os.path.abspath(__file__)
                if settings['startOnLaunch'] == False:
                    Shortcut.save()
                elif settings['startOnLaunch'] == True:
                    os.remove(os.path.join(StartupFolder, "NSO-RPC.lnk"))

            elif platform.system() == "Linux":  # This is where Linux code should go
                linuxServiceFile = [
                    "[Unit]",
                    "Description=NSO-RPC Autostart",
                    "PartOf=graphical-session.target",
                    "",
                    "[Service]",
                    "Type=simple",
                    "StandardOutput=journal",
                    "WorkingDirectory=" + os.getcwd(),
                    "ExecStart=" + " ".join([sys.executable, os.path.abspath(__file__)]),
                    "",
                    "[Install]",
                    "WantedBy=graphical-session.target"
                ]
                linuxServicePath = os.path.expanduser('~/.local/share/systemd/user')
                if not os.path.exists(linuxServicePath):
                    os.makedirs(linuxServicePath)
                if settings['startOnLaunch'] == False:
                    with open(os.path.join(linuxServicePath, "NSO-RPC.service"), 'w') as out:
                        out.writelines(line + "\n" for line in linuxServiceFile)
                        out.close()
                    os.system('systemctl --user daemon-reload && systemctl --user enable NSO-RPC.service')
                else:
                    os.system('systemctl --user disable NSO-RPC.service')
                    os.remove(os.path.join(linuxServicePath, "NSO-RPC.service"))
                    os.system('systemctl --user daemon-reload')
            elif platform.system() == "Darwin":
                applicationPath = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), "MacOS/NSO-RPC")

                # Rebuild the path if we're running inside Downloads (This assumes that only Downloads can have /private/var/folders)
                if applicationPath.startswith("/private"):
                    applicationPathTmp = applicationPath.split("/")
                    applicationPathTmp = applicationPathTmp[len(applicationPathTmp) - 4:len(applicationPathTmp)]
                    applicationPath = os.path.join(os.path.expanduser('~/Downloads'), "/".join(applicationPathTmp))

                macOSplist = [
                    '<?xml version="1.0" encoding="UTF-8"?>',
                    '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
                    '<plist version="1.0">',
                    '	<dict>',
                    '		<key>Label</key>',
                    '		<string>NSO-RPC.app</string>',
                    '		<key>Program</key>',
                    '		<string>' + applicationPath + '</string>',
                    '		<key>RunAtLoad</key>',
                    '		<true/>',
                    '	</dict>',
                    '</plist>'
                ]
                macOSLaunchAgentPath = os.path.expanduser('~/Library/LaunchAgents')
                if not os.path.exists(macOSLaunchAgentPath):
                    os.makedirs(macOSLaunchAgentPath)
                if settings['startOnLaunch'] == False:
                    with open(os.path.join(macOSLaunchAgentPath, "NSO-RPC.plist"), 'w') as out:
                        out.writelines(line + "\n" for line in macOSplist)
                        out.close()
                else:
                    os.system('rm ' + os.path.join(macOSLaunchAgentPath, "NSO-RPC.plist"))
            else:
                raise Exception('not implemented yet')
            settings['startOnLaunch'] = mode
        except:
            settings['startOnLaunch'] = False
            self.startOnLaunch.setChecked(settings.get('startOnLaunch', False))
        writeSettings()

    def selfService(self):
        self.mode = 1
        self.setMode(settings['dark'])

        self.MainWindow.closeEvent = self.closeEvent

        self.stackedWidget.setCurrentIndex(0)
        if not session_token:
            self.session = Session()
            threading.Thread(target = self.grabToken, daemon = True).start()
        else:
            self.changeState()

    def assignVariables(self):
        self.button = self.groupBox.findChild(QPushButton, 'pushButton')
        self.button.clicked.connect(self.changeState)

        self.lineEdit = self.groupBox.findChild(QLineEdit, 'lineEdit')

        self.comboBox = self.groupBox.findChild(QComboBox, 'comboBox')
        self.comboBox.clear()
        self.comboBox.addItems(languages)

        # Home
        self.selfImage = self.stackedWidget.findChild(QLabel, 'label_3')
        self.selfImage.setScaledContents(True)
        self.selfImage.setCursor(QCursor(Qt.PointingHandCursor))
        self.selfImage.mousePressEvent = self.openPfp

        self.pushButton_7.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_8.setCursor(QCursor(Qt.PointingHandCursor))
        self.pushButton_7.clicked.connect(lambda *args: self.updateProfile(True))
        self.pushButton_8.clicked.connect(lambda *args: self.updateProfile(False))

        self.namePlate = self.stackedWidget.findChild(QLabel, 'label_4')
        self.namePlate.setAlignment(Qt.AlignCenter)
        self.namePlate.setStyleSheet('color:#fff;')

        self.groupBox_2.setStyleSheet('background-color: #e60012; border-radius: 0px;')

        self.groupBox_2.findChild(QLabel, 'label_5').setStyleSheet('font-weight: bold; color: #fff;')
        self.nSwitchIcon = self.groupBox_2.findChild(QLabel, 'label_6')
        self.nSwitchIcon.setScaledContents(True)

        self.groupBox_6.setStyleSheet('background-color: #%s; border: 0px; border-radius: 0px;' % ('fff' if not settings['dark'] else '212020'))
        for i in range(4):
            if i == 3:
                i += 2
            group = self.stackedWidget.findChild(QGroupBox, 'groupBox_%s' % (i + 3))
            group.setStyleSheet('background-color: #%s; border: 1px solid #%s; border-radius: 8px;' % (('fff', 'dfdfdf') if not settings['dark'] else ('1c1b1b', '121111')))

            if i == 5:
                i -= 2
            button = self.stackedWidget.findChild(QPushButton, 'pushButton_%s' % (i + 2))
            button.setStyleSheet('background-color: transparent; border-radius: 0px; border: 0px; color: #%s;' % ('3c3c3c' if not settings['dark'] else 'fff'))
            button.setCursor(QCursor(Qt.PointingHandCursor))
            if i == 0:
                button.clicked.connect(self.switchMe)
            if i == 1:
                button.clicked.connect(self.switchFriends)
            if i == 2:
                button.clicked.connect(self.switchSettings)
            if i == 3:
                button.clicked.connect(sys.exit)

        self.logout = self.stackedWidget.findChild(QPushButton, 'pushButton_6')
        self.logout.clicked.connect(client.logout)
        self.logout.setCursor(QCursor(Qt.PointingHandCursor))

        self.presenceImage = self.stackedWidget.findChild(QLabel, 'label_8')
        self.presenceImage.setScaledContents(True)
        self.label_11.setScaledContents(True)

        self.presenceText = self.stackedWidget.findChild(QLabel, 'label_7')
        self.presenceState = self.stackedWidget.findChild(QLabel, 'label_10')
        [x.setStyleSheet('background-color: transparent;') for x in (self.presenceText, self.presenceState)]

        self.presenceDesc = self.stackedWidget.findChild(QLabel, 'label_9')
        self.presenceDesc.setAlignment(Qt.AlignCenter)

        # Settings
        self.toggleDiscord = AnimatedToggle(self.page_3, checked_color = '#09ab44')
        self.toggleDiscord.setGeometry(QRect(101, 0, 60, 41))
        self.toggleStatus = AnimatedToggle(self.page_3, checked_color = '#09ab44')
        self.toggleStatus.setGeometry(QRect(101, 40, 60, 41))
        self.toggleTheme = AnimatedToggle(self.page_3, checked_color = '#09ab44')
        self.toggleTheme.setGeometry(QRect(101, 80, 60, 41))
        self.startInSystemTray = AnimatedToggle(self.page_3, checked_color = '#09ab44')
        self.startInSystemTray.setGeometry(QRect(101, 120, 60, 41))
        self.startOnLaunch = AnimatedToggle(self.page_3, checked_color = '#09ab44')
        self.startOnLaunch.setGeometry(QRect(101, 160, 60, 41))

        # [MacOS] Hide Buttons if running app.py directly.
        if platform.system() == "Darwin" and not isScriptBundled:
            self.startOnLaunch.setHidden(True)
            self.label_19.setHidden(True)
            self.startInSystemTray.setHidden(True)
            self.label_17.setHidden(True)

    def closeEvent(self, event = None):
        if self.mode == 1:
            sys.exit('User closed')
        event.ignore()
        self.MainWindow.hide()

    def grabToken(self):
        global session_token, user_lang, targetID
        try:
            session_token = self.session.run(*self.session.login(self.waitUntil))
            user_lang = self.comboBox.currentText()
            client.createCTX(session_token, user_lang, None, version)
        except Exception as e:
            print(log(f'An error occurred! Chances are, you didn\'t paste the right link, but here\'s the error message:\n{e}'))
            os._exit(1)

    def waitUntil(self):
        while self.mode == 1:
            pass
        return self.lineEdit.text().strip()

    def changeState(self):
        self.mode = 2
        while not client.api:
            pass
        try:
            client.setApp(self.updatePresence)
            client.connect()
            client.update()
        except Exception as e:
            log(e)
            raise e

        # Set user image
        client.api.user.image = loadPix(client.api.user.imageUri)
        radius = 150

        rounded = QPixmap(client.api.user.image.size())
        rounded.fill(QColor('transparent'))

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(client.api.user.image))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(client.api.user.image.rect(), radius, radius)
        del painter

        self.selfImage.setPixmap(rounded)

        # Set user details
        self.namePlate.setText(client.api.user.name)

        # Friends
        self.updateFriends()

        # Set NSwitch Icon
        self.nSwitchIcon.setPixmap(QPixmap(getPath('icon.png')))

        # Set toggle state
        self.toggleStatus.setChecked(client.running)
        self.toggleStatus.toggled.connect(self.switch)
        self.toggleTheme.setChecked(settings['dark'])
        self.toggleTheme.toggled.connect(self.setMode)
        self.toggleDiscord.setChecked(True if client.rpc else False)
        self.toggleDiscord.toggled.connect(self.toggleConnect)
        self.startInSystemTray.setChecked(settings.get("startInSystemTray", False))
        self.startInSystemTray.toggled.connect(self.setVisibility)
        self.startOnLaunch.setChecked(settings.get('startOnLaunch', False))
        self.startOnLaunch.toggled.connect(self.setLaunchMode)

        # Check Discord Errors
        self.checkDiscordError()

        # Set home
        self.switchMe()

        # Switch screens
        self.stackedWidget.setCurrentIndex(1)

    def updatePresence(self, user):
        global friendTime, iconsStorage, userSelected

        def mousePressEvent(event = None):
            pass

        def openLink(url):
            def e(event = None):
                event.ignore()
                webbrowser.open(url)
            return lambda event: e(event)

        # If the player is the user
        try:
            text = 'Friend Code: SW-%s' % str(user.links.get('friendCode').get('id')).replace(' ', '-')
            state = ''
            self.pushButton_7.setEnabled(False)
            self.pushButton_8.setEnabled(False)

            # Show notice when you dont have an account selected in friends.
            self.label_20.setHidden(False)
            self.label_21.setText('<a href="https://github.com/MCMi460/NSO-RPC#quickstart-guide" style="color: cyan;">NSO-RPC Quickstart Guide</a>')
        except:
            zone = '%Y/%m/%d'
            if client.api.userInfo['language'] == 'en-US':
                zone = '%m/%d/%Y'
            elif client.api.userInfo['language'] == 'en-GB':
                zone = '%d/%m/%Y'
            text = 'When You Became Friends:\n%s' % time.strftime(zone, time.localtime(user.friendCreatedAt))
            state = timeSince(user.presence.logoutAt)
            self.pushButton_7.setEnabled(True)
            self.pushButton_8.setEnabled(True)
            # Hide Notice and Quickstart Link.
            self.label_20.setHidden(True)
            self.label_21.setHidden(True)

        if user == client.api.user:
            self.pushButton_7.setEnabled(False)

        if not user.image:
            if not user.nsaId in iconsStorage:
                user.image = loadPix(user.imageUri)
                iconsStorage[user.nsaId] = user.image
            else:
                user.image = iconsStorage[user.nsaId]

        # Set user pic
        self.label_11.setPixmap(user.image)
        self.label_11.mousePressEvent = openLink(user.imageUri)
        self.label_11.setCursor(QCursor(Qt.PointingHandCursor))

        self.label_13.setText(user.name)

        self.label_14.setText(text)

        # Set presence image and game data
        if user.presence.game.name:
            threading.Thread(target = up, args = (self.presenceImage, user.presence.game.imageUri), daemon = True).start()

            self.presenceText.setText(user.presence.game.name)
            self.presenceText.adjustSize()
            state = user.presence.game.sysDescription
            if not state:
                state = 'Played for %s hours or more' % (int(user.presence.game.totalPlayTime / 60 / 5) * 5)
                if user.presence.game.totalPlayTime / 60 < 5:
                    state = 'Played for a little while'

            self.groupBox_7.setCursor(QCursor(Qt.PointingHandCursor))
            self.groupBox_7.mousePressEvent = openLink(user.presence.game.shopUri)
        else:
            self.presenceImage.clear()
            self.presenceText.setText('Offline')

            self.groupBox_7.setCursor(QCursor(Qt.ArrowCursor))
            self.groupBox_7.mousePressEvent = mousePressEvent
        self.presenceState.setText(state)
        self.presenceState.adjustSize()

        userSelected = user.nsaId

    def checkDiscordError(self):
        # This just assumes that if client.rpc is set to None, then there was a permission issue preventing NSO-RPC.
        # There was an attempt at catching the [Access is denied] event in the cli, however I had scope and timing issues with it.
        # We also assume that only Windows users would experence this permission oversight.
        # Updated by MCMi460 -- works for Admin issues as well as Discord is not running issues.
        if not client.rpc:
            ret = client.connect()
            if not ret[0]:
                msg = ''
                if 'WinError 5' in str(ret[1]):
                    msg = 'Try running NSO-RPC with Administrator.'
                elif 'Could not find Discord' in str(ret[1]) or 'Connection refused' in str(ret[1]):
                    msg = 'Try opening Discord first.'
                self.label_12.setFixedWidth(self.label_12.width() + 120)
                self.label_12.setFixedHeight(36)
                self.label_12.setText("<a style='color: orange;'>Unable to connect to Discord!<br>%s</a>" % msg)
                self.toggleDiscord.setHidden(True)
        else:
            self.toggleDiscord.setHidden(False)
            self.label_12.setFixedHeight(21)
            self.label_12.setText('Discord:')

    def updateProfile(self, new):
        if new:
            client.api.targetID = userSelected
        else:
            client.api.targetID = None
        with open(os.path.join(applicationPath, 'private.txt'), 'w') as file:
            file.write(json.dumps({
                'session_token': client.api.session_token,
                'user_lang': client.api.user_lang,
                'targetID': client.api.targetID,
            }))
        dlg = QMessageBox()
        dlg.setWindowTitle('NSO-RPC')
        dlg.setText('You will need to restart the application in order for the changes to take place.\nSorry for the inconvenience.')
        sys.exit(dlg.exec_())

    def setFriendIcons(self, layout):
        global client, iconsStorage
        n = 0
        i = 0
        for i in range(layout.count()):
            try:
                for items in layout.itemAt(i).widget().findChildren(QGroupBox):
                    i = 0
                    for item in items.findChildren(QLabel):
                        if i == 1:
                            if not client.api.friends[n].nsaId in iconsStorage:
                                iconsStorage[client.api.friends[n].nsaId] = loadPix(client.api.friends[n].imageUri)
                            client.api.friends[n].image = iconsStorage[client.api.friends[n].nsaId]
                            up(item, client.api.friends[n].image)
                        i += 1
                    n += 1
            except:
                break

    def updateFriends(self):
        client.api.getFriends()
        self.scrollArea.setWidget(QWidget())
        page = self.scrollArea.widget()
        layout = QGridLayout()
        j = 0
        n = 0
        overlay = QGroupBox()

        def openFriend(i):
            def e(event = None):
                event.ignore()
                self.updatePresence(client.api.friends[i])
                self.switchHome()
                client.gui = False
            return lambda event: e(event)
        for i in range(len(client.api.friends)):
            overlay.move(0, 0)
            overlay.setStyleSheet('background-color: transparent; border-radius: 0px; border: 0px;')
            overlay.setFixedSize(81 * 4 + (4 * 10), 111)
            if j == 3:
                layout.addWidget(overlay)
                layout.addWidget(QSplitter(Qt.Horizontal))
                overlay = QGroupBox()
                n += 1
            j = i % 4

            friend = client.api.friends[i]
            groupBox = QGroupBox(overlay)
            groupBox.setStyleSheet('background-color: #%s; border: 1px solid %s; border-radius: 8px;' % (('fff', '#dfdfdf') if not settings['dark'] else ('212020', 'transparent')))

            groupBox.setGeometry(QRect(10 + (j * 91), 0, 81, 111))
            groupBox.setFixedSize(81, 111)

            namePlate = QLabel(groupBox)
            namePlate.setGeometry(0, 81, 81, 30)
            namePlate.setAlignment(Qt.AlignCenter)
            namePlate.setText(friend.name)

            label = QLabel(groupBox)
            label.setGeometry(QRect(0, 0, 81, 81))
            label.setScaledContents(True)

            groupBox.mousePressEvent = openFriend(i)
            groupBox.setCursor(QCursor(Qt.PointingHandCursor))
        if j >= 0:
            overlay.move(0, 0)
            overlay.setStyleSheet('background-color: transparent; border-radius: 0px; border: 0px;')
            overlay.setFixedSize(81 * 4 + (4 * 10), 111)
            layout.addWidget(overlay)
            layout.addWidget(QSplitter(Qt.Horizontal))
        layout.addItem(QSpacerItem(0, 600))

        page.setLayout(layout)

        threading.Thread(target = self.setFriendIcons, args = (layout,), daemon = True).start()

    def switchMe(self):
        client.gui = True
        self.updatePresence(client.user)
        self.switchHome()

    def switchHome(self):
        self.stackedWidget_2.setCurrentIndex(0)

    def switchFriends(self):
        global friendTime
        if time.time() - friendTime >= 30:
            self.updateFriends()
            friendTime = time.time()
        self.stackedWidget_2.setCurrentIndex(1)

    def switchSettings(self):
        self.checkDiscordError()
        self.stackedWidget_2.setCurrentIndex(2)

    def openPfp(self, event = None):
        webbrowser.open(client.api.user.imageUri)

    def switch(self, toggle):
        client.running = toggle
        if not client.running:
            if client.rpc:
                client.rpc.clear()
            client.api.user.presence.game.name = ''
            self.updatePresence(client.api.user)

    def toggleConnect(self, toggle):
        if not toggle:
            client.disconnect()
        else:
            client.connect()
            if client.rpc:
                self.toggleStatus.setChecked(True)
                client.update()
            else:
                self.toggleDiscord.setChecked(False)


class SystemTrayApp(QSystemTrayIcon):
    def __init__(self, icon, parent):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)

        self.controller = menu.addAction('Open')
        self.controller.triggered.connect(self.switch)

        quit = menu.addAction('Quit')
        quit.triggered.connect(sys.exit)

        self.setContextMenu(menu)

    def switch(self):
        MainWindow.show()

    def windowsLightMode():  # https://stackoverflow.com/a/65349866
        try:
            import winreg
        except ImportError:
            return False
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        reg_keypath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        try:
            reg_key = winreg.OpenKey(registry, reg_keypath)
        except FileNotFoundError:
            return False

        for i in range(1024):
            try:
                value_name, value, _ = winreg.EnumValue(reg_key, i)
                if value_name == 'AppsUseLightTheme':
                    return value == 0
            except OSError:
                break
        return False


if __name__ == '__main__':
    if os.path.isfile(settingsFile):
        readSettings()
    else:
        writeSettings()

    window = GUI(MainWindow)

    iconFile = 'taskbarDark.png'
    if sys.platform.startswith('darwin'):
        import subprocess
        if not bool(subprocess.Popen('defaults read -g AppleInterfaceStyle', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True).communicate()[0]):
            iconFile = 'taskbarLight.png'
    if sys.platform.startswith('win'):
        if not bool(SystemTrayApp.windowsLightMode()):
            iconFile = 'taskBarLight.png'
    tray = SystemTrayApp(QIcon(getPath(iconFile)), MainWindow)
    app.setWindowIcon(QIcon(getPath("icon.png")))
    window.setupUi(MainWindow)
    window.selfService()

    def clientBackgroundCatcher():
        try:
            client.background()
        except Exception as e:
            log(e)
            raise e

    threading.Thread(target = clientBackgroundCatcher, daemon = True).start()

    if settings.get("startInSystemTray") == True:
        tray.show()
    else:
        tray.show()
        MainWindow.show()

    sys.exit(app.exec_())
