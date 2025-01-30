from PyQt5.QtWidgets import QComboBox, QListWidget, QListWidgetItem, QCheckBox, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import QState, QStateMachine, pyqtSignal, QObject
import sys
import re
from datetime import datetime
from src.file_manager import load_from_json, save_to_json, load_from_csv, save_to_csv
from src.table import Table
from src.utils import append_log
from src.utils import AddClickError, DateError, LoadError, SaveError, AddRowError

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
        self.table_obj = Table(self, self.tab.table)
        
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

        # Init state machines
        self.init_state_machines()

    def run_edit(self, obj, path, item_input):
        try:
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
                save_to_json(items, path, self.tab.log_text)
                obj.dialog.accept()

            obj.dialog_buttons.accepted.connect(apply_changes)
            obj.dialog_buttons.rejected.connect(obj.dialog.reject)      

            obj.dialog.exec_()
        except SaveError as e:
            QMessageBox.warning(self.view, "SaveError", f"{e}")
        except Exception as e:
            QMessageBox.warning(self.view, "Error", f"An unknown error occurred while executing edit {obj.name.lower()}: {e}")

    def handle_load_click(self):
        try:
            date = self.get_date()
            table_list = load_from_csv(self.name, date, self.tab.log_text)
            self.table_obj.reset(table_list)
            self.table_obj.is_loaded = True
            self.table_obj.is_cell_changed = False
            self.table_obj.is_inserted = False
            self.clear_selection()
            self.check_button_enable()
            self.debug_print()
        except AddRowError as e:
            QMessageBox.warning(self.view, "AddRowError", f"{e}")
            self.debug_print()            
        except LoadError as e:
            QMessageBox.warning(self.view, "LoadError", f"{e}")
            self.debug_print()                        
        except DateError as e:
            QMessageBox.warning(self.view, "DateError", f"{e}")
            self.debug_print()            
        except Exception as e:
            QMessageBox.warning(self.view, "Error", f"An unknown error occurred while executing load file: {e}")
            self.debug_print()

    def handle_save_click(self):
        try:
            date = self.get_date()
            save_to_csv(self.view, self.name, date, self.table_obj.table, self.tab.log_text)
            self.table_obj.clear()
            self.clear_selection()
            self.check_button_enable()
            self.debug_print()
        except SaveError as e:
            QMessageBox.warning(self.view, "SaveError", f"{e}")
            self.debug_print()            
        except DateError as e:
            QMessageBox.warning(self.view, "DateError", f"{e}")
            self.debug_print()               
        except Exception as e:
            QMessageBox.warning(self.view, "Error", f"An unknown error occurred while executing save file: {e}")
            self.debug_print()            

    def handle_add_click(self):
        try:
            date = self.get_date()
            category = self.tab.category_input.selected_items
            method = self.tab.method_input.currentText()
            description = self.tab.description_input.text()
            amount = self.tab.amount_input.text()

            if not re.fullmatch(r"[0-9+\-*/(). ]+", amount):
                raise AddClickError("The amount can only be entered as a number or an arithmetic expression.")

            try:
                amount = eval(amount, {"__builtins__": None}, {})
                amount = int(amount)
            except Exception:
                raise AddClickError("Error", "Invalid formula.")

            if date and category and method and description and amount:
                self.table_obj.add_row(date, category, method, description, amount)
                self.clear_selection()
                self.check_button_enable()
                append_log(self.tab.log_text, f"The input values have been added to the table: [{date}, {category}, {method}, {description}, {amount}]")
            else:
                raise AddClickError("You must fill in all the fields.")
            self.debug_print()
        except AddRowError as e:
            QMessageBox.warning(self.view, "AddRowError", f"{e}")
            self.debug_print()             
        except DateError as e:
            QMessageBox.warning(self.view, "DateError", f"{e}")
            self.debug_print()               
        except AddClickError as e:
            QMessageBox.warning(self.view, "AddClickError", f"{e}")
            self.debug_print()                         
        except Exception as e:
            QMessageBox.warning(self.view, "Error", f"An unknown error occurred while executing add entries: {e}")
            self.debug_print()             

    def handle_undo_click(self):
        try:
            self.table_obj.undo_delete()
            self.check_button_enable()
            append_log(self.tab.log_text, "The deleted row has been re-added to the table.")
            self.debug_print()
        except DateError as e:
            QMessageBox.warning(self.view, "Error", f"{e}")
            self.debug_print()               
        except Exception as e:
            QMessageBox.warning(self.view, "Error", f"An unknown error occurred while executing undo delete: {e}")
            self.debug_print()             

    def get_date(self):
        if not self.tab.year_input.text().isdigit() or not self.tab.month_input.text().isdigit() or not self.tab.day_input.text().isdigit():
            raise DateError("The date is not a number or is empty. Please check again.")
        
        try:
            year = int(self.tab.year_input.text())
            month = int(self.tab.month_input.text())
            day = int(self.tab.day_input.text())

            current_year = datetime.now().year
            
            if year > current_year:
                raise DateError("The entered year is greater than the current year.")
            
            datetime(year, month, day)

            date = f"{self.tab.year_input.text()}-{self.tab.month_input.text()}-{self.tab.day_input.text()}"
            return date
        except Exception as e:
            raise DateError(f"Invalid date: {e}")
    
    def clear_selection(self):
        for i in range(self.tab.category_input.list_widget.count()):
            checkbox = self.tab.category_input.list_widget.itemWidget(self.tab.category_input.list_widget.item(i))
            checkbox.setChecked(False)
        self.tab.category_input.selected_items = []
        self.tab.category_input.setEditText("")

    def on_cell_changed(self):
        self.table_obj.is_cell_changed = True
        self.check_button_enable()
        self.debug_print()

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
    
    def init_state_machines(self):
        self.load_state_machine = StateMachine(self.tab.load_button, self.load_button_enabled_signal, self.load_button_disabled_signal, True)
        self.save_state_machine = StateMachine(self.tab.save_button, self.save_button_enabled_signal, self.save_button_disabled_signal, False)
        self.add_state_machine = StateMachine(self.tab.add_button, self.add_button_enabled_signal, self.add_button_disabled_signal, False)
        self.undo_state_machine = StateMachine(self.tab.undo_button, self.undo_button_enabled_signal, self.undo_button_disabled_signal, False)

class StateMachine:
    def __init__(self, button, actice_signal, inactive_signal, init_state) -> None:
        self.state_machine = QStateMachine()
        
        # Button state machine
        active_state = QState()
        inactive_state = QState()

        # Button property setting
        active_state.assignProperty(button, "enabled", True)
        inactive_state.assignProperty(button, "enabled", False)

        # Button state transition
        active_state.addTransition(inactive_signal, inactive_state)
        inactive_state.addTransition(actice_signal, active_state)

        # Add state
        self.state_machine.addState(active_state)
        self.state_machine.addState(inactive_state)
        self.state_machine.setInitialState(active_state if init_state else inactive_state)

        # State machine start
        self.state_machine.start()
