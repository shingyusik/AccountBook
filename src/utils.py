from PyQt5.QtWidgets import QComboBox, QListWidget, QListWidgetItem, QCheckBox

class AddClickError(Exception):
    pass

class DateError(Exception):
    pass

class LoadError(Exception):
    pass

class SaveError(Exception):
    pass

class AddRowError(Exception):
    pass

class MultiSelectComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.list_widget = QListWidget()
        self.items = []
        self.selected_items = []

        self.setModel(self.list_widget.model())
        self.setView(self.list_widget)

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    def add_item(self, text):
        list_item = QListWidgetItem()
        checkbox = QCheckBox(text)
        checkbox.stateChanged.connect(self.update_selection)
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, checkbox)

    def update_selection(self):
        self.selected_items = [
            self.list_widget.itemWidget(self.list_widget.item(i)).text()
            for i in range(self.list_widget.count())
            if self.list_widget.itemWidget(self.list_widget.item(i)).isChecked()
        ]
        self.setEditText(", ".join(self.selected_items))

def append_log(log_text, message):
    log_text.append(message)
    log_text.ensureCursorVisible()
