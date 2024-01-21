from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt


class LookupDialog(QDialog):
    def __init__(self, data, column_names, parent=None):
        super(LookupDialog, self).__init__(parent)
        self.column_names = column_names
        self.filter_column = 1  # Default: filter based on the entire row
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Type to filter...")
        self.search_field.textChanged.connect(self.filter_table)
        self.search_field.returnPressed.connect(self.move_focus_to_table)

        self.table_widget = QTableWidget()
        self.table_widget.setFocusPolicy(Qt.StrongFocus)  # Set focus policy
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setColumnCount(len(column_names))
        self.table_widget.setHorizontalHeaderLabels(column_names)
        self.table_widget.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item):
                item_widget = QTableWidgetItem(str(value))
                item_widget.setFlags(
                    item_widget.flags() ^ Qt.ItemIsEditable)  # Make the cell read-only
                self.table_widget.setItem(row, col, item_widget)

        # Hide the vertical header (row numbers)
        self.table_widget.verticalHeader().setVisible(False)

        self.selected_item = None

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(self.search_field)
        layout.addWidget(self.table_widget)

        header = self.table_widget.horizontalHeader()
        # Set minimum width for each column header based on the length of
        # column names
        for col, column_name in enumerate(self.column_names):
            header.setSectionResizeMode(
                col, QHeaderView.Interactive)  # Allow manual resizing
            header.setMinimumSectionSize(
                self.fontMetrics().width(column_name) +
                20)  # Add some extra space
        # Calculate the total width of the columns
        total_column_width = sum(
            self.table_widget.columnWidth(col) for col in range(
                self.table_widget.columnCount()))

        # Set the width of the dialog
        self.setFixedWidth(total_column_width + 20)  # Adding some extra space
        # Calculate the total height of the rows
        total_row_height = sum(self.table_widget.rowHeight(row)
                               for row in range(self.table_widget.rowCount()))

        # Set the maximum height for the dialog (adjust this value as needed)
        max_dialog_height = 799

        # Set the height of the dialog, ensuring it doesn't exceed the maximum
        # height
        self.setFixedHeight(min(total_row_height + 200, max_dialog_height))
        # Set the height of the dialog, ensuring it doesn't exceed the maximum
        # height
        self.setFixedHeight(min(total_row_height + 200, max_dialog_height))

    def filter_table(self, text):
        text = text.lower()

        for row in range(self.table_widget.rowCount()):
            match_found = False
            for col in range(self.table_widget.columnCount()):
                item_text = str(
                    self.table_widget.item(
                        row, col).text()).lower()
                if text in item_text and (
                        self.filter_column == -
                        1 or col == self.filter_column):
                    match_found = True
                    break

            self.table_widget.setRowHidden(row, not match_found)

        visible_rows = [
            row for row in range(
                self.table_widget.rowCount()) if not self.table_widget.isRowHidden(row)]
        if visible_rows:
            first_visible_row = visible_rows[0]
            self.table_widget.selectRow(first_visible_row)

    def move_focus_to_table(self):
        if self.table_widget.currentRow() != -1:
            self.table_widget.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            current_row = self.table_widget.currentRow()
            while current_row < self.table_widget.rowCount() - 1:
                next_row = current_row + 1
                if not self.table_widget.isRowHidden(next_row):
                    self.table_widget.selectRow(next_row)
                    self.table_widget.setCurrentCell(next_row, 0)
                    break
                current_row += 1
        elif event.key() == Qt.Key_Up:
            current_row = self.table_widget.currentRow()
            while current_row > 0:
                prev_row = current_row - 1
                if not self.table_widget.isRowHidden(prev_row):
                    self.table_widget.selectRow(prev_row)
                    self.table_widget.setCurrentCell(prev_row, 0)
                    break
                current_row -= 1
        elif (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and self.table_widget.currentRow() != -1:
            visible_rows = [
                row for row in range(
                    self.table_widget.rowCount()) if not self.table_widget.isRowHidden(row)]
            if visible_rows:
                current_row = self.table_widget.currentRow()
                if current_row != -1:
                    self.selected_item_first_cell = self.table_widget.item(
                        current_row, 0).text()
                    self.accept()

        super().keyPressEvent(event)

# # Example usage
# if __name__ == '__main__':
#     app = QApplication(sys.argv)

#     # Sample data (replace this with your actual data)
#     data = [(1, '8978', 12, 1), (2, '4567', 79897978, 7989797), (3, '4567', 7989797, 798979),
#             (4, '', 798979, 7989), (5, '7890', 798979, ''), (6, '7676', 798979, 7989),
#             (7, '78789', 7989, ''), (8, '223232', 7989, '')]

#     column_names = ['Serial Number', 'Vehicle No', '1st Weight', '2nd Weight']

#     lookup_dialog = LookupDialog(data, column_names)
#     result = lookup_dialog.exec_()

#     if result == QDialog.Accepted:
#         selected_item_data = lookup_dialog.selected_item
#         print("Selected Item Data:", selected_item_data)

#     sys.exit()
