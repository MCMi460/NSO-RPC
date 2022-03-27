from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from layout import Ui_MainWindow
import sys
import threading
from cli import *

# NSO Variables
session_token = None
path = os.path.expanduser('~/Documents/NSO-RPC/private.txt')
if os.path.isfile(path):
    with open(path, 'r') as file:
        session_token = json.loads(file.read())['session_token']
client = Discord(session_token)
# PyQt5 Variables

class GUI(Ui_MainWindow):
    def __init__(self, MainWindow):
        self.MainWindow = MainWindow

    def selfService(self):
        self.MainWindow.setStyleSheet(open('./layout/layout.css', 'r').read())
        self.assignVariables()

        self.MainWindow.closeEvent = self.closeEvent

        self.state = False
        if not session_token:
            self.session = Session()
            threading.Thread(target = self.grabToken, daemon = True).start()

    def assignVariables(self):
        self.button = self.groupBox.findChild(QPushButton, 'pushButton')
        self.button.clicked.connect(self.changeState)

        self.lineEdit = self.groupBox.findChild(QLineEdit, 'lineEdit')

    def closeEvent(self, event):
        if not self.state:
            sys.exit()
        event.ignore()
        self.MainWindow.hide()
        tray.show()
        tray.controller.setChecked(True)

    def grabToken(self):
        global session_token
        try:
            session_token = self.session.run(*self.session.login(self.waitUntil))
            client.createCTX(session_token)
        except Exception as e:
            print(f'An error occurred! Chances are, you didn\'t paste the right link, but here\'s the error message:\n{e}')
            os._exit(1)

    def waitUntil(self):
        while not self.state:
            pass
        return self.lineEdit.text().strip()

    def changeState(self):
        self.state = True
        self.MainWindow.close()

class SystemTrayApp(QSystemTrayIcon):
    def __init__(self, icon, parent):
        QSystemTrayIcon.__init__(self, icon, parent)
        menu = QMenu(parent)

        self.controller = menu.addAction('Discord')
        self.controller.setCheckable(True)
        self.controller.setChecked(client.running)
        self.controller.toggled.connect(self.switch)

        quit = menu.addAction('Quit')
        quit.triggered.connect(sys.exit)

        self.setContextMenu(menu)

    def switch(self):
        if session_token:
            client.running = not client.running
            self.controller.setChecked(client.running)
            if not client.running:
                client.rpc.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    MainWindow = QMainWindow()
    window = GUI(MainWindow)

    tray = SystemTrayApp(QIcon('icon.png'), MainWindow)
    window.setupUi(MainWindow)
    window.selfService()

    threading.Thread(target = client.background, daemon = True).start()

    if session_token:
        tray.show()
    else:
        MainWindow.show()

    sys.exit(app.exec_())
