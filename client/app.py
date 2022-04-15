# Created by Deltaion Lee (MCMi460) on Github

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from layout import Ui_MainWindow
import sys
import threading
import requests
import time
from qtwidgets import Toggle, AnimatedToggle
from cli import *

# NSO Variables
session_token, user_lang = getToken(False)
client = Discord(session_token, user_lang)
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
  color: #fff;
  background-color: #e60012;
  border-radius: 10px;
  text-align: center;
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
def up(_label,image):
    _label.clear()
    if isinstance(image,str):
        image = loadPix(image)
    _label.setPixmap(image)
def timeSince(epoch:int):
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

class GUI(Ui_MainWindow):
    def __init__(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setFixedSize(600, 600)

    def selfService(self):
        self.MainWindow.setStyleSheet(style)
        self.assignVariables()

        self.MainWindow.closeEvent = self.closeEvent

        self.mode = 1
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

        self.namePlate = self.stackedWidget.findChild(QLabel, 'label_4')
        self.namePlate.setAlignment(Qt.AlignCenter)
        self.namePlate.setStyleSheet('color:#fff;')

        self.groupBox_2.setStyleSheet('background-color: #e60012; border-radius: 0px;')

        self.groupBox_2.findChild(QLabel, 'label_5').setStyleSheet('font-weight: bold; color: #fff;')
        self.nSwitchIcon = self.groupBox_2.findChild(QLabel, 'label_6')
        self.nSwitchIcon.setScaledContents(True)

        self.groupBox_6.setStyleSheet('background-color: #fff; border: 0px; border-radius: 0px;')
        for i in range(4):
            if i == 3:
                i += 2
            group = self.stackedWidget.findChild(QGroupBox, 'groupBox_%s' % (i + 3))
            group.setStyleSheet('background-color: #fff; border: 1px solid #dfdfdf; border-radius: 8px;')

            if i == 5:
                i -= 2
            button = self.stackedWidget.findChild(QPushButton, 'pushButton_%s' % (i + 2))
            button.setStyleSheet('background-color: transparent; border-radius: 0px; border: 0px; color: #3c3c3c;')
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
        [ x.setStyleSheet('background-color: transparent;') for x in (self.presenceText,self.presenceState) ]

        self.presenceDesc = self.stackedWidget.findChild(QLabel, 'label_9')
        self.presenceDesc.setAlignment(Qt.AlignCenter)

        # Settings
        self.toggle = AnimatedToggle(self.page_3, checked_color = '#09ab44')
        self.toggle.setGeometry(QRect(101,0,60,41))

    def closeEvent(self, event = None):
        if self.mode == 1:
            sys.exit('User closed')
        event.ignore()
        self.MainWindow.hide()
        tray.show()

    def grabToken(self):
        global session_token, user_lang
        try:
            session_token = self.session.run(*self.session.login(self.waitUntil))
            user_lang = self.comboBox.currentText()
            client.createCTX(session_token, user_lang)
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
        client.setApp(self.updatePresence)
        client.update()

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
        self.toggle.setChecked(client.running)
        self.toggle.toggled.connect(self.switch)

        # Set home
        self.switchMe()

        # Switch screens
        self.stackedWidget.setCurrentIndex(1)

    def updatePresence(self, user):
        def mousePressEvent(event = None):
            pass
        def openLink(url):
            def e(event = None):
                event.ignore()
                webbrowser.open(url)
            return lambda event : e(event)

        if not user.image:
            user.image = loadPix(user.imageUri)

        # Set user pic
        self.label_11.setPixmap(user.image)
        self.label_11.mousePressEvent = openLink(user.imageUri)
        self.label_11.setCursor(QCursor(Qt.PointingHandCursor))

        self.label_13.setText(user.name)

        try:
            text = 'Friend Code: SW-%s' % str(user.links.get('friendCode').get('id')).replace(' ','-')
            state = ''
        except:
            text = 'Added Friend at: %s' % time.strftime('%Y-%m-%d', time.localtime(user.friendCreatedAt))
            state = timeSince(user.presence.logoutAt)
        self.label_14.setText(text)

        # Set presence image and game data
        if user.presence.game.name:
            threading.Thread(target = up, args = (self.presenceImage,user.presence.game.imageUri), daemon = True).start()

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

    def setFriend(self, i):
        global client
        client.api.friends[i].image = loadPix(client.api.friends[i].imageUri)

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
            return lambda event : e(event)
        for i in range(len(client.api.friends)):
            overlay.move(0, 0)
            overlay.setStyleSheet('background-color: transparent; border-radius: 0px; border: 0px;')
            overlay.setFixedSize(81 * 4 + (4 * 10), 111)
            if j == 3:
                layout.addWidget(overlay)
                overlay = QGroupBox()
                n += 1
            j = i % 4

            friend = client.api.friends[i]
            groupBox = QGroupBox(overlay)
            groupBox.setStyleSheet('background-color: #fff; border: 1px solid #dfdfdf; border-radius: 8px;')

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

        page.setLayout(layout)
        def whatever():
            n = 0
            i = 0
            for i in range(layout.count()):
                for items in layout.itemAt(i).widget().findChildren(QGroupBox):
                    i = 0
                    for item in items.findChildren(QLabel):
                        if i == 1:
                            self.setFriend(n)
                            up(item,client.api.friends[n].image)
                        i += 1
                    n += 1
        threading.Thread(target = whatever, args = (), daemon = True).start()

    def switchMe(self):
        client.gui = True
        self.updatePresence(client.user)
        self.switchHome()

    def switchHome(self):
        self.stackedWidget_2.setCurrentIndex(0)

    def switchFriends(self):
        self.stackedWidget_2.setCurrentIndex(1)

    def switchSettings(self):
        self.stackedWidget_2.setCurrentIndex(2)

    def openPfp(self, event = None):
        webbrowser.open(client.api.user.imageUri)

    def switch(self):
        client.running = not client.running
        if not client.running:
            client.rpc.clear()
            client.api.user.presence.game.name = ''
            self.updatePresence(client.api.user)

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
        tray.hide()
        MainWindow.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    MainWindow = QMainWindow()
    window = GUI(MainWindow)

    tray = SystemTrayApp(QIcon(getPath('icon.png')), MainWindow)
    window.setupUi(MainWindow)
    window.selfService()

    threading.Thread(target = client.background, daemon = True).start()

    MainWindow.show()

    sys.exit(app.exec_())
