import os
import pymel.core as pm
import pymel.api as pma
from PySide2 import QtWidgets

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import getCppPointer

from dsRenamingTool.loggingFn import Logger
from dsRenamingTool.template import Template


def add_widget_to_layout(widget, control_name):
    if pm.workspaceControl(control_name, q=1, ex=1):
        if os.sys.version_info[0] >= 3:
            workspaceControlPtr = int(pma.MQtUtil.findControl(control_name))
            widgetPtr = int(getCppPointer(widget)[0])
        else:
            workspaceControlPtr = long(pma.MQtUtil.findControl(control_name))
            widgetPtr = long(getCppPointer(widget)[0])

        pma.MQtUtil.addWidgetToMayaLayout(widgetPtr, workspaceControlPtr)


class Dialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "dsRenaming Tool"
    UI_NAME = "dsRenamingTool"
    UI_SCRIPT = "import dsRenamingTool\ndsRenamer = dsRenamingTool.Dialog()"
    UI_INSTANCE = None

    @classmethod
    def display(cls):
        if not cls.UI_INSTANCE:
            cls.UI_INSTANCE = Dialog()

        if cls.UI_INSTANCE.isHidden():
            cls.UI_INSTANCE.show(dockable=1, uiScript=cls.UI_SCRIPT)
        else:
            cls.UI_INSTANCE.raise_()
            cls.UI_INSTANCE.activateWindow()

    def __init__(self):
        super(Dialog, self).__init__()
        self.__class__.UI_INSTANCE = self
        self.setObjectName(self.__class__.UI_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)

        # WorkspaceControl
        self.workspaceControlName = "{0}WorkspaceControl".format(self.UI_NAME)
        add_widget_to_layout(self, self.workspaceControlName)

        # UI setup
        self.create_actions()
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_actions(self):
        # Menubar
        self.menuBar = QtWidgets.QMenuBar(self)
        editMenu = self.menuBar.addMenu("&Edit")

        # Actions
        self.editSuffixAliasesAction = QtWidgets.QAction("Suffix aliases", self)

        # Populate menubar
        editMenu.addAction(self.editSuffixAliasesAction)

    def create_widgets(self):
        pass

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

    def create_connections(self):
        pass

    def rename_selected(self):
        pass
