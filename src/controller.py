from PyQt5.QtWidgets import QComboBox, QListWidget, QListWidgetItem, QCheckBox, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QState, QStateMachine, pyqtSignal, QObject
from src.file_manager import load_from_json, save_to_json, load_from_csv, save_to_csv
from src.table import Table
from src.utils import append_log

class MainController():
    def __init__(self, view) -> None:
        self.view = view

        self.income_tab = self.view.tab_obj["Income"]
        self.expense_tab = self.view.tab_obj["Expenses"]
        self.saving_tab = self.view.tab_obj["Savings"]

        TabController(view, self.income_tab)
        TabController(view, self.expense_tab)
        TabController(view, self.saving_tab)

class TabController(QObject):
    CATEGORY_FILE = "categories.json"
    METHOD_FILE = "methods.json"

    load_button_enabled_signal = pyqtSignal()
    save_button_enabled_signal = pyqtSignal()
    add_button_enabled_signal = pyqtSignal()
    undo_button_enabled_signal = pyqtSignal()

    load_button_disabled_signal = pyqtSignal()
    save_button_disabled_signal = pyqtSignal()
    add_button_disabled_signal = pyqtSignal()
    undo_button_disabled_signal = pyqtSignal()

    def __init__(self, view, tab):
        super(TabController, self).__init__()
        self.view = view
        self.tab = tab
        self.name = tab.name

        self.categories = load_from_json(self.view, self.CATEGORY_FILE)
        self.methods = load_from_json(self.view, self.METHOD_FILE)

        # Set category items
        self.tab.category_input.add_items(self.categories.get(self.name, ["Category1", "Category2", "Category3", "Other"]))

        # Set method items
        self.tab.method_input.addItems(self.methods.get(self.name, ["Account1", "Account2", "Cash", "Other"]))

        # Connect category edit button
        self.tab.edit_categories_button.clicked.connect(lambda: self.run_edit(self.tab.category_edit, self.CATEGORY_FILE, self.tab.category_input))

        # Connect method edit button
        self.tab.edit_methods_button.clicked.connect(lambda: self.run_edit(self.tab.method_edit, self.METHOD_FILE, self.tab.method_input, self.tab.log_text))

        self.table_obj = Table(self, self.tab.table)
        
        # Connect load button
        self.tab.load_button.clicked.connect(self.handle_load_click)

        # Connect save button
        self.tab.save_button.clicked.connect(self.handle_save_click)

        # Connect add button
        self.tab.add_button.clicked.connect(self.handle_add_click)
        
        # Connect undo button
        self.tab.undo_button.clicked.connect(self.handle_undo_click)

        # Connect table changes
        self.tab.table.cellChanged.connect(self.on_cell_changed)

        # # Init state machines
        # self.state_machines = {}
        # for tab_name in self.view.tab_obj.keys():
        #     self.state_machines[tab_name] = {}
        #     self.state_machines[tab_name]['load'] = QStateMachine()
        #     self.state_machines[tab_name]['save'] = QStateMachine()
        #     self.state_machines[tab_name]['add'] = QStateMachine()
        #     self.state_machines[tab_name]['undo'] = QStateMachine()

        # self.init_state_machines(self.income_tab, self.state_machines["Income"])
        # self.init_state_machines(self.expense_tab, self.state_machines["Expenses"])
        # self.init_state_machines(self.saving_tab, self.state_machines["Savings"])

    def run_edit(self, obj, path, item_input):
        obj.edit_view()
        items = load_from_json(self.view, path)
        obj.item_list.addItems(items.get(obj.tab_name, []))  

        obj.add_button.clicked.connect(obj.add_item)
        obj.delete_button.clicked.connect(obj.delete_item)

        def apply_changes():
            updated_items = [obj.item_list.item(i).text() for i in range(obj.item_list.count())]
            items[obj.tab_name] = updated_items
            item_input.clear()
            if obj.name == "Category":
                item_input.add_items(updated_items)
            else:
                item_input.addItems(updated_items)
            save_to_json(self.view, items, path, self.tab.log_text)
            obj.dialog.accept()

        obj.dialog_buttons.accepted.connect(apply_changes)
        obj.dialog_buttons.rejected.connect(obj.dialog.reject)      

        obj.dialog.exec_()        

    def handle_load_click(self):
        date = self.get_date()
        if date:
            table_list = load_from_csv(self.view, self.name, date, self.tab.log_text)
            self.table_obj.reset(table_list)
            self.table_obj.is_loaded = True
            self.table_obj.is_cell_changed = False
            self.table_obj.is_inserted = False
            self.clear_selection()
            self.check_button_enable()
        else:
            QMessageBox.warning(self.view, "Error", "You must fill in all the date fields.")
        self.debug_print()

    def handle_save_click(self):
        date = self.get_date()
        if date:
            save_to_csv(self.view, self.name, date, self.table_obj, self.tab.log_text)
            self.table_obj.clear()
            self.clear_selection()
            self.check_button_enable()
        else:
            QMessageBox.warning(self.view, "Error", "You must fill in all the date fields.")
        self.debug_print()

    def handle_add_click(self):
        date = self.get_date()
        category = self.tab.category_input.selected_items
        method = self.tab.method_input.currentText()
        description = self.tab.description_input.text()
        amount = self.tab.amount_input.text()

        if date and category and method and description and amount.isdigit():
            self.table_obj.add_row(date, category, method, description, amount)
            self.clear_selection()
            self.check_button_enable()
            append_log(self.tab.log_text, f"The input values have been added to the table: [{date}, {category}, {method}, {description}, {amount}]")
        else:
            QMessageBox.warning(self.view, "Error", "You must fill in all the fields.")
        self.debug_print()

    def handle_undo_click(self):        
        self.table_obje.undo_delete()
        self.check_button_enable()
        append_log(self.tab.log_text, "The deleted row has been re-added to the table.")
        self.debug_print()

    def get_date(self):
        is_valid = self.tab.year_input.text().isdigit() and self.tab.month_input.text().isdigit() and self.tab.day_input.text().isdigit()
        date = f"{self.tab.year_input.text()}-{self.tab.month_input.text()}-{self.tab.day_input.text()}" if is_valid else ""
        return date
    
    def clear_selection(self):
        for i in range(self.tab.category_input.list_widget.count()):
            checkbox = self.tab.category_input.list_widget.itemWidget(self.tab.category_input.list_widget.item(i))
            checkbox.setChecked(False)
        self.tab.category_input.selected_items = []
        self.tab.category_input.setEditText("")

    def on_cell_changed(self):
        self.table_obj.is_cell_changed = True
        self.check_button_enable()

    def check_button_enable(self):
        if self.load_button_condition():
            self.load_button_enabled_signal.emit()
        else:
            self.load_button_disabled_signal.emit()

        if self.save_button_condition():
            self.save_button_enabled_signal.emit()
        else:
            self.save_button_disabled_signal.emit()

        if self.add_button_condition():
            self.add_button_enabled_signal.emit()
        else:
            self.add_button_disabled_signal.emit()

        if self.undo_button_condition():
            self.undo_button_enabled_signal.emit()
        else:
            self.undo_button_disabled_signal.emit()

    def debug_print(self):
        print("Table State:")
        print(f"1. Loaded: {self.table_obj.is_loaded}")
        print(f"2. Cell changed: {self.table_obj.is_cell_changed}")
        print(f"3. Inserted: {self.table_obj.is_inserted}")
        print(f"4. Deleted: {self.table_obj.is_deleted}")
        print()

    def load_button_condition(self):
        return not self.table_obj.is_cell_changed and not self.table_obj.is_inserted and not self.table_obj.is_deleted

    def save_button_condition(self):
        return self.table_obj.is_cell_changed or self.table_obj.is_inserted or self.table_obj.is_deleted

    def add_button_condition(self):
        return self.table_obj.is_loaded

    def undo_button_condition(self):
        return self.table_obj.is_deleted


