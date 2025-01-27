from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QPushButton

def mark_table_modified(table, save_button, load_button):
    """
    Marks the table as modified and updates the state of Save and Load buttons.

    Args:
        table (QTableWidget): The table widget being modified.
        save_button (QPushButton): The Save button to enable.
        load_button (QPushButton): The Load button to disable.
    """
    table.modified = True
    save_button.setEnabled(True)
    load_button.setEnabled(False)

def toggle_add_button(description_input, amount_input, add_button):
    """
    Enables or disables the Add button based on the validity of input fields.

    Args:
        description_input (QLineEdit): The description input field.
        amount_input (QLineEdit): The amount input field.
        add_button (QPushButton): The Add button to toggle.
    """
    if description_input.text() and amount_input.text().isdigit():
        add_button.setEnabled(True)
    else:
        add_button.setEnabled(False)

def append_log(log_text, message):
    """로그 창에 메시지 추가"""
    log_text.append(message)  # 메시지 추가
    log_text.ensureCursorVisible()  # 자동 스크롤 
