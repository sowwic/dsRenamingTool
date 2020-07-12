import pymel.core as pm
import pymel.api as pma
import logging
import logging.config
import json
from PySide2 import QtWidgets

from dsRenamingTool import renameFn
from dsRenamingTool import aliasesDialog
from dsRenamingTool import config
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import getCppPointer


# Setup logging
LOGGER = logging.getLogger(__name__)


class Dialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    WINDOW_TITLE = "dsRenaming Tool"
    UI_NAME = "dsRenamingTool"
    UI_SCRIPT = "import dsRenamingTool\ndsRenamer = dsRenamingTool.Dialog()"
    UI_INSTANCE = None

    DEFAULT_SETTINGS = {"autoSuffix": True,
                        "indexing": True,
                        "indexPadding": 1,
                        "indexStart": 0}

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
        self.setMinimumSize(300, 170)
        self.settings = self.loadSettings()

        workspaceControlName = "{0}WorkspaceControl".format(self.UI_NAME)
        if pm.workspaceControl(workspaceControlName, q=1, ex=1):
            workspaceControlPtr = long(pma.MQtUtil.findControl(workspaceControlName))
            widgetPtr = long(getCppPointer(self)[0])

            pma.MQtUtil.addWidgetToMayaLayout(widgetPtr, workspaceControlPtr)

        # UI setup
        self.createActions()
        self.createWidgets()
        self.createLayouts()
        self.createConnections()

        # Aliases optionVar
        aliasesDialog.AliasDialog.checkOptionVar()

    def createActions(self):
        # Menubar
        self.menuBar = QtWidgets.QMenuBar(self)
        editMenu = self.menuBar.addMenu("&Edit")

        # Actions
        self.editSuffixAliasesAction = QtWidgets.QAction("Suffix aliases", self)

        # Populate menubar
        editMenu.addAction(self.editSuffixAliasesAction)

    def createWidgets(self):
        self.baseNameLineEdit = QtWidgets.QLineEdit()
        self.prefixLineEdit = QtWidgets.QLineEdit()
        self.suffixLineEdit = QtWidgets.QLineEdit()
        self.autoSuffixCheckBox = QtWidgets.QCheckBox("Auto suffix")
        self.indexingCheckBox = QtWidgets.QCheckBox("Indexing")
        self.indexPaddingSpinBox = QtWidgets.QSpinBox()
        self.startingIndexSpinBox = QtWidgets.QSpinBox()
        self.applyButton = QtWidgets.QPushButton("Apply")
        self.closeButton = QtWidgets.QPushButton("Close")

        # Adjust widgets
        self.baseNameLineEdit.setPlaceholderText("Name")
        self.prefixLineEdit.setPlaceholderText("Prefix")
        self.suffixLineEdit.setPlaceholderText("Suffix")
        self.autoSuffixCheckBox.setChecked(self.settings.get("autoSuffix", True))
        self.indexingCheckBox.setChecked(self.settings.get("indexing", True))
        self.indexPaddingSpinBox.setValue(self.settings.get("indexPadding", 1))
        self.startingIndexSpinBox.setValue(self.settings.get("indexing", 0))
        self.applyButton.setMinimumSize(70, 20)
        self.closeButton.setMinimumSize(70, 20)

    def createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        renameLayout = QtWidgets.QHBoxLayout()
        optionsLayout = QtWidgets.QHBoxLayout()
        self.indexLayout = QtWidgets.QFormLayout()
        buttonsLayout = QtWidgets.QHBoxLayout()

        # Populate rename
        renameLayout.addWidget(self.prefixLineEdit)
        renameLayout.addWidget(self.baseNameLineEdit)
        renameLayout.addWidget(self.suffixLineEdit)

        # Populate options
        optionsLayout.addWidget(self.autoSuffixCheckBox)
        optionsLayout.addWidget(self.indexingCheckBox)
        optionsLayout.addStretch()

        # Populate index
        self.indexLayout.addRow("Index padding", self.indexPaddingSpinBox)
        self.indexLayout.addRow("Index start", self.startingIndexSpinBox)

        # Populate buttons
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.applyButton)
        buttonsLayout.addWidget(self.closeButton)

        # Populate main
        mainLayout.addLayout(renameLayout)
        mainLayout.addLayout(optionsLayout)
        mainLayout.addLayout(self.indexLayout)
        mainLayout.addLayout(buttonsLayout)
        mainLayout.setSpacing(10)
        mainLayout.setContentsMargins(10, 25, 10, 10)

    def createConnections(self):
        self.closeButton.clicked.connect(self.hide)
        self.indexingCheckBox.toggled.connect(self.indexPaddingSpinBox.setEnabled)
        self.indexingCheckBox.toggled.connect(self.startingIndexSpinBox.setEnabled)
        self.editSuffixAliasesAction.triggered.connect(self.editSuffixAliases)
        self.applyButton.clicked.connect(self.rename)

        # Settings changed
        self.closeEventTriggered.connect(self.saveSettings)

    def rename(self):
        sel = pm.ls(sl=1, r=1)
        tempList = []
        aliasesDict = json.loads(pm.optionVar.get("dsRenamingToolSuffixAliases", json.dumps(aliasesDialog.AliasDialog.DEFAULT_SUFFIX_ALIASES, sort_keys=True)))
        for each in sel:
            tempList.append(renameFn.RenameUtils.rename(each,
                                                        "tempName",
                                                        aliasesDict,
                                                        prefix="NULL",
                                                        suffix="NULL",
                                                        autoSuffix=False,
                                                        indexing=True,
                                                        indexPadding=0,
                                                        startIndex=0))
        for each in tempList:
            renameFn.RenameUtils.rename(each,
                                        self.baseNameLineEdit.text(),
                                        aliasesDict,
                                        prefix=self.prefixLineEdit.text(),
                                        suffix=self.suffixLineEdit.text(),
                                        autoSuffix=self.autoSuffixCheckBox.isChecked(),
                                        indexing=self.indexingCheckBox.isChecked(),
                                        indexPadding=self.indexPaddingSpinBox.value(),
                                        startIndex=self.startingIndexSpinBox.value())

    def editSuffixAliases(self):
        editDialog = aliasesDialog.AliasDialog(parent=self)
        editDialog.show()

    # Events

    def showEvent(self, e):
        self.resize(self.minimumSize())

    def hideEvent(self, e):
        self.saveSettings()

    # Properties
    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, settingsDict):
        self._settings = settingsDict

    def loadSettings(self):
        loaded = pm.optionVar.get("dsRiggingRenamingToolSettings", json.dumps(self.DEFAULT_SETTINGS, sort_keys=True))
        return json.loads(loaded)

    # @QtCore.Slot()
    def saveSettings(self):
        self.settings = {"indexing": self.indexingCheckBox.isChecked(),
                         "indexStart": self.startingIndexSpinBox.value(),
                         "autoSuffix": self.autoSuffixCheckBox.isChecked(),
                         "indexPadding": self.indexPaddingSpinBox.value()}
        pm.optionVar["dsRiggingRenamingToolSettings"] = json.dumps(self.settings, sort_keys=True)
        return 1


if __name__ == "__main__":
    try:
        if dsRenamer and dsRenamer.parent():  # noqa: F821
            workspaceControlName = dsRenamer.parent().objectName()  # noqa: F821

            if pm.window(workspaceControlName, ex=1, q=1):
                pm.deleteUI(workspaceControlName)
    except Exception:
        pass

    dsRenamer = Dialog()

    uiScript = "import dsRenamingTool\ndsRenamer = dsRenamingTool.Dialog()"
    dsRenamer.show(dockable=1, uiScript=uiScript)
