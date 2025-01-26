import os
import csv
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
from utils import toggle_add_button
import log as Log

def save_to_file(table: QTableWidget, tab_name: str, date: str, log) -> None:
    """
    Saves the data from a QTableWidget to a CSV file in the specified directory.

    Args:
        table (QTableWidget): The table widget containing the data.
        file_name (str): The name of the file to save.
        directory (str): The directory where the file will be saved.
    """
    year, month = date.split("-")[:2]
    directory = os.path.join("Result", year)
    os.makedirs(directory, exist_ok=True)

    file_name = f"{month}_{tab_name}.csv"
    path = os.path.join(directory, file_name)

    try:
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Write headers
            headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
            writer.writerow(headers)

            # Write rows
            for row in range(table.rowCount()):
                values = [
                    table.item(row, col).text() if table.item(row, col) else ""
                    for col in range(table.columnCount())
                ]
                writer.writerow(values)

        Log.append_log(log, f"Data successfully saved to {path}")
        # QMessageBox.information(None, "File Saved", f"Data successfully saved to {path}")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to save file: {e}")

def load_from_file(table: QTableWidget, tab_name: str, date: str, log) -> None:
    """
    Loads data from a CSV file into a QTableWidget.

    Args:
        table (QTableWidget): The table widget where data will be loaded.
        file_name (str): The name of the file to load.
        directory (str): The directory containing the file.
    """
    year, month = date.split("-")[:2]
    directory = os.path.join("Result", year)
    file_name = f"{month}_{tab_name}.csv"
    path = os.path.join(directory, file_name)

    if not os.path.exists(path):
        table.setRowCount(0)  # Reset table for new input
        return

    try:
        with open(path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)

            if rows:
                # Clear existing table data
                table.setRowCount(0)

                # Set headers
                table.setColumnCount(len(rows[0]))
                table.setHorizontalHeaderLabels(rows[0])

                # Add rows
                for row_data in rows[1:]:
                    row_position = table.rowCount()
                    table.insertRow(row_position)
                    for col, value in enumerate(row_data):
                        table.setItem(row_position, col, QTableWidgetItem(value))

        Log.append_log(log, f"Data successfully loaded from {path}")
        # QMessageBox.information(None, "File Loaded", f"Data successfully loaded from {path}")
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load file: {e}")

def handle_load_click(description_input, amount_input, add_button, save_button, load_button, table, tab_name, date, log):
    if table.modified:
        save_to_file(table, tab_name, date, log)
    load_from_file(table, tab_name, date, log)
    description_input.setEnabled(True)
    amount_input.setEnabled(True)
    save_button.setEnabled(False)
    load_button.setEnabled(True)
    table.modified = False
    toggle_add_button(description_input, amount_input, add_button)

def handle_save_click(table, save_button, load_button, tab_name, date, log):
    save_to_file(table, tab_name, date, log)
    save_button.setEnabled(False)
    load_button.setEnabled(True)
    table.modified = False