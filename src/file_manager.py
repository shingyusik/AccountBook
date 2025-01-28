import os
import json
import csv
from src.utils import append_log
from PyQt5.QtWidgets import QMessageBox

def load_from_json(parent, path):
    if os.path.exists(path):
        try:
            with open(path, "r") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
                else:
                    raise ValueError("Invalid format.")
        except (json.JSONDecodeError, IOError):
            QMessageBox.warning(parent, "Error", f"Failed to load Json file in '{path}'. Resetting to default.")
            return {}
    return {}    

def save_to_json(parent, data, path, log):
    try:
        with open(path, "w") as file:
            json.dump(data, file, indent=4)
        append_log(log, f"{path} saved successfully!")
    except IOError:
        QMessageBox.critical(parent, "Error", f"Failed to save Json file in '{path}'.")    

def load_from_csv(parent, tab_name, date, log) -> None:
    year, month = date.split("-")[:2]
    directory = os.path.join("Result", year)
    file_name = f"{month}_{tab_name}.csv"
    path = os.path.join(directory, file_name)

    if not os.path.exists(path):
        append_log(log, "There is no file to load")
        return []

    try:
        with open(path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)     
            append_log(log, f"Data successfully loaded from '{path}'")
            return rows
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to load file: {e}")

def save_to_csv(parent, tab_name, date, table, log) -> None:
    year, month = date.split("-")[:2]
    directory = os.path.join("Result", year)
    os.makedirs(directory, exist_ok=True)

    file_name = f"{month}_{tab_name}.csv"
    path = os.path.join(directory, file_name)

    try:
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Write headers
            headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount()-1)]
            writer.writerow(headers)

            # Write rows
            for row in range(table.rowCount()):
                values = [
                    table.item(row, col).text() if table.item(row, col) else ""
                    for col in range(table.columnCount()-1)
                ]
                writer.writerow(values)

        append_log(log, f"Data successfully saved to '{path}'")
    except Exception as e:
        QMessageBox.critical(parent, "Error", f"Failed to save file: {e}")        