# Created by Deltaion Lee (MCMi460) on Github

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from layout import Ui_MainWindow
import sys
import threading
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

        self.state = False
        if not session_token:
            self.session = Session()
            threading.Thread(target = self.grabToken, daemon = True).start()

    def assignVariables(self):
        self.button = self.groupBox.findChild(QPushButton, 'pushButton')
        self.button.clicked.connect(self.changeState)

        self.lineEdit = self.groupBox.findChild(QLineEdit, 'lineEdit')

        self.comboBox = self.groupBox.findChild(QComboBox, 'comboBox')
        self.comboBox.clear()
        self.comboBox.addItems(languages)

    def closeEvent(self, event):
        if not self.state:
            sys.exit()
        event.ignore()
        self.MainWindow.hide()
        tray.show()
        tray.controller.setChecked(True)

    def grabToken(self):
        global session_token, user_lang
        try:
            session_token = self.session.run(*self.session.login(self.waitUntil))
            user_lang = self.comboBox.currentText()
            client.createCTX(session_token, user_lang)
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

    tray = SystemTrayApp(QIcon(getPath('icon.png')), MainWindow)
    window.setupUi(MainWindow)
    window.selfService()

    threading.Thread(target = client.background, daemon = True).start()

    if session_token:
        tray.show()
    else:
        MainWindow.show()

    sys.exit(app.exec_())
