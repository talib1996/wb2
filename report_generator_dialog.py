# report_generator_dialog.py
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate
from report_form_ui import Ui_Dialog
from report import generate_report_datewise, generate_report_vehiclewise, generate_report_partywise
from database_operations import DatabaseOperations
# Set the LC_TIME environment variable to a specific value (e.g.,
# 'en_US.UTF-8' for English)
os.environ['LC_TIME'] = 'en_US.UTF-8'


class ReportGeneratorDialog(QtWidgets.QDialog):
    def __init__(self):
        super(ReportGeneratorDialog, self).__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.fromDate.setFocus()
        self.db = DatabaseOperations()

        # Get the current date
        current_date = QDate.currentDate()

        # Set the "From" date to the first day of the current month
        first_day_of_month = QDate(
            current_date.year(), current_date.month(), 1)
        self.ui.fromDate.setDate(first_day_of_month)

        # Set the "To" date to the last day of the current month
        last_day_of_month = QDate(
            current_date.year(),
            current_date.month(),
            current_date.daysInMonth())
        self.ui.toDate.setDate(last_day_of_month)

        # Connect the tabChanged signal to the setFocusOnTabChange slot
        self.ui.tabWidget.currentChanged.connect(self.setFocusOnTabChange)

        # Connect button click events to custom functions
        self.ui.submitDatewise.clicked.connect(self.onSubmitDatewise)
        self.ui.submitVehiclewise.clicked.connect(self.onSubmitVehiclewise)
        self.ui.submitPartywise.clicked.connect(self.onSubmitPartywise)
        vehicleColumnName = "vehicle_no"
        vehicleNoList = self.db.getColumnData(vehicleColumnName)
        self.ui.vehicleNo.addItems(vehicleNoList)
        partyColumnName = "party_name"
        partyNameList = self.db.getColumnData(partyColumnName)
        self.ui.partyName.addItems(partyNameList)

    def setFocusOnTabChange(self, tabIndex):
        if tabIndex == 0:  # Tab 1
            self.ui.fromDate.setFocus()
        elif tabIndex == 1:  # Tab 2
            self.ui.vehicleNo.setFocus()
        elif tabIndex == 2:  # Tab 3
            self.ui.partyName.setFocus()

    def onSubmitDatewise(self):
        # Your custom logic for the Datewise submit button
        result = generate_report_datewise(
            self.ui.fromDate.date().toString("dd/MM/yyyy"),
            self.ui.toDate.date().toString("dd/MM/yyyy"))
        if result is None:
            QMessageBox.warning(
                self, 'Information', 'No data found in this range')
        print("Datewise submit button pressed")

    def onSubmitVehiclewise(self):
        # Your custom logic for the Vehiclewise submit button
        result = generate_report_vehiclewise(self.ui.vehicleNo.currentText())
        if result is None:
            QMessageBox.warning(
                self,
                'Information',
                'No data found with this Vehicle')

    def onSubmitPartywise(self):
        # Your custom logic for the Vehiclewise submit button
        result = generate_report_partywise(self.ui.partyName.currentText())
        if result is None:
            QMessageBox.warning(
                self,
                'Information',
                'No data found with this Party Name')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = ReportGeneratorDialog()
    dialog.show()
    sys.exit(app.exec_())
