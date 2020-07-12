import pymel.core as pm
import json
from PySide2 import QtWidgets, QtCore
from dsRenamingTool import dialogBase


class AliasDialog(dialogBase._modalDialog):

    DEFAULT_SUFFIX_ALIASES = {
        "transform": "GRP",
        "mesh": "PLY",
        "nurbsCurve": "CRV",
        "nurbsSurface": "NURB",
        "pointLight": "LGT",
        "areaLight": "LGT",
        "joint": "JNT",
        "locator": "LOC",
        "camera": "CAM",
    }

    def __init__(self, parent=None, title="Edit aliases"):
        super(AliasDialog, self).__init__(parent=parent)

        # Setup UI
        self.setWindowTitle(title)
        self.setMinimumSize(300, 200)

        # Update table
        self.updateAliasTable()

    def createActions(self):
        # Menubar
        self.menuBar = QtWidgets.QMenuBar(self)
        editMenu = self.menuBar.addMenu("&Edit")

        # Actions
        self.addAliasesAction = QtWidgets.QAction("Add new alias", self)
        self.deleteAliasAction = QtWidgets.QAction("Delete selected", self)
        self.resetAliasesAction = QtWidgets.QAction("Reset to defaults", self)

        # Populate menubar
        editMenu.addAction(self.addAliasesAction)
        editMenu.addAction(self.deleteAliasAction)
        editMenu.addAction(self.resetAliasesAction)

    def createWidgets(self):
        # Table
        self.aliasesTable = AliasTable()
        self.aliasesTable.setColumnCount(2)
        self.aliasesTable.setHorizontalHeaderLabels(["Object type", "Suffix"])
        tableHeaderView = self.aliasesTable.horizontalHeader()
        tableHeaderView.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        # Dialog buttons
        self.confirmButton = QtWidgets.QPushButton("Confirm")
        self.saveButton = QtWidgets.QPushButton("Save")
        self.cancelButton = QtWidgets.QPushButton("Cancel")

    def createLayouts(self):
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(10, 25, 10, 10)

        # Table layout
        tableLayout = QtWidgets.QVBoxLayout()
        tableLayout.addWidget(self.aliasesTable)

        # Buttons layout
        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(self.confirmButton)
        buttonsLayout.addWidget(self.saveButton)
        buttonsLayout.addWidget(self.cancelButton)

        # Populate main
        self.mainLayout.addLayout(tableLayout)
        self.mainLayout.addLayout(buttonsLayout)

    def createConnections(self):
        # Buttons
        self.confirmButton.clicked.connect(self.confirmAndClose)
        self.saveButton.clicked.connect(self.saveAliases)
        self.cancelButton.clicked.connect(self.close)

        # Actions
        self.addAliasesAction.triggered.connect(self.aliasesTable.addNewEntry)
        self.deleteAliasAction.triggered.connect(self.aliasesTable.deleteSelectedRow)
        self.resetAliasesAction.triggered.connect(self.resetToDefault)

    def updateAliasTable(self):
        self.aliasesTable.setRowCount(0)
        self.suffixAliases = json.loads(pm.optionVar.get("dsRenamingToolSuffixAliases", json.dumps(self.DEFAULT_SUFFIX_ALIASES, sort_keys=True)))
        for i, k in enumerate(self.suffixAliases.keys()):
            self.aliasesTable.insertRow(i)
            self.insertItem(i, 0, text=k)
            self.insertItem(i, 1, text=self.suffixAliases[k])

    def insertItem(self, row, column, text=""):
        item = QtWidgets.QTableWidgetItem(text)
        self.aliasesTable.setItem(row, column, item)

        return item

    def getAliasTableData(self):
        newAliasDict = {}
        for row in range(0, self.aliasesTable.rowCount()):
            objType = self.aliasesTable.model().index(row, 0).data()
            suffix = self.aliasesTable.model().index(row, 1).data()
            if objType:
                newAliasDict[str(objType)] = str(suffix)

        return newAliasDict

    def saveAliases(self):
        self.suffixAliases = self.getAliasTableData()
        aliasString = json.dumps(self.suffixAliases, sort_keys=True)
        pm.optionVar["dsRenamingToolSuffixAliases"] = aliasString

    def confirmAndClose(self):
        self.saveAliases()
        self.close()

    def showEvent(self, e):
        self.checkOptionVar()

    def resetToDefault(self):
        self.aliasesTable.setRowCount(0)
        for i, k in enumerate(self.DEFAULT_SUFFIX_ALIASES.keys()):
            self.aliasesTable.insertRow(i)
            self.insertItem(i, 0, text=k)
            self.insertItem(i, 1, text=self.DEFAULT_SUFFIX_ALIASES[k])

    @classmethod
    def checkOptionVar(cls):
        pm.optionVar.get("dsRenamingToolSuffixAliases", json.dumps(cls.DEFAULT_SUFFIX_ALIASES, sort_keys=True))


class AliasTable(QtWidgets.QTableWidget):
    def __init__(self, rows=0, columns=0, parent=None):
        super(AliasTable, self).__init__(rows, columns, parent)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.createActions()
        self.createConnections()

    def createActions(self):
        self.addAliasAction = QtWidgets.QAction("Add new alias", self)
        self.deleteAliasAction = QtWidgets.QAction("Delete alias", self)

    def createConnections(self):
        self.addAliasAction.triggered.connect(self.addNewEntry)
        self.deleteAliasAction.triggered.connect(self.deleteSelectedRow)

    def addNewEntry(self):
        newIndex = self.rowCount()
        self.insertRow(newIndex)

    def deleteSelectedRow(self):
        for each in self.selectedItems():
            self.removeRow(each.row())

    def showContextMenu(self, point):
        contextMenu = QtWidgets.QMenu()
        contextMenu.addAction(self.addAliasAction)
        contextMenu.addAction(self.deleteAliasAction)

        contextMenu.exec_(self.mapToGlobal(point))