# class MainController(QObject):
#     CATEGORY_FILE = "categories.json"
#     METHOD_FILE = "methods.json"

#     load_button_enabled_signal = pyqtSignal()
#     save_button_enabled_signal = pyqtSignal()
#     add_button_enabled_signal = pyqtSignal()
#     undo_button_enabled_signal = pyqtSignal()

#     load_button_disabled_signal = pyqtSignal()
#     save_button_disabled_signal = pyqtSignal()
#     add_button_disabled_signal = pyqtSignal()
#     undo_button_disabled_signal = pyqtSignal()

#     def __init__(self, view):
#         super(MainController, self).__init__()
#         self.view = view

#         self.income_tab = self.view.tab_obj["Income"]
#         self.expense_tab = self.view.tab_obj["Expenses"]
#         self.saving_tab = self.view.tab_obj["Savings"]

#         self.categories = load_from_json(self.view, self.CATEGORY_FILE)
#         self.methods = load_from_json(self.view, self.METHOD_FILE)

#         # Set category items
#         self.income_tab.category_input.add_items(self.categories.get("Income", ["Salary", "Business", "Investment", "Other"]))
#         self.expense_tab.category_input.add_items(self.categories.get("Expenses", ["Food", "Transport", "Utilities", "Entertainment", "Other"]))
#         self.saving_tab.category_input.add_items(self.categories.get("Savings", ["Savings Goal", "Monthly Deposit", "Other"]))

