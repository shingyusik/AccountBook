from PyQt5.QtWidgets import (
    QApplication, QComboBox, QMainWindow, QListWidget, QCheckBox, 
    QVBoxLayout, QWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QPushButton
)


class MultiSelectComboBox(QComboBox):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setEditable(False)
        self.list_widget = QListWidget()
        self.items = items
        self.selected_items = []

        # 아이템 추가
        for item in items:
            self.add_item(item)

        self.setModel(self.list_widget.model())
        self.setView(self.list_widget)

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Select ComboBox with Table")
        
        # Multi-Select ComboBox 생성
        items = ["Option 1", "Option 2", "Option 3", "Option 4"]
        self.combo_box = MultiSelectComboBox(items, self)
        
        # 테이블 생성
        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels(["Selected Items"])

        # 저장 버튼 생성
        self.save_button = QPushButton("Save to Table")
        self.save_button.clicked.connect(self.save_to_table)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.combo_box)
        layout.addWidget(self.save_button)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def save_to_table(self):
        # 선택된 항목을 테이블에 추가
        selected_items = self.combo_box.selected_items
        self.table.setRowCount(len(selected_items))
        for row, item in enumerate(selected_items):
            self.table.setItem(row, 0, QTableWidgetItem(item))


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
