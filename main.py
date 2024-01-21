from search_available_ports import find_serial_ports
from PyQt5.QtCore import QThread, pyqtSignal
from report_generator_dialog import ReportGeneratorDialog
from LookupDialog import LookupDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplashScreen, QProgressBar, QMessageBox, QInputDialog, QShortcut, QDialog
from PyQt5 import QtGui
from weight_bridge_ui import Ui_WeighmentForm  # Import the generated UI class
from database_operations import DatabaseOperations
from weighment_slip_print import generate_report
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
import datetime
import sys
import os
import serial
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'chughtaitech.software.weightbridge.1.0'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass
# Set the LC_TIME environment variable to a specific value (e.g., 'en_US.UTF-8' for English)
os.environ['LC_TIME'] = 'en_US.UTF-8'
basedir = os.path.dirname(__file__)

first_weight_date_and_time = None
second_weight_date_and_time = None

# class WeightReaderThread(QThread):
# weight_updated = pyqtSignal(float)  # Signal to update the UI with the weight
##
# def __init__(self):
# super().__init__()
##
# def run(self):
# available_serial_ports = find_serial_ports()
# ser = serial.Serial(available_serial_ports[0], baudrate=9600, timeout=1)  # Replace 'COMx' with the correct serial port
# try:
# while True:
# weight_data = ser.readline().decode('utf-8').strip()
# print("1")
# if weight_data:
# print("2")
# self.weight_updated.emit(int(weight_data))
# except serial.SerialException as e:
# print(f"Error: {e}")
# finally:
# if ser.is_open:
# ser.close()


class Main_Class(QMainWindow):
    # global second_weight_date_and_time
    def __init__(self):
        super().__init__()
        
        # Set up a timer to delay showing the main window after 2 seconds
        self.window_timer = QTimer(self)
        self.window_timer.timeout.connect(self.show_main_window)
        self.window_timer.start(1900)  # Show the main window after 2000 milliseconds (2 seconds)




        # Create an instance of the UI class
        self.ui = Ui_WeighmentForm()
        self.ui.setupUi(self)
        self.db = DatabaseOperations()
        self.ui.serialNumber.setText(self.db.getSerialNumber())
# self.weight_reader_thread = WeightReaderThread()
# self.weight_reader_thread.weight_updated.connect(self.update_lcd_number)
# self.weight_reader_thread.start()
        self.ui.lcdNumber.display(8787)

        vehicleColumnName = "vehicle_no"
        vehicleNoList = self.db.getColumnData(vehicleColumnName)
        self.ui.vehicleNo.addItems(vehicleNoList)
        # print(vehicleNoList)
        partyColumnName = "party_name"
        partyNameList = self.db.getColumnData(partyColumnName)
        self.ui.partyName.addItems(partyNameList)
        itemColumnName = "item_name"
        itemNameList = self.db.getColumnData(itemColumnName)
        self.ui.itemName.addItems(itemNameList)
        bagWeightColumnName = "bag_weight"
        bagWeightList = self.db.getColumnData(bagWeightColumnName)
        bagWeightList_as_strings = [str(weight) for weight in bagWeightList]
        self.ui.bagWeight.addItems(bagWeightList_as_strings)

        self.ui.secondWeightdriver.setEnabled(False)
        # print(self.ui.lcdNumber.intValue())
        self.ui.saveButton.clicked.connect(self.save)
        self.ui.goToButton.clicked.connect(self.goto)
        # Create a new QShortcut object and set the key combination to
        # Qt.Key_F5.
        shortcut = QShortcut(Qt.Key_F5, self)

        # Connect the activated signal to a callback function.
        shortcut.activated.connect(self.on_f5_key_pressed)
        self.ui.newButton.clicked.connect(self.new)
        self.ui.closeButton.clicked.connect(self.close)
        self.ui.printButton.clicked.connect(self.print)
        self.ui.lookButton.clicked.connect(self.lookUp)
        self.ui.reportButton.clicked.connect(self.report)
        self.ui.bagWeight.editTextChanged.connect(self.update_tare_weight)
        self.ui.bagQuantity.valueChanged.connect(self.update_tare_weight)
        self.ui.vehicleNo.setFocus()

