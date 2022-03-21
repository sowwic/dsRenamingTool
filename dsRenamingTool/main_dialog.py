import os
import pymel.core as pm
import pymel.api as pma
from PySide2 import QtWidgets

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import getCppPointer

from dsRenamingTool.loggingFn import Logger
from dsRenamingTool.template import Template
from dsRenamingTool.template_widget import QTemplateWidget


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

        self.update_available_templates()

    def create_actions(self):
        # Menubar
        pass
        # self.menuBar = QtWidgets.QMenuBar(self)
        # editMenu = self.menuBar.addMenu("&Edit")

        # Actions
        # self.editSuffixAliasesAction = QtWidgets.QAction("Suffix aliases", self)

        # Populate menubar
        # editMenu.addAction(self.editSuffixAliasesAction)

    def create_widgets(self):
        self.templates_combobox = QtWidgets.QComboBox()
        self.templates_stack = QtWidgets.QStackedWidget()
        self.rename_button = QtWidgets.QPushButton("Rename")
        self.close_button = QtWidgets.QPushButton("Close")

    def create_layouts(self):
        template_choose_layout = QtWidgets.QFormLayout()
        template_choose_layout.addRow("Template:", self.templates_combobox)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.rename_button)
        buttons_layout.addWidget(self.close_button)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(template_choose_layout)
        self.main_layout.addWidget(self.templates_stack)
        self.main_layout.addStretch()
        self.main_layout.addLayout(buttons_layout)

    def create_connections(self):
        self.rename_button.clicked.connect(self.rename_selected)
        self.close_button.clicked.connect(self.hide)

    def rename_selected(self):
        template_widget = self.templates_stack.currentWidget()  # type: QTemplateWidget
        if not template_widget:
            return
        try:
            for node in pm.selected():
                tk_map = {"side": "temp",
                          "name": "temp",
                          "suffix": "temp"}
                new_name = (template_widget.template.generate_name(tk_map, node=node))
            node.rename(new_name)
            for node in pm.selected():
                tk_map = template_widget.get_token_value_map()
                new_name = (template_widget.template.generate_name(tk_map, node=node))
                node.rename(new_name)
        except Exception:
            Logger.exception("Renaming exception")

    def create_new_template_from_current(self):
        current_template = self.templates_combobox.currentData()  # type: Template
        new_template = Template(current_template.file_path)
        self.update_available_templates()
        self.templates_combobox.addItem("{}(copy)".format(new_template.name))

    def _clear_templates_stack(self):
        while self.templates_stack.count():
            widget_to_delete = self.templates_stack.widget(0)  # type: QTemplateWidget
            self.templates_stack.removeWidget(widget_to_delete)
            widget_to_delete.deleteLater()

    def update_available_templates(self):
        self._clear_templates_stack()
        self.templates_combobox.clear()
        templates = Template.get_templates()
        for temp in templates:
            self.templates_combobox.addItem(temp.name, temp)
            template_widget = QTemplateWidget(temp)
            self.templates_stack.addWidget(template_widget)
