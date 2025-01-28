from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QPushButton

class Table:
    def __init__(self, parent, table) -> None:
        self.parent = parent
        self.table = table
        self.is_loaded = False
        self.is_cell_changed = False
        self.is_inserted = False
        self.is_deleted = False
        self.deleted_rows_stack = []

    def reset(self, rows: list):
        self.clear()
        for row in rows[1:]:
            if row:
                self.add_row(row[0], row[1], row[2], row[3], row[4])

    def clear(self):
        self.table.clearContents()
        self.table.setRowCount(0)
        self.is_loaded = False
        self.is_cell_changed = False
        self.is_inserted = False
        self.is_deleted = False        
        self.deleted_rows_stack = []

    def add_row(self, date_input, category, method, description, amount):
        date = date_input
        input_year, input_month = date.split("-")[:2]

        # Validate against table data
        for row in range(self.table.rowCount()):
            row_date = self.table.item(row, 0).text()
            table_year, table_month = row_date.split("-")[:2]
            if input_year != table_year or input_month != table_month:
                QMessageBox.warning(self, "Date Mismatch", "The year and month of the entry must match the table data.")
                return

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(date))
        self.table.setItem(row_position, 1, QTableWidgetItem(", ".join(category) if type(category) is list else category))
        self.table.setItem(row_position, 2, QTableWidgetItem(method))
        self.table.setItem(row_position, 3, QTableWidgetItem(description))
        self.table.setItem(row_position, 4, QTableWidgetItem(amount))
        self.add_delete_button(row_position)
        self.is_inserted = True

    def add_delete_button(self, row):
        button = QPushButton("-")
        button.clicked.connect(lambda: self.delete_row(row))
        self.table.setCellWidget(row, 5, button)        

    def delete_row(self, row):
        deleted_row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(6)]
        self.deleted_rows_stack.append((row, deleted_row_data))
        self.table.removeRow(row)
        for i in range(self.table.rowCount()):
            self.add_delete_button(i)
        self.is_deleted = True
        self.parent.check_button_enable(self)
        self.parent.debug_print(self)

    def undo_delete(self):
        if self.deleted_rows_stack:
            row, row_data = self.deleted_rows_stack.pop()

            self.table.insertRow(row)
            for col, data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(data))
            self.add_delete_button(row)

            for i in range(self.table.rowCount()):
                self.add_delete_button(i)

            self.is_deleted = True if self.deleted_rows_stack else False