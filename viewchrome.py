import sys
import threading
import time
# from selenium import webdriver
import undetected_chromedriver as webdriver
from viewer import Ui_SeleniumrViewer
from PyQt5 import QtWidgets
import psutil
import win32gui
import win32process
from webdriver_manager.chrome import ChromeDriverManager
chromedriver = ChromeDriverManager().install()
def Set():
        list_hwnd = {}
        def enumHandler(hwnd, lParam):
            text = win32gui.GetWindowText(hwnd)
            enable = win32gui.IsWindowEnabled (hwnd)
            # if "chrome" in text.lower():
            if win32gui.IsWindowVisible (hwnd) and win32gui.IsWindowEnabled (hwnd) and "chrome" in text.lower():
                __, pid = win32process.GetWindowThreadProcessId(hwnd)
                list_hwnd[pid] = hwnd
        win32gui.EnumWindows(enumHandler, None)
        return list_hwnd
def view():
    global ui
    app = QtWidgets.QApplication(sys.argv)
    SeleniumrViewer = QtWidgets.QWidget()
    ui = Ui_SeleniumrViewer()
    ui.setupUi(SeleniumrViewer)
    SeleniumrViewer.show()
    for i in range(5):
        threading.Thread(target=getDriver, args=(i, )).start()
    sys.exit(app.exec_())
def getDriver(i):
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options, use_subprocess=True, driver_executable_path=chromedriver)
    userdata = '--user-data-dir='+driver.user_data_dir
    for process in psutil.process_iter():
        if process.name() == 'chrome.exe' and userdata in process.cmdline() and "--remote-debugging-host=127.0.0.1" in process.cmdline():
            pid = process.pid
            # print(process.cmdline())
    handle = Set()[pid]
    win32gui.SetParent(handle, ui.hwnd[i])
    win32gui.MoveWindow(handle, -8, -40, 470, 525, True)
    driver.get("https://gleam.io/g58DZ/ggem-1500-airdrop")
    time.sleep(200)
    # print(handle)
    pass
def new():
    def create_view_chrome(self):
        global ROW_VIEW, COL_VIEW
        self.widget[self.index_view] = QWidget(self.scrollAreaWidgetContents)
        self.widget[self.index_view].setStyleSheet("background-color: yellow;")
        # self.widget[self.index_view].setMaximumSize(500, 500)
        # self.widget[self.index_view].setMinimumSize(500, 500)
        self.widget[self.index_view].setLayout(QVBoxLayout())
        if COL_VIEW == 2:
            ROW_VIEW += 1
            COL_VIEW = 0
        self.gridLayout_4.addWidget(self.widget[self.index_view], ROW_VIEW, COL_VIEW, 1, 1)
        COL_VIEW += 1
        self.index_view += 1
        return self.index_view - 1
    def set_parent_handle(self, chrome_handle):
        index = self.create_view_chrome()
        qwindow = QWindow.fromWinId(chrome_handle)
        container = QWidget.createWindowContainer(qwindow, self)
        container.setFocusPolicy(Qt.NoFocus)
        self.widget[index].layout().addWidget(container)
if __name__ == "__main__":
    view()
    
    