from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QDialogButtonBox, QInputDialog, QMessageBox, QComboBox, QListWidgetItem, QCheckBox
import os
import json
import log as Log

class CategoryManager:
    CATEGORY_FILE = "categories.json"

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.categories = self.load_categories()
        # self.save_categories_callback = self.save_categories()

    def edit_categories(self, category_input, log):
        dialog = QDialog(self.parent)
        dialog.setWindowTitle(f"Edit {self.name} Categories")
        dialog.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        category_list = QListWidget()
        category_list.addItems(self.categories.get(self.name, []))
        category_list.setDragDropMode(QListWidget.InternalMove)  # Enable drag-and-drop
        layout.addWidget(category_list)

        add_button = QPushButton("Add")
        delete_button = QPushButton("Delete")
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(dialog_buttons)

        dialog.setLayout(layout)

        def add_category():
            text, ok = QInputDialog.getText(self.parent, "Add Category", "Enter new category:")
            if ok and text:
                category_list.addItem(text)

        def delete_category():
            for item in category_list.selectedItems():
                category_list.takeItem(category_list.row(item))

        add_button.clicked.connect(add_category)
        delete_button.clicked.connect(delete_category)

        def apply_changes():
            updated_categories = [category_list.item(i).text() for i in range(category_list.count())]
            self.categories[self.name] = updated_categories
            category_input.clear()
            category_input.add_items(updated_categories)
            self.save_categories(log)
            dialog.accept()

        dialog_buttons.accepted.connect(apply_changes)
        dialog_buttons.rejected.connect(dialog.reject)

        dialog.exec_()

    def load_categories(self):
        if os.path.exists(self.CATEGORY_FILE):
            try:
                with open(self.CATEGORY_FILE, "r") as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        return data
                    else:
                        raise ValueError("Invalid format in categories file.")
            except (json.JSONDecodeError, IOError):
                QMessageBox.warning(self.parent, "Error", "Failed to load categories. Resetting to default.")
                return {}
        return {}

    def save_categories(self, log):
        try:
            with open(self.CATEGORY_FILE, "w") as file:
                json.dump(self.categories, file, indent=4)
            Log.append_log(log, "Categories saved successfully!")
            # QMessageBox.information(self.parent, "Success", "Categories saved successfully!")
        except IOError:
            QMessageBox.critical(self.parent, "Error", "Failed to save categories.")


class MultiSelectComboBox(QComboBox):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.list_widget = QListWidget()
        self.items = items
        self.selected_items = []

        self.add_items(self.items)

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