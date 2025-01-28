from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QTextEdit, QSizePolicy, QGridLayout, QLabel
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QInputDialog
from PyQt5.QtCore import QDate
from src.utils import MultiSelectComboBox

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Account Book")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_obj = {}
        self.tab_obj["Income"] = TabCreator(self, "Income", ["Date", "Category", "Method", "Description", "Amount", "Delete"])
        self.tab_obj["Expenses"] = TabCreator(self, "Expenses", ["Date", "Category", "Method", "Description", "Amount", "Delete"])
        self.tab_obj["Savings"] = TabCreator(self, "Savings", ["Date", "Category", "Method", "Description", "Amount", "Delete"])

        self.tabs.addTab(self.tab_obj["Income"].tab, "Income")
        self.tabs.addTab(self.tab_obj["Expenses"].tab, "Expenses")
        self.tabs.addTab(self.tab_obj["Savings"].tab, "Savings")

        # self.category_obj = {}
        # self.method_obj = {}
        # for tab in self.tab_obj.keys():
        #     self.category_obj[tab] = EditWindow(self, tab, "Category")
        #     self.method_obj[tab] = EditWindow(self, tab, "Method")

class EditWindow():
    def __init__(self, parent, tab_name, name) -> None:
        self.parent = parent
        self.tab_name = tab_name
        self.name = name
        self.dialog = QDialog(self.parent)

    def edit_view(self):
        self.dialog = QDialog(self.parent)
        self.dialog.setWindowTitle(f"Edit {self.tab_name} {self.name}")
        self.dialog.setGeometry(100, 100, 300, 400)

        self.layout = QVBoxLayout()

        self.item_list = QListWidget()
        self.item_list.setDragDropMode(QListWidget.InternalMove)  # Enable drag-and-drop
        self.layout.addWidget(self.item_list)

        self.add_button = QPushButton("Add")
        self.delete_button = QPushButton("Delete")
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.layout.addLayout(self.button_layout)

        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.layout.addWidget(self.dialog_buttons)

        self.dialog.setLayout(self.layout)  

    def add_item(self):
        text, ok = QInputDialog.getText(self.parent, f"Add {self.name}", f"Enter New {self.name}:")
        if ok and text:
            self.item_list.addItem(text)

    def delete_item(self):
        for item in self.item_list.selectedItems():
            self.item_list.takeItem(self.item_list.row(item))        

class TabCreator():
    def __init__(self, parent, name, header) -> None:
        self.name = name
        self.header = header
        self.parent = parent

        self.create_tab()

        self.category_edit = EditWindow(parent, name, "Category")
        self.method_edit = EditWindow(parent, name, "Method")

    def create_tab(self):
        self.tab = QWidget()
        self.layout = QGridLayout()
        
        # Date input, load, save
        today = QDate.currentDate().toString("yyyy-MM-dd")
        year = today.split("-")[0]
        month = today.split("-")[1]
        day = today.split("-")[2]

        self.year_input = QLineEdit()
        self.year_input.setText(year)
        self.year_input.setPlaceholderText("YYYY")

        self.month_input = QLineEdit()      
        self.month_input.setText(month)
        self.month_input.setPlaceholderText("MM")

        self.day_input = QLineEdit()
        self.day_input.setText(day)
        self.day_input.setPlaceholderText("DD")

        self.save_button = QPushButton("Save to File")
        self.save_button.setEnabled(False)

        self.load_button = QPushButton("Load by Date")
        self.load_button.setEnabled(True)

        self.layout.addWidget(QLabel('Date:'), 0, 0, 1, 1)
        self.layout.addWidget(self.year_input, 0, 1, 1, 2)
        self.layout.addWidget(self.month_input, 0, 3, 1, 2)
        self.layout.addWidget(self.day_input, 0, 5, 1, 2)
        self.layout.addWidget(self.load_button, 0, 7, 1, 1)
        self.layout.addWidget(self.save_button, 0, 8, 1, 1)
        
        # Category
        self.category_input = MultiSelectComboBox()
        self.edit_categories_button = QPushButton("Edit Categories")        
        self.layout.addWidget(QLabel('Category:'), 1, 0, 1, 1)
        self.layout.addWidget(self.category_input, 1, 1, 1, 7)
        self.layout.addWidget(self.edit_categories_button, 1, 8, 1, 1)

        # Method
        self.method_input = QComboBox()
        self.edit_methods_button = QPushButton("Edit Methods")        
        self.layout.addWidget(QLabel('Method:'), 2, 0, 1, 1)
        self.layout.addWidget(self.method_input, 2, 1, 1, 7)
        self.layout.addWidget(self.edit_methods_button, 2, 8, 1, 1)        

        # Details
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(f"Enter {self.name.lower()} description")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.layout.addWidget(QLabel('Details:'), 3, 0, 1, 1)
        self.layout.addWidget(self.description_input, 3, 1, 1, 4) 
        self.layout.addWidget(self.amount_input, 3, 5, 1, 4) 

        # Add
        self.add_button = QPushButton(f"Add {self.name}")
        self.add_button.setEnabled(False)
        self.layout.addWidget(self.add_button, 4, 0, 1, 8)

        # Undo
        self.undo_button = QPushButton(f"Undo Deleted Row")
        self.undo_button.setEnabled(False)
        self.layout.addWidget(self.undo_button, 4, 8, 1, 1)        

        # Table
        self.table = QTableWidget(0, len(self.header))
        self.table.setHorizontalHeaderLabels(self.header)
        self.layout.addWidget(self.table, 5, 0, 8, 9)        

        # Log
        self.log_text = QTextEdit(self.parent)
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("Log messages are displayed here...")
        self.layout.addWidget(self.log_text, 13, 0, 1, 9)            

        self.layout.setRowStretch(5, 8)
        self.layout.setRowStretch(13, 1)

        self.tab.setLayout(self.layout)