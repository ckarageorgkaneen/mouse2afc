import sys
import os
import types
import enum

from AnyQt.QtWidgets import QMainWindow
from AnyQt.QtWidgets import QApplication
from AnyQt.QtWidgets import QHeaderView
from AnyQt.QtWidgets import QTableWidget
from AnyQt.QtWidgets import QTableWidgetItem
from AnyQt.QtWidgets import QComboBox
from AnyQt.QtWidgets import QCheckBox
from AnyQt.QtWidgets import QAbstractSpinBox
from AnyQt.QtWidgets import QLineEdit
from AnyQt.QtWidgets import QTextEdit
from AnyQt.QtWidgets import QDialog
from AnyQt.QtWidgets import QDialogButtonBox
from AnyQt.QtWidgets import QLabel
from AnyQt.QtWidgets import QVBoxLayout
from AnyQt import uic


def fullpath(file):
    return os.path.join(os.path.dirname(__file__), file)


class AttrDict(dict):

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    @staticmethod
    def from_nested_dict(data):
        if not isinstance(data, dict):
            return data
        else:
            return AttrDict({
                key: AttrDict.from_nested_dict(data[key])
                for key in data})


class TaskParametersGUITable:

    def __init__(self, headers, **columns):
        assert len(headers) == len(columns)
        self.headers = headers
        self.columns = AttrDict.from_nested_dict(columns)


class TaskParametersGUIConfirmDialog(QDialog):

    def __init__(self, parent, label):
        super().__init__(parent)
        self.setWindowTitle('Confirmation')
        q_button = QDialogButtonBox.Yes | QDialogButtonBox.No
        self.buttonBox = QDialogButtonBox(q_button)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        message = QLabel(label)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class TaskParametersGUI(QMainWindow):

    _file = fullpath('task_parameters.ui')

    def __init__(self, task_parameters):
        super().__init__()
        uic.loadUi(self._file, self)
        self._buttonBox_accepted = False
        self._task_parameters = task_parameters
        self.actionReload_defaults.triggered.connect(
            self._load_task_parameters)
        self.buttonBox.accepted.connect(self._button_accepted_callback)
        self.buttonBox.rejected.connect(self.close)
        self._load_task_parameters()
        self.show()

    def closeEvent(self, event):
        confirmation_dialog = TaskParametersGUIConfirmDialog(
            self, "Are you sure you want to exit?")
        if not self._buttonBox_accepted and not confirmation_dialog.exec_():
            event.ignore()

    def _button_accepted_callback(self):
        confirmation_dialog = TaskParametersGUIConfirmDialog(
            self, "Proceed with selected parameters?")
        if confirmation_dialog.exec_():
            self._update_task_parameters()
            self._buttonBox_accepted = True
            self.close()

    def _field(self, name):
        return getattr(self, name, None)

    def _load_task_parameter(self, parameter, value):
        ui_field = self._field(parameter)
        if ui_field is None:
            return
        if isinstance(ui_field, QTableWidget):
            assert isinstance(value, TaskParametersGUITable)
            ui_field.setEditTriggers(QTableWidget.NoEditTriggers)
            ui_field.setColumnCount(len(value.headers))
            ui_field.setRowCount(len(next(iter(value.columns.items()))[1]))
            ui_field.horizontalHeader().setSectionResizeMode(
                QHeaderView.Stretch)
            ui_field.setHorizontalHeaderLabels(value.headers)
            for col, key in enumerate(value.columns.keys()):
                for row, item in enumerate(value.columns[key]):
                    ui_field.setItem(row, col, QTableWidgetItem(str(item)))
            ui_field.resizeColumnsToContents()
            ui_field.resizeRowsToContents()
        elif isinstance(ui_field, QComboBox):
            assert isinstance(value, enum.Enum)
            ui_field.addItems(value.__class__.members())
            ui_field.setCurrentIndex(ui_field.findText(value.name))
        elif isinstance(ui_field, QCheckBox):
            ui_field.setChecked(bool(value))
        elif isinstance(ui_field, QAbstractSpinBox):
            ui_field.setValue(float(value))
        elif isinstance(ui_field, (QLineEdit, QTextEdit)):
            ui_field.setText(str(value))

    def _update_task_parameter(self, parameter, value):
        ui_field = self._field(parameter)
        if ui_field is None:
            return
        if isinstance(ui_field, QComboBox):
            assert isinstance(value, enum.Enum)
            enum_class = value.__class__
            enum_ = enum_class[ui_field.currentText()]
            self._task_parameters[parameter] = enum_
        elif isinstance(ui_field, QCheckBox):
            self._task_parameters[parameter] = ui_field.isChecked()
        elif isinstance(ui_field, QAbstractSpinBox):
            self._task_parameters[parameter] = ui_field.value()
        elif isinstance(ui_field, (QLineEdit, QTextEdit)):
            self._task_parameters[parameter] = ui_field.text()

    def _load_task_parameters(self):
        for param, val in self._task_parameters.items():
            self._load_task_parameter(param, val)

    def _update_task_parameters(self):
        for param, val in self._task_parameters.items():
            self._update_task_parameter(param, val)


class TaskParameters:

    _default_file = fullpath('config.py')

    def __init__(self, file_=None, open_gui=True):
        self._file = file_ or self._default_file
        self.task_parameters = None
        self._load()
        if open_gui:
            app = QApplication(sys.argv)
            self.GUI = TaskParametersGUI(self.task_parameters)
            app.exec_()
        self.task_parameters = AttrDict(**self.task_parameters)

    def _load(self):
        import importlib.util
        base_filename = os.path.basename(self._file)
        module_name = os.path.splitext(base_filename)[0]
        spec = importlib.util.spec_from_file_location(
            module_name, self._file)
        task_parameters = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(task_parameters)
        self.task_parameters = {}
        for k, v in vars(task_parameters).items():
            if getattr(task_parameters, k, object()) is v and \
                    not isinstance(v, types.ModuleType) and \
                    not k.startswith('__'):
                self.task_parameters[k] = v