#         # Set method items
#         self.income_tab.method_input.addItems(self.methods.get("Income", ["Account1", "Account2", "Cash", "Other"]))
#         self.expense_tab.method_input.addItems(self.methods.get("Expenses", ["Account1", "Account2", "Cash", "Other"]))
#         self.saving_tab.method_input.addItems(self.methods.get("Savings", ["Account1", "Account2", "Cash", "Other"]))

#         # Connect edit button
#         self.income_tab.edit_categories_button.clicked.connect(lambda: self.run_edit(self.view.category_obj["Income"], self.CATEGORY_FILE, self.income_tab.category_input, self.income_tab.log_text))
#         self.expense_tab.edit_categories_button.clicked.connect(lambda: self.run_edit(self.view.category_obj["Expenses"], self.CATEGORY_FILE, self.expense_tab.category_input, self.expense_tab.log_text))
#         self.saving_tab.edit_categories_button.clicked.connect(lambda: self.run_edit(self.view.category_obj["Savings"], self.CATEGORY_FILE, self.saving_tab.category_input, self.saving_tab.log_text))

#         self.income_tab.edit_methods_button.clicked.connect(lambda: self.run_edit(self.view.method_obj["Income"], self.METHOD_FILE, self.income_tab.method_input, self.income_tab.log_text))
#         self.expense_tab.edit_methods_button.clicked.connect(lambda: self.run_edit(self.view.method_obj["Expenses"], self.METHOD_FILE, self.expense_tab.method_input, self.expense_tab.log_text))
#         self.saving_tab.edit_methods_button.clicked.connect(lambda: self.run_edit(self.view.method_obj["Savings"], self.METHOD_FILE, self.saving_tab.method_input, self.saving_tab.log_text))

#         self.income_table = Table(self, self.income_tab.table)
#         self.expense_table = Table(self, self.expense_tab.table)
#         self.saving_table = Table(self, self.saving_tab.table)
        
#         # Connect load button
#         self.income_tab.load_button.clicked.connect(lambda: self.handle_load_click(self.income_tab, self.income_table, "Income", self.income_tab.log_text))
#         self.expense_tab.load_button.clicked.connect(lambda: self.handle_load_click(self.expense_tab, self.expense_table, "Expenses", self.expense_tab.log_text))
#         self.saving_tab.load_button.clicked.connect(lambda: self.handle_load_click(self.saving_tab, self.saving_table, "Savings", self.saving_tab.log_text))

#         # Connect save button
#         self.income_tab.save_button.clicked.connect(lambda: self.handle_save_click(self.income_tab, self.income_table, "Income", self.income_tab.log_text))
#         self.expense_tab.save_button.clicked.connect(lambda: self.handle_save_click(self.expense_tab, self.expense_table, "Expenses", self.expense_tab.log_text))
#         self.saving_tab.save_button.clicked.connect(lambda: self.handle_save_click(self.saving_tab, self.saving_table, "Savings", self.saving_tab.log_text))     