##    def advance_progress(self):
##        # Calculate the progress value based on the elapsed time
##        progress_value = int(100 - (self.progress_timer.remainingTime() / 20))
##
##        # Ensure the progress value stays within the valid range [0, 100]
##        progress_value = max(0, min(progress_value, 100))
##
##        # Update the progress bar value
##        self.progressBar.setValue(progress_value)
##
##        # Close the splash screen and show the main window after 2 seconds
##        if progress_value >= 100:
##            self.progress_timer.stop()
##            self.close_splash()
##    def advance_progress(self):
##        # Increment the progress bar value
##        current_value = self.progressBar.value()
##        new_value = current_value + 1
##        self.progressBar.setValue(new_value)
##
##        # Close the splash screen and show the main window after 2 seconds
##        if new_value >= 100:
##            self.progress_timer.stop()
##            self.splash.close()
    def advance_progress(self):
        # Increment the progress bar value
        current_value = self.progressBar.value()
        new_value = current_value + 1

        # Set the progress bar value, ensuring it reaches exactly 100
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(new_value)

        # Close the splash screen and show the main window after 2 seconds
        if new_value >= 100:
            self.progress_timer.stop()
            self.splash.close()

    def show_main_window(self):
            # Stop the progress timer
            self.progress_timer.stop()

            # Close the splash screen
            self.splash.close()

            # Show the main window
            self.show()

    def is_float(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False
    def update_tare_weight(self):
        if self.ui.bagWeight.currentText() == "" or self.ui.bagWeight.currentText().isspace():
            return
        else:
            if self.is_float(self.ui.bagWeight.currentText()):
                tare_weight = float(self.ui.bagWeight.currentText()) * self.ui.bagQuantity.value()
                self.ui.tareWeight.setText(str(tare_weight))
            else:
                QMessageBox.warning(self, 'Error', 'Enter a valid number!')
            # or not self.ui.bagWeight.currentText().isspace():
    def update_lcd_number(self, weight):
        self.ui.lcdNumber.display(weight)

    def report(self):
        reportGenerateDialog = ReportGeneratorDialog()
        reportGenerateDialog.exec_()

    def lookUp(self):
        print("ma sha Allah")

        data = self.db.fetchSelectedColumns(
            ['serial_number', 'vehicle_no', 'first_weight', 'second_weight'])
        column_names = [
            'Serial Number',
            'Vehicle No',
            '1st Weight',
            '2nd Weight']

        lookup_dialog = LookupDialog(data, column_names)
        result = lookup_dialog.exec_()

        if result == QDialog.Accepted:
            # this returns the first cell of the selected row which is a
            # serrial number
            serial_number = lookup_dialog.selected_item_first_cell
            # print("Selected Item Data:", serial_number)
            if serial_number is not None:
                row = self.db.fetchOneRow(serial_number)
                updation_type = "old"
                self.ui.secondWeightdriver.setDisabled(False)
                self.ui.secondWeightdriver.setFocus()
                self.update_entry_form(row, updation_type)

    def print(self):
        if self.db.check_if_exists(int(self.ui.serialNumber.text())):
            defaultValue = '3'  # Set your default number of copies here
            noOfCopies, done = QInputDialog.getText(
                self, 'Input Dialog', 'Enter Number of Copies:', text=defaultValue)
            if done is True:
                status = generate_report(
                    int(self.ui.serialNumber.text()), int(noOfCopies))
                if status == 0:
                    QMessageBox.warning(
                        self,
                        'information',
                        'Slip has been saved in the \\pending_slip folder, because printer was offline or not attached!')
                print("Alhamdulillah !")
            else:
                print("ma sha Allah")
        else:
            self.show_error_message_box('Cannot Print an unsaved form')

    def close(self):
        sys.exit()

    def new(self):
        row = [int(self.db.getSerialNumber()), "","" ,"", "", 0, "", "", "", "", ""]
        updation_type = "new"
        self.update_entry_form(row, updation_type)

    def on_f5_key_pressed(self):
        # Do something when the user presses the F5 key.
        print("F5 key pressed!")
        # self.ui.lcdNumber.display(0)
        if self.ui.lcdNumber.intValue() > 0:
            # Get the current date and time
            current_datetime = datetime.datetime.now()

            # Convert the datetime object to a string in ISO 8601 format
            current_datetime_string = current_datetime.isoformat()
            print(self.ui.serialNumber.text())
            if self.db.check_if_exists((int(self.ui.serialNumber.text()))):
                if (self.ui.firstWeight.text() !=
                        "" and self.ui.secondWeight.text() == ""):
                    if float(
                            self.ui.lcdNumber.intValue()) >= float(
                            self.ui.firstWeight.text()):
                        errorMessage = "Second Weight must be less than first weight"
                        self.show_error_message_box(errorMessage)
                    else:
                        self.ui.secondWeight.setText(
                            str(self.ui.lcdNumber.intValue()))
                        global second_weight_date_and_time
                        second_weight_date_and_time = current_datetime_string
                        self.ui.netWeight.setText(
                            str(float(self.ui.firstWeight.text()) - float(self.ui.secondWeight.text()) - float(self.ui.tareWeight.text())))
            # self.ui.firstWeight.setText(str(self.ui.lcdNumber.intValue()))
                elif (self.ui.firstWeight.text() != "" and self.ui.secondWeight.text() != ""):
                    errorMessage = "Can't update"
                    self.show_error_message_box(errorMessage)
            else:
                if (self.ui.firstWeight.text() ==
                        "" and self.ui.secondWeight.text() == ""):
                    self.ui.firstWeight.setText(
                        str(self.ui.lcdNumber.intValue()))
                    global first_weight_date_and_time
                    first_weight_date_and_time = current_datetime_string
        else:
            errorMessage = "Invalid Input. Weight can't be zero!"
            self.show_error_message_box(errorMessage)

    def goto(self):
        serialNumber, done = QInputDialog.getText(
            self, 'Input Dialog', 'Enter Serial Number:')
        if done is True:
            print("Alhamdulillah !")
            row = self.db.fetchOneRow(serialNumber)
            print(row)
            if row:
                # print(row[1])
                updation_type = "old"
                self.ui.secondWeightdriver.setDisabled(False)
                self.ui.secondWeightdriver.setFocus()
                self.update_entry_form(row, updation_type)
            else:
                errorMessage = "No Record exists with this Serial Number"
                self.show_error_message_box(errorMessage)
        else:
            print("ma sha Allah")

    def update_entry_form(self, row, updationType):
        if updationType == "old":
            print(row)
            self.ui.serialNumber.setText(str(row[0]))
            self.ui.vehicleNo.setEditText(str(row[1]))
            self.ui.vehicleNo.setDisabled(True)
            self.ui.partyName.setEditText(str(row[2]))
            self.ui.partyName.setDisabled(True)
            self.ui.itemName.setDisabled(True)
            self.ui.itemName.setEditText(str(row[3]))
            self.ui.bagWeight.setDisabled(True)
            self.ui.bagWeight.setEditText(str(row[4]))
            self.ui.bagQuantity.setDisabled(True)
            self.ui.bagQuantity.setValue(row[5])
            self.ui.tareWeight.setText(str(row[6]))
            self.ui.firstWeight.setText(str(row[7]))
            self.ui.secondWeight.setText(str(row[8]))
            self.ui.netWeight.setText(str(row[9]))
            self.ui.firstWeightdriver.setDisabled(True)
            if str(self.ui.netWeight.text()) != "":
                self.ui.secondWeightdriver.setDisabled(True)
            if int(row[10]) != 0:
                self.ui.firstWeightdriver.setChecked(True)
            if row[11] and not "NULL":
                self.ui.secondWeightdriver.setChecked(True)
        else:
            self.ui.serialNumber.setText(str(row[0]))
            self.ui.vehicleNo.setEditText(str(row[1]))
            self.ui.vehicleNo.setDisabled(False)
            self.ui.partyName.setEditText(str(row[2]))
            self.ui.partyName.setDisabled(False)
            self.ui.itemName.setDisabled(False)
            self.ui.itemName.setEditText(str(row[3]))
            self.ui.bagWeight.setDisabled(False)
            self.ui.bagWeight.setEditText(str(row[4]))
            self.ui.bagQuantity.setDisabled(False)
            self.ui.bagQuantity.setValue(row[5])
            self.ui.tareWeight.setText(row[6])
            self.ui.firstWeight.setText(str(row[7]))
            self.ui.secondWeight.setText(str(row[8]))
            self.ui.netWeight.setText(str(row[9]))
            self.ui.firstWeightdriver.setDisabled(False)
            self.ui.firstWeightdriver.setChecked(False)
            self.ui.secondWeightdriver.setDisabled(True)
            self.ui.secondWeightdriver.setChecked(False)
        self.ui.vehicleNo.setFocus()

    def show_error_message_box(self, errorMessage):
        # Create a QMessageBox
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(errorMessage)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()

    def save(self):
        vehicle_number = self.ui.vehicleNo.currentText()
        party_name = self.ui.partyName.currentText()
        item_name = self.ui.itemName.currentText()
        bag_weight = self.ui.bagWeight.currentText()
        bag_quantity = self.ui.bagQuantity.value()

        if not vehicle_number:
            QMessageBox.warning(self, 'Warning', 'Vehicle number is required!')
            return
        if not party_name:
            QMessageBox.warning(self, 'Warning', 'Party name is required!')
            return
        if not item_name:
            QMessageBox.warning(self, 'Warning', 'Item name is required!')
            return
        if not bag_weight:
            QMessageBox.warning(self, 'Warning', 'Bag Weight is required!')
            return
        if not bag_weight.isdigit():
            try:
                float(bag_weight)
            except ValueError:
                QMessageBox.warning(self, 'Warning', 'It must be a digit')
                self.ui.bagWeight.setFocus()
                return
        if not bag_quantity:
            QMessageBox.warning(self, 'Warning', 'Bags Quantity is required!')
            return
        if bag_quantity < 1:
            QMessageBox.warning(self, 'Warning', 'Bags Quantity cannot be 0!')
            return
        if (self.ui.firstWeight.text() ==
                "" and self.ui.secondWeight.text() == ""):
            errorMessage = "Can't save without first weight"
            self.show_error_message_box(errorMessage)
            return

            # Get the current date and time
        current_datetime = datetime.datetime.now()

        # Convert the datetime object to a string in ISO 8601 format
        current_datetime_string = current_datetime.isoformat()
        # Display the error message
        if (self.ui.firstWeight.text() !=
                "" and self.ui.secondWeight.text() == ""):
            if self.db.check_if_exists((int(self.ui.serialNumber.text()))):
                errorMessage = "Can't save again without second weight"
                self.show_error_message_box(errorMessage)
                return
            else:
                # vehicle_no = self.ui.vehicleNo.currentText()
                # party_name = self.ui.partyName.currentText()
                # item_name = self.ui.itemName.currentText()
                first_weight = self.ui.firstWeight.text()
                second_weight = self.ui.secondWeight.text()
                first_weight_driver = self.ui.firstWeightdriver.isChecked()
                second_weight_driver = "NULL"
                net_weight = self.ui.netWeight.text()
                tare_weight = self.ui.tareWeight.text()

                # Create the data_to_insert tuple
                data_to_insert = {
                    "vehicle_no": vehicle_number,
                    "party_name": party_name,
                    "item_name": item_name,
                    "bag_weight": bag_weight,
                    "bag_quantity": bag_quantity,
                    "tare_weight": tare_weight,
                    "first_weight": first_weight,
                    "second_weight": second_weight,
                    "net_weight": net_weight,
                    "first_weight_driver": first_weight_driver,
                    "second_weight_driver": second_weight_driver,
                    "first_weight_date_and_time": first_weight_date_and_time,
                    "second_weight_date_and_time": "NULL",
                    "created_at": current_datetime_string,
                    "modified_at": "NULL"
                }
                print("saving")
                print(data_to_insert)
                last_inserted_id = self.db.insert(data_to_insert)
                row = [int(self.db.getSerialNumber()),
                       "", "", "", "", 0, "", "", "", ""]
                updation_type = "new"
                self.update_entry_form(row, updation_type)
            print(last_inserted_id)
        if (self.ui.firstWeight.text() !=
                "" and self.ui.secondWeight.text() != ""):
            second_weight = self.ui.secondWeight.text()
            second_weight_driver = self.ui.secondWeightdriver.isChecked()
            net_weight = self.ui.netWeight.text()
            # Create the data_to_update tuple
            data_to_update = {
                "second_weight": second_weight,
                "net_weight": net_weight,
                "second_weight_driver": second_weight_driver,
                "second_weight_date_and_time": second_weight_date_and_time,
                "modified_at": current_datetime_string
            }
            self.db.update(data_to_update, int(self.ui.serialNumber.text()))
            row = [int(self.db.getSerialNumber()),
                   "", "", "", "", 0, "", "", "", ""]
            updation_type = "new"
            self.update_entry_form(row, updation_type)
            print("save 2")

    def getBalanceWithoutSecondWeight(self):
        print("Allah")


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, "./icons",'main_icon.ico')))
    window = Main_Class()
     # Create a splash screen
    splash_pix = QtGui.QPixmap('images/splash_image.png')  # Replace with the path to your splash image
    window.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    window.splash.setMask(splash_pix.mask())

    # Add progress bar to the splash screen (optional)
    window.progressBar = QProgressBar(window.splash)
    window.progressBar.setGeometry(0, window.splash.height() - 25, window.splash.width(), 20)

    # Set progress bar properties (optional)
    window.progressBar.setMinimum(0)
    window.progressBar.setMaximum(100)

    # Display the splash screen
    window.splash.show()

    # Set up a timer to update the progress bar every 20 milliseconds for 2 seconds
    window.progress_timer = QTimer(window)
    window.progress_timer.timeout.connect(window.advance_progress)
    window.progress_timer.start(10)  # Update every 10 milliseconds
    
    sys.exit(app.exec_())
##    window.show()
