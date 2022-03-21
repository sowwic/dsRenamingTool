from PySide2 import QtWidgets
from dsRenamingTool.template import Template
from collections import OrderedDict


class QTemplateWidget(QtWidgets.QWidget):
    def __init__(self, template, parent=None):
        # type: (Template, QtWidgets.QWidget) -> None
        super(QTemplateWidget, self).__init__(parent=parent)
        self.template = template
        self.token_lineedit_map = OrderedDict()

        # Base static widgets
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        # Dynamic token lineedits
        self.generate_token_widgets()

    def create_widgets(self):
        self.mapping_line_edit = QtWidgets.QLineEdit()
        self.mapping_line_edit.setText(self.template.mapping)
        self.index_start_spinbox = QtWidgets.QSpinBox()
        self.index_padding_spinbox = QtWidgets.QSpinBox()
        self.suffix_upper_checkout = QtWidgets.QCheckBox("Upper case suffix")

    def create_layouts(self):
        self.token_fields_layout = QtWidgets.QHBoxLayout()

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.mapping_line_edit)
        self.main_layout.addLayout(self.token_fields_layout)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)

    def create_connections(self):
        pass

    def get_token_value_map(self):
        tk_map = {}
        for tk_name, tk_lineedit in self.token_lineedit_map.items():
            tk_map[tk_name] = tk_lineedit.text()
        return tk_map

    def generate_token_widgets(self):
        for lineedit in self.token_lineedit_map.values():
            lineedit.deleteLater()
        for token_name in self.template.get_tokens():
            if token_name == "index":
                continue

            lineedit = QtWidgets.QLineEdit()
            lineedit.setPlaceholderText(token_name)
            self.token_lineedit_map[token_name] = lineedit
            self.token_fields_layout.addWidget(lineedit)