#         # Connect add button
#         self.income_tab.add_button.clicked.connect(lambda: self.handle_add_click(self.income_tab, self.income_table, self.income_tab.log_text))
#         self.expense_tab.add_button.clicked.connect(lambda: self.handle_add_click(self.expense_tab, self.expense_table, self.expense_tab.log_text))
#         self.saving_tab.add_button.clicked.connect(lambda: self.handle_add_click(self.saving_tab, self.saving_table, self.saving_tab.log_text))
        
#         # Connect undo button
#         self.income_tab.undo_button.clicked.connect(lambda: self.handle_undo_click(self.income_table, self.income_tab.log_text))
#         self.expense_tab.undo_button.clicked.connect(lambda: self.handle_undo_click(self.expense_table, self.expense_tab.log_text))
#         self.saving_tab.undo_button.clicked.connect(lambda: self.handle_undo_click(self.saving_table, self.saving_tab.log_text))

#         # Connect table changes
#         self.income_table.table.cellChanged.connect(lambda: self.on_cell_changed(self.income_table))
#         self.expense_table.table.cellChanged.connect(lambda: self.on_cell_changed(self.expense_table))
#         self.saving_table.table.cellChanged.connect(lambda: self.on_cell_changed(self.saving_table))

#         # Init state machines
#         self.state_machines = {}
#         for tab_name in self.view.tab_obj.keys():
#             self.state_machines[tab_name] = {}
#             self.state_machines[tab_name]['load'] = QStateMachine()
#             self.state_machines[tab_name]['save'] = QStateMachine()
#             self.state_machines[tab_name]['add'] = QStateMachine()
#             self.state_machines[tab_name]['undo'] = QStateMachine()

#         self.init_state_machines(self.income_tab, self.state_machines["Income"])
#         self.init_state_machines(self.expense_tab, self.state_machines["Expenses"])
#         self.init_state_machines(self.saving_tab, self.state_machines["Savings"])

#     def run_edit(self, obj, path, item_input, log):
#         obj.edit_view()
#         items = load_from_json(self.view, path)
#         obj.item_list.addItems(items.get(obj.tab_name, []))  

#         obj.add_button.clicked.connect(obj.add_item)
#         obj.delete_button.clicked.connect(obj.delete_item)

#         def apply_changes():
#             updated_items = [obj.item_list.item(i).text() for i in range(obj.item_list.count())]
#             items[obj.tab_name] = updated_items
#             item_input.clear()
#             if obj.name == "Category":
#                 item_input.add_items(updated_items)
#             else:
#                 item_input.addItems(updated_items)
#             save_to_json(self.view, items, path, log)
#             obj.dialog.accept()

#         obj.dialog_buttons.accepted.connect(apply_changes)
#         obj.dialog_buttons.rejected.connect(obj.dialog.reject)      

#         obj.dialog.exec_()        

#     def handle_load_click(self, obj, table, tab_name, log):
#         date = self.get_date(obj)
#         if date:
#             table_list = load_from_csv(self.view, tab_name, date, log)
#             table.reset(table_list)
#             table.is_loaded = True
#             table.is_cell_changed = False
#             table.is_inserted = False
#             self.clear_selection(obj.category_input)
#             self.check_button_enable(table)
#         else:
#             QMessageBox.warning(self.view, "Error", "You must fill in all the date fields.")
#         self.debug_print(table)

#     def handle_save_click(self, obj, table, tab_name, log):
#         date = self.get_date(obj)
#         if date:
#             save_to_csv(self.view, tab_name, date, obj.table, log)
#             table.clear()
#             self.clear_selection(obj.category_input)
#             self.check_button_enable(table)
#         else:
#             QMessageBox.warning(self.view, "Error", "You must fill in all the date fields.")
#         self.debug_print(table)

#     def handle_add_click(self, obj, table, log):
#         date = self.get_date(obj)
#         category = obj.category_input.selected_items
#         method = obj.method_input.currentText()
#         description = obj.description_input.text()
#         amount = obj.amount_input.text()

