# Created by Deltaion Lee (MCMi460) on Github

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from layout import Ui_MainWindow
import sys
import threading
import requests
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
"""
# self.mode = 1 is for token
# self.mode = 2 is for full
def getPath(path):
    try:
        root = sys._MEIPASS
    except Exception:
        root = os.path.abspath('.')

    return os.path.join(root, path)

class GUI(Ui_MainWindow):
    def __init__(self, MainWindow):
        self.MainWindow = MainWindow

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
                button.clicked.connect(self.switchHome)
            if i == 1:
                button.clicked.connect(self.switchFriends)
            if i == 2:
                button.clicked.connect(self.switchSettings)
            if i == 3:
                button.clicked.connect(sys.exit)

        self.presenceImage = self.stackedWidget.findChild(QLabel, 'label_8')
        self.presenceImage.setScaledContents(True)

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
        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(client.api.user.imageUri).content)
        radius = 150

        rounded = QPixmap(pixmap.size())
        rounded.fill(QColor('transparent'))

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pixmap))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(pixmap.rect(), radius, radius)
        del painter

        self.selfImage.setPixmap(rounded)

        # Set user details
        self.namePlate.setText(client.api.user.name)

        # Set NSwitch Icon
        self.nSwitchIcon.setPixmap(QPixmap(getPath('icon.png')))

        # Set toggle state
        self.toggle.setChecked(client.running)
        self.toggle.toggled.connect(self.switch)

        # Set home
        self.switchHome()

        # Switch screens
        self.stackedWidget.setCurrentIndex(1)

    def updatePresence(self):
        def mousePressEvent(event = None):
            pass
        # Set presence image and game data
        if client.api.user.presence.game.name:
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(client.api.user.presence.game.imageUri).content)
            self.presenceImage.setPixmap(pixmap)

            self.presenceText.setText(client.api.user.presence.game.name)
            self.presenceText.adjustSize()
            self.presenceState.setText(client.state)
            self.presenceState.adjustSize()

            self.groupBox_7.setCursor(QCursor(Qt.PointingHandCursor))
            self.groupBox_7.mousePressEvent = self.openShop
        else:
            self.presenceImage.clear()
            self.presenceText.setText('Offline')
            self.presenceState.setText('')

            self.groupBox_7.setCursor(QCursor(Qt.ArrowCursor))
            self.groupBox_7.mousePressEvent = mousePressEvent

    def switchHome(self):
        self.stackedWidget_2.setCurrentIndex(0)

    def switchFriends(self):
        self.stackedWidget_2.setCurrentIndex(1)

    def switchSettings(self):
        self.stackedWidget_2.setCurrentIndex(2)

    def openPfp(self, event = None):
        webbrowser.open(client.api.user.imageUri)

    def openShop(self, event = None):
        webbrowser.open(client.api.user.presence.game.shopUri)

    def switch(self):
        client.running = not client.running
        if not client.running:
            client.rpc.clear()

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
