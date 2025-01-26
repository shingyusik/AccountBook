import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QTextEdit, QSizePolicy, QGridLayout, QLabel
from PyQt5.QtCore import QDate
from category_manager import CategoryManager, MultiSelectComboBox
from file_operations import handle_load_click, handle_save_click
from utils import mark_table_modified, toggle_add_button

class AccountBook(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Account Book")
        self.setGeometry(100, 100, 800, 600)

        self.manager = CategoryManager(self, None)
        self.categories = self.manager.load_categories()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.income_tab = self.create_tab("Income", ["Date", "Category", "Description", "Amount"], self.categories.get("Income", ["Salary", "Business", "Investment", "Other"]))
        self.expense_tab = self.create_tab("Expenses", ["Date", "Category", "Description", "Amount"], self.categories.get("Expenses", ["Food", "Transport", "Utilities", "Entertainment", "Other"]))
        self.savings_tab = self.create_tab("Savings", ["Date", "Category", "Description", "Amount"], self.categories.get("Savings", ["Savings Goal", "Monthly Deposit", "Other"]))

        self.tabs.addTab(self.income_tab["widget"], "Income")
        self.tabs.addTab(self.expense_tab["widget"], "Expenses")
        self.tabs.addTab(self.savings_tab["widget"], "Savings")

    def create_tab(self, name, headers, categories):
        tab = QWidget()
        layout = QGridLayout()
        
        # Date input, load, save
        today = QDate.currentDate().toString("yyyy-MM-dd")
        year = today.split("-")[0]
        month = today.split("-")[1]
        day = today.split("-")[2]

        year_input = QLineEdit()
        year_input.setText(year)
        year_input.setPlaceholderText("YYYY")

        month_input = QLineEdit()      
        month_input.setText(month)
        month_input.setPlaceholderText("MM")

        day_input = QLineEdit()
        day_input.setText(day)
        day_input.setPlaceholderText("DD")

        save_button = QPushButton("Save to File")
        save_button.setEnabled(False)

        load_button = QPushButton("Load by Date")
        load_button.setEnabled(True)

        layout.addWidget(QLabel('Date:'), 0, 0, 1, 1)
        layout.addWidget(year_input, 0, 1, 1, 2)
        layout.addWidget(month_input, 0, 3, 1, 2)
        layout.addWidget(day_input, 0, 5, 1, 2)
        layout.addWidget(load_button, 0, 7, 1, 1)
        layout.addWidget(save_button, 0, 8, 1, 1)

        date_input = f"{year}-{month}-{day}"
        
        # Category
        category_input = MultiSelectComboBox(categories)
        edit_categories_button = QPushButton("Edit Categories")        
        layout.addWidget(QLabel('Category:'), 1, 0, 1, 1)
        layout.addWidget(category_input, 1, 1, 1, 4)
        layout.addWidget(edit_categories_button, 1, 5, 1, 4)

        # Details
        description_input = QLineEdit()
        description_input.setPlaceholderText(f"Enter {name.lower()} description")
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("Enter amount")
        layout.addWidget(QLabel('Details:'), 2, 0, 1, 1)
        layout.addWidget(description_input, 2, 1, 1, 4) 
        layout.addWidget(amount_input, 2, 5, 1, 4) 

        # Add
        add_button = QPushButton(f"Add {name}")
        add_button.setEnabled(False)
        layout.addWidget(add_button, 3, 0, 1, 9)

        # Table
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        layout.addWidget(table, 4, 0, 8, 9)        

        # Log
        log_text = QTextEdit(self)
        log_text.setReadOnly(True)
        log_text.setPlaceholderText("Log messages are displayed here...")
        layout.addWidget(log_text, 12, 0, 1, 9)            

        layout.setRowStretch(4, 8)
        layout.setRowStretch(12, 1)

        tab.setLayout(layout)

        # Initialize modified flag
        table.modified = False

        # Ensure Add button is checked on startup for pre-filled inputs
        toggle_add_button(description_input, amount_input, add_button)

        # Track modifications to the table
        table.itemChanged.connect(lambda: mark_table_modified(table, save_button, load_button))

        # Connect save and load buttons to file operations
        load_button.clicked.connect(lambda: handle_load_click(description_input, amount_input, add_button, save_button, load_button, table, name, date_input, log_text))
        save_button.clicked.connect(lambda: handle_save_click(table, save_button, load_button, name, date_input, log_text))

        # Add utility functions
        description_input.textChanged.connect(lambda: toggle_add_button(description_input, amount_input, add_button))
        amount_input.textChanged.connect(lambda: toggle_add_button(description_input, amount_input, add_button))

        # Connect the Edit Categories button
        add_button.clicked.connect(lambda: self.add_entry(date_input, category_input, description_input, amount_input, table))
        edit_categories_button.clicked.connect(lambda: self.edit_categories(name, category_input, log_text))

        return {"widget": tab, "table": table}

    def add_entry(self, date_input, category_input, description_input, amount_input, table):
        date = date_input
        input_year, input_month = date.split("-")[:2]

        # Validate against table data
        for row in range(table.rowCount()):
            row_date = table.item(row, 0).text()
            table_year, table_month = row_date.split("-")[:2]
            if input_year != table_year or input_month != table_month:
                QMessageBox.warning(self, "Date Mismatch", "The year and month of the entry must match the table data.")
                return
                    
        category = category_input.selected_items
        description = description_input.text()
        amount = amount_input.text()

        if not description or not amount.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please provide valid inputs for all fields.")
            return

        row_position = table.rowCount()
        table.insertRow(row_position)
        table.setItem(row_position, 0, QTableWidgetItem(date))
        table.setItem(row_position, 1, QTableWidgetItem(", ".join(category)))
        table.setItem(row_position, 2, QTableWidgetItem(description))
        table.setItem(row_position, 3, QTableWidgetItem(amount))

        description_input.clear()
        amount_input.clear()
        table.modified = True

        self.clear_selection(category_input)

    def edit_categories(self, name, category_input, log):
        self.manager.name = name
        self.manager.edit_categories(category_input, log)

    def clear_selection(self, catetogies):
        for i in range(catetogies.list_widget.count()):
            checkbox = catetogies.list_widget.itemWidget(catetogies.list_widget.item(i))
            checkbox.setChecked(False)
        catetogies.selected_items = []
        catetogies.setEditText("")        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AccountBook()
    window.show()
    sys.exit(app.exec_())