#         if date and category and method and description and amount.isdigit():
#             table.add_row(date, category, method, description, amount)
#             self.clear_selection(obj.category_input)
#             self.check_button_enable(table)
#             append_log(log, f"The input values have been added to the table: [{date}, {category}, {method}, {description}, {amount}]")
#         else:
#             QMessageBox.warning(self.view, "Error", "You must fill in all the fields.")
#         self.debug_print(table)

#     def handle_undo_click(self, table, log):        
#         table.undo_delete()
#         self.check_button_enable(table)
#         append_log(log, "The deleted row has been re-added to the table.")
#         self.debug_print(table)

#     def get_date(self, obj):
#         is_valid = obj.year_input.text().isdigit() and obj.month_input.text().isdigit() and obj.day_input.text().isdigit()
#         date = f"{obj.year_input.text()}-{obj.month_input.text()}-{obj.day_input.text()}" if is_valid else ""
#         return date
    
#     def clear_selection(self, catetogies):
#         for i in range(catetogies.list_widget.count()):
#             checkbox = catetogies.list_widget.itemWidget(catetogies.list_widget.item(i))
#             checkbox.setChecked(False)
#         catetogies.selected_items = []
#         catetogies.setEditText("")

#     def on_cell_changed(self, table):
#         table.is_cell_changed = True
#         self.check_button_enable(table)

#     def check_button_enable(self, table):
#         if self.load_button_condition(table):
#             self.load_button_enabled_signal.emit()
#         else:
#             self.load_button_disabled_signal.emit()

#         if self.save_button_condition(table):
#             self.save_button_enabled_signal.emit()
#         else:
#             self.save_button_disabled_signal.emit()

#         if self.add_button_condition(table):
#             self.add_button_enabled_signal.emit()
#         else:
#             self.add_button_disabled_signal.emit()

#         if self.undo_button_condition(table):
#             self.undo_button_enabled_signal.emit()
#         else:
#             self.undo_button_disabled_signal.emit()

#     def debug_print(self, table):
#         print("Table State:")
#         print(f"1. Loaded: {table.is_loaded}")
#         print(f"2. Cell changed: {table.is_cell_changed}")
#         print(f"3. Inserted: {table.is_inserted}")
#         print(f"4. Deleted: {table.is_deleted}")
#         print()

#     def load_button_condition(self, table):
#         return not table.is_cell_changed and not table.is_inserted and not table.is_deleted

#     def save_button_condition(self, table):
#         return table.is_cell_changed or table.is_inserted or table.is_deleted

#     def add_button_condition(self, table):
#         return table.is_loaded

#     def undo_button_condition(self, table):
#         return table.is_deleted
    
#     def init_state_machines(self, obj, machine):
#         # 1. Load button state machine
#         load_active_state = QState()  # Load active state
#         load_inactive_state = QState()  # Load inactive state

#         # Load button property setting
#         load_active_state.assignProperty(obj.load_button, "enabled", True)
#         load_inactive_state.assignProperty(obj.load_button, "enabled", False)

#         # Load button state transition
#         load_active_state.addTransition(self.load_button_disabled_signal, load_inactive_state)
#         load_inactive_state.addTransition(self.load_button_enabled_signal, load_active_state)

#         # Add state
#         machine['load'].addState(load_active_state)
#         machine['load'].addState(load_inactive_state)
#         machine['load'].setInitialState(load_active_state)

#         # State machine start
#         machine['load'].start()

#         # 2. Save button state machine
#         save_active_state = QState()  # Save active state
#         save_inactive_state = QState()  # Save inactive state

#         # Save button property setting
#         save_active_state.assignProperty(obj.save_button, "enabled", True)
#         save_inactive_state.assignProperty(obj.save_button, "enabled", False)

#         # Save button state transition
#         save_active_state.addTransition(self.save_button_disabled_signal, save_inactive_state)
#         save_inactive_state.addTransition(self.save_button_enabled_signal, save_active_state)

#         # Add state
#         machine['save'].addState(save_active_state)
#         machine['save'].addState(save_inactive_state)
#         machine['save'].setInitialState(save_inactive_state)

#         # State machine start
#         machine['save'].start()

class StateMachine():
    def __init__(self) -> None:
        pass
