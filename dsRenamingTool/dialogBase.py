import sys
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


def mayaMainWindow():
    """
    Get maya main window as QWidget

    :return: Maya main window as QWidget
    :rtype: PySide2.QtWidgets.QWidget
    """
    mainWindowPtr = omui.MQtUtil.mainWindow()
    if mainWindowPtr:
        if sys.version_info[0] < 3:
            return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)  # noqa: F821
        else:
            return wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)
    else:
        mayaMainWindow()


class _modalDialog(QtWidgets.QDialog):

    def __init__(self, parent=mayaMainWindow()):
        super(_modalDialog, self).__init__(parent)

        # Disable question mark for windows
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        # MacOSX window stay on top
        self.setProperty("saveWindowPref", True)

        self.createActions()
        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def createActions(self):
        pass

    def createWidgets(self):
        pass

    def createLayouts(self):
        pass

    def createConnections(self):
        pass
