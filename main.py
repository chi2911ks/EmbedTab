
import sys
import threading
from time import sleep
import traceback
import typing
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from GUI.embed_tab_ui import Ui_FormView
from flask import Flask, request, jsonify
from utils.find_handle import is_window
app = Flask(__name__)
ROW_VIEW = COL_VIEW = 0
NUMBER_COL = 3
MAX_HEIGHT = 500
PORT = 5000


class MainEmbed(QWidget, QObject):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_FormView()
        self.ui.setupUi(self)
        self.setWindowTitle("Embed Tab")
        self.embed_dict = {}
        self.widget: typing.Dict[int, QWidget] = {}
        self.index_view = 0
        threading.Thread(target=app.run, args=(
            '127.0.0.1', PORT, ), daemon=True).start()

    @pyqtSlot()
    def __create_view(self):
        global ROW_VIEW, COL_VIEW
        self.widget[self.index_view] = QWidget(
            self.ui.scrollAreaWidgetContents)
        self.widget[self.index_view].setStyleSheet("background-color: gray;")
        self.widget[self.index_view].setMaximumHeight(MAX_HEIGHT)
        self.widget[self.index_view].setMinimumHeight(MAX_HEIGHT)
        self.widget[self.index_view].setLayout(QHBoxLayout())
        if COL_VIEW == NUMBER_COL:
            ROW_VIEW += 1
            COL_VIEW = 0
        self.ui.gridLayout_2.addWidget(
            self.widget[self.index_view], ROW_VIEW, COL_VIEW, 1, 1)
        
        COL_VIEW += 1
        self.index_view += 1
        return self.index_view-1
    

    @pyqtSlot(int, int)
    def __embed_chrome(self, index, chrome_handle):
        if self.widget:
            qwindow = QWindow.fromWinId(chrome_handle)
            container = QWidget.createWindowContainer(qwindow, self)
            container.setFocusPolicy(Qt.NoFocus)
            layout = self.widget[index].layout()
            # delete widget old
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().deleteLater()

            layout.addWidget(container)

    @pyqtSlot()
    def __arrange_view(self):
        # arrange remaining view
        global ROW_VIEW, COL_VIEW
        ROW_VIEW = COL_VIEW = 0
        for index, widget in self.widget.items():
            if COL_VIEW == NUMBER_COL:
                ROW_VIEW += 1
                COL_VIEW = 0
            self.ui.gridLayout_2.addWidget(
                widget, ROW_VIEW, COL_VIEW, 1, 1)
            COL_VIEW += 1


        

    def embed(self):
        def is_it_true(value):
            return value.lower() == 'true'
        try:
            handle = request.args.get('handle', '????? wtf')
            new = request.args.get('new', default=False, type=is_it_true)
            index = request.args.get('index', '')
            if handle == "":
                return jsonify({"status": False, "msg": "wtf handle?"})
            
            if is_window(int(handle)):
                if not new:
                    if index == "":
                        return jsonify({"status": False, "msg": "Please enter index!"})
                    index = int(index)
                    if index not in self.widget:
                        print("No indexes have been created for this tab!")
                        return jsonify({"status": False, "msg": "No indexes have been created for this tab!"})
                else:
                    index = QMetaObject.invokeMethod(
                        self, "__create_view", Qt.QueuedConnection)
                    sleep(1)
                    index = self.index_view-1
                    
                QMetaObject.invokeMethod(self, "__embed_chrome",
                                         Qt.QueuedConnection,
                                         Q_ARG(int, index),
                                         Q_ARG(int, int(handle)))
                
                self.embed_dict[int(handle)] = index
                return jsonify({"status": True, "msg": "success"})
            else:
                return jsonify({"status": False, "msg": "handle not found!"})
        except:
            return jsonify({"status": False, "msg": "error embed!", "error": traceback.format_exc()})
        

    def unembed(self):
        try:
            handle = request.args.get('handle', '????? wtf')
            if handle == "":
                return jsonify({"status": False, "msg": "wtf handle?"})
                        
            if is_window(int(handle)):
                if int(handle) in self.embed_dict:
                    index = self.embed_dict[int(handle)]
                    layout = self.widget[index].layout()

                    self.widget[index].deleteLater()

                    self.ui.gridLayout_2.removeWidget(self.widget[index])
                    self.widget.pop(index)
                    self.embed_dict.pop(int(handle))

                    data = QMetaObject.invokeMethod(
                        self, "__arrange_view", Qt.QueuedConnection)


                    return jsonify({"status": True, "msg": "success"})
                else:
                    return jsonify({"status": False, "msg": "handle not found!"})
            else:
                return jsonify({"status": False, "msg": "handle not found!"})


        except:
            return jsonify({"status": False, "msg": "error unembed!", "error": traceback.format_exc()})


@app.route('/embed', methods=['GET'])
def embed():
    return main.embed()

@app.route('/unembed', methods=['GET'])
def unembed():
    return main.unembed()





if __name__ == "__main__":
    app_ui = QApplication(sys.argv)
    main = MainEmbed()
    main.show()
    sys.exit(app_ui.exec_())
