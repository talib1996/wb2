try:
    import win32print
    import win32api
except ImportError:
    win32print = None
    win32api = None
try:
    from cups import Connection
except ImportError:
    Connection = None
import webbrowser, platform, os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from database_operations import DatabaseOperations
from datetime import datetime
basedir = os.path.dirname(__file__)

# Set the LC_TIME environment variable to a specific value (e.g., 'en_US.UTF-8' for English)
os.environ['LC_TIME'] = 'en_US.UTF-8'
def generate_report(serial_number, no_of_copies=3, pdf_file_path=os.path.join(basedir, r'temp_report.pdf')):
    if check_printer_attached():
        width, height = A4
        print("Printer is attached.")
        # Example usage
        current_os = get_operating_system()
        c = canvas.Canvas(pdf_file_path, pagesize=A4)
        for _ in range(no_of_copies):
            generate_pdf(c, serial_number)
            # Save the page content and start a new page for the next print
            c.showPage()

        # Save the PDF content in the temporary file
        c.save()

        if current_os == "Windows":
            print("Running on Windows.")
            GHOSTSCRIPT_PATH = ".\GHOSTSCRIPT\\bin\gswin32c.exe"
            GSPRINT_PATH = os.path.join(basedir, '.\GSPRINT\gsprint.exe')
            current_printer = win32print.GetDefaultPrinter()
            relative_path = pdf_file_path
            absolute_path = os.path.join(basedir, relative_path)
            command = [
                '-sDEVICE=mswinpr2',
                '-dBATCH',
                '-dNOPAUSE',
                '-sPAPERSIZE=a4',
                f'-sOutputFile="%printer%{current_printer}"',
                '-f',
                absolute_path
            ]
            
##            print("Command:", command)  # Debugging print
    
# Combine the command list into a single string
            command_string = " ".join(command)

    # Use ShellExecute to run the command
            status = win32api.ShellExecute(0, "open", GHOSTSCRIPT_PATH, command_string, None, 1)
            print(status)
            ##            os.startfile(absolute_path, 'Print')
            # Wait for the process to finish
##            win32api.ShellExecute(
##                           0,
##                           "open",
##                           GSPRINT_PATH,
##                           '-printer "Kyocera TASKalfa 5501i" ' + '"%s"' % absolute_path,
##                           ".",
##                           0
##                         )
##gswin32c.exe -sDEVICE=mswinpr2 -dBATCH -dNOPAUSE -sPAPERSIZE=a4 -dFIXEDMEDIA -dPDFFitPage -sOutputFile="%printer%Kyocera TASKalfa 5501i" -f
    
##gswin32c.exe -sDEVICE=mswinpr2 -dBATCH -dNOPAUSE -sOutputFile="%printer%Kyocera TASKalfa 5501i"
##gswin32c.exe -dNORANGEPAGESIZE -dPrinted -dNoCancel -dBATCH -dNOPAUSE -dNOSAFER -q -dNumCopies=1 -dQueryUser=3 -sDEVICE=mswinpr2
##.\GSPRINT\gsprint.exe -ghostscript .\GHOSTSCRIPT\bin\gswin32.exe -noquery -all -printer "Kyocera TASKalfa 5501i"

##            gsprint -noquery -all -printer "Kyocera TASKalfa 5501i"
##            win32api.ShellExecute(0, 'open', GHOSTSCRIPT_PATH, '-ghostscript "'+GSPRINT_PATH+'" -printer "'+current_printer+'" "%s"'%(absolute_path), '.', 0)
##            try:
##                subprocess.run(['print', pdf_file_path], shell=False, timeout=10)
##            except subprocess.TimeoutExpired:
##                print('The process did not finish within 0 seconds.')
##            os.remove(pdf_file_path)
            return 1
        elif current_os == "Linux":
            os.system(f"lp {pdf_file_path}")
            os.remove(pdf_file_path)
            return 1

            print("Running on Linux.")
        elif current_os == "Darwin":
            print("Running on macOS.")
        else:
            print("Operating system not recognized.")
    else:
        print("Printer is not attached.")
        # Specify the page size
        width, height = A4
##        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            # Create a canvas
        slip_path_with_name = "pending_slips/"+"slip_no_"+str(serial_number)+".pdf"
        c = canvas.Canvas(slip_path_with_name, pagesize=(width, height))
                # Create a canvas using the temporary file
        for _ in range(no_of_copies):  # Print the report three times
            generate_pdf(c, serial_number)
            # Save the page content and start a new page for the next print
            c.showPage()

            # Save the PDF content in the temporary file
        c.save()
        relative_path = slip_path_with_name
        absolute_path = os.path.abspath(relative_path)
        webbrowser.open(absolute_path, new=2)
        return 0
def get_operating_system():
    system = platform.system()
    return system
##def check_printer_attached():
##    return os.path.exists('/dev/usb/lp0')
def check_printer_attached():
    if get_operating_system()== "Windows":
        handle = win32print.OpenPrinter(win32print.GetDefaultPrinter())
        attributes = win32print.GetPrinter(handle)[13]
        isOffline = (attributes & 0x00000400) >> 10
        if isOffline:
            return False
        else:
            return True
    elif get_operating_system() == "Linux":
    	return os.path.exists('/dev/usb/lp0')
def get_default_printer():
    if get_operating_system() == "Linux":
        connection = Connection()
        default_printer = connection.getDefault()
        # Assuming the Connection class has a close method
        return default_printer
    elif get_operating_system() == "Windows":
        return win32print.GetDefaultPrinter()
def generate_pdf(c,serial_number):
    # Use A4 size paper
    width, height = A4

    # Add content to the report
    # Add headings at the top center
    company_name = "Ideal Fluting and Craft Paper (Pvt) Ltd"
    address = "2-km, Sharaqpur Road, Near Murad-E-Khurad, Sheikhupura"
    contact_info = "Contact: 0321-4433500, 0321-4248644"

    # Set the font for the company name to 18px and bold
    c.setFont("Helvetica-Bold", 18)

    # Calculate the width and height of the company name text to be centered
    text_width = c.stringWidth(company_name, "Helvetica-Bold", 18)
    text_height = 18  # Font size is now 18px

    # Center the company name text horizontally
    x_centered = (width - text_width) / 2

    # Set the position for the first line with reduced top margin
    y_first_line = height - 30  # Reduced top margin

    # Draw the company name
    c.drawString(x_centered, y_first_line, company_name)

    # Set the font back to regular for the other text
    c.setFont("Helvetica", 12)

    # Calculate the width and height of the address text to be centered
    address_width = c.stringWidth(address, "Helvetica", 12)
    address_height = 12  # Font size is 12px

    # Center the address text horizontally
    x_address_centered = (width - address_width) / 2

    # Set the position for the second line with reduced margin
    y_second_line = y_first_line - text_height - 4  # Reduced margin

    # Draw the centered address
    c.drawString(x_address_centered, y_second_line, address)

    # Calculate the width and height of the contact info text to be centered
    contact_width = c.stringWidth(contact_info, "Helvetica", 12)
    # Center the contact info text horizontally
    x_contact_centered = (width - contact_width) / 2

    # Set the position for the third line with reduced margin
    y_third_line = y_second_line - address_height - 4  # Reduced margin

    # Draw the centered contact information
    c.drawString(x_contact_centered, y_third_line, contact_info)

    # Add "Computerized Weight Slip" with borders, centered text, and padding
    c.setFont("Helvetica-Bold", 12)
    weight_slip_text = "Computerized Weight Slip"
    padding = 3  # Adjust the padding as needed

    weight_slip_width = c.stringWidth(weight_slip_text, "Helvetica-Bold", 12)
    weight_slip_x = x_contact_centered  # Centered with the contact info
    weight_slip_y = y_third_line - 10  # Adjusted position

    # Calculate center positions for the text inside the borders with padding
    text_center_x = weight_slip_x + (weight_slip_width + 4 + 2 * padding) / 2
    text_center_y = weight_slip_y - 2 - 28 / 2 - padding  # Adjusted calculation for vertical centering

    # Calculate borders with padding
    border_x_start = text_center_x - (weight_slip_width + 4 + 2 * padding) / 2
    border_y_start = weight_slip_y - 2 - padding

    # Draw the borders with padding
    c.rect(border_x_start, border_y_start, weight_slip_width + 4 + 2 * padding, -14 - 2 * padding)

    # Draw the centered text inside the borders with padding
    c.drawCentredString(text_center_x, text_center_y, weight_slip_text)

    db = DatabaseOperations()
    data = db.fetchOneRow(serial_number)
    data_dict = {
        'serial_number': data[0],
        'vehicle_no': data[1],
        'party_name': data[2],
        'item_name': data[3],
        'tare_weight': data[6],
        'first_weight': data[7],
        'second_weight': data[8],
        'net_weight': data[9],
        'first_weight_driver': data[10],
        'second_weight_driver': data[11],
        'first_weight_date_and_time': data[12],
        'second_weight_date_and_time': data[13],
    }
    # print(data_dict)

    # Add labels before the table
    labels = [
        ["Serial No:", str(data_dict['serial_number']), "Party Name:", str(data_dict['party_name'])],
        ["Vehicle No:", str(data_dict['vehicle_no']), "Item Name:", str(data_dict['item_name'])]
    ]

    # Set font and font size
    c.setFont("Helvetica-Bold", 12)

    # First label
    label1_text = labels[0][0]
    label1_x = 65
    label1_y = weight_slip_y - 50
    c.drawString(label1_x, label1_y, label1_text)

    # Set font and font size
    c.setFont("Helvetica", 12)

    # First Value
    value1_text = labels[0][1]
    value1_x = label1_x + 69
    value1_y = label1_y
    c.drawString(value1_x, value1_y, value1_text)

    # Set font and font size
    c.setFont("Helvetica-Bold", 12)

    # Second label
    label2_text = labels[0][2]
    label2_x = value1_x + 100
    label2_y = label1_y
    c.drawString(label2_x, label2_y, label2_text)

    # Set font and font size
    c.setFont("Helvetica", 12)

    # Second Value
    value2_text = labels[0][3]
    value2_x = label2_x + 75
    value2_y = label1_y
    c.drawString(value2_x, value2_y, value2_text)

        # Set font and font size
    c.setFont("Helvetica-Bold", 12)

    # Third label
    label3_text = labels[1][0]
    label3_x = label1_x
    label3_y = label1_y - 25
    c.drawString(label3_x, label3_y, label3_text)

    # Set font and font size
    c.setFont("Helvetica", 12)

    # Third Value
    value3_text = labels[1][1]
    value3_x = label3_x + 70
    value3_y = label3_y
    c.drawString(value3_x, value3_y, value3_text)

            # Set font and font size
    c.setFont("Helvetica-Bold", 12)

    # Fourth label
    label4_text = labels[1][2]
    label4_x = label2_x
    label4_y = label3_y
    c.drawString(label4_x, label4_y, label4_text)

    # Set font and font size
    c.setFont("Helvetica", 12)

    # Fourth Value
    value4_text = labels[1][3]
    value4_x = label4_x + 70
    value4_y = label4_y
    c.drawString(value4_x, value4_y, value4_text)

    # Calculate the position to place the label table below the "Computerized Weight Slip" section
    y_label_table_position = y_third_line - 60 # Adjust the vertical position as needed

    # Using datetime parsing and strftime
    datetime_object = datetime.fromisoformat(data_dict['first_weight_date_and_time'])
    first_weight_date = datetime_object.date()  # Extracts datetime.date object
    first_weight_time_24 = datetime_object.time()  # Extracts datetime.time object

    # Format time in AM/PM
    first_weight_time_ampm = first_weight_time_24.strftime("%I:%M:%S %p")
    print(first_weight_time_ampm)
    if data_dict['second_weight_date_and_time'] != "NULL":

        # Using datetime parsing and strftime
        if data_dict['second_weight_date_and_time'] is not None:
            datetime_object = datetime.fromisoformat(data_dict['second_weight_date_and_time'])
            second_weight_date = datetime_object.date()  # Extracts datetime.date object
            second_weight_time_24 = datetime_object.time()  # Extracts datetime.time object

        # Format time in AM/PM
        second_weight_time_ampm = second_weight_time_24.strftime("%I:%M:%S %p")
    else:
        second_weight_date = ""
        second_weight_time_ampm = ""

    # Convert the net weight to munds

# Display the results
    if data_dict['net_weight'] != "":
        munds = str((data_dict['net_weight']) // 40)
        remaining_kilograms = str((data_dict['net_weight']) % 40)  # Using modulo to get the remaining kilograms

        munds_text = f"{munds} Munds, {float(remaining_kilograms):.2f} Kg"
    else:
        munds_text = ""
    column_names = ["Weight Type", "Kg", "Date", "Time"]
    data = [
        column_names,
        ["1st Weight: ", data_dict['first_weight'], first_weight_date, first_weight_time_ampm],
        ["2nd Weight: ", data_dict['second_weight'], second_weight_date, second_weight_time_ampm],
        ["Tare Weight: ", data_dict['tare_weight'], ""],
        ["Net Weight: ", data_dict['net_weight'], "" ],
    ]
# Set the font with bold for the specific cell
    c.setFont("Helvetica-Bold", 12)

    # Draw bold text in the specified cell
    c.drawString(305, 531, "Munds (40Kg): ")
    c.setFont("Helvetica", 12)

    # Draw bold text in the specified cell
    c.drawString(395, 531, munds_text)
    # Set column widths to decrease the overall width of the table
    col_widths = [int(width / 5) for _ in range(4)]  # Convert to integer

    # Define style for the table
    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Center vertically
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 0), (0, 5), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (29, 29), 12),  # Set the font size for all values in the table
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add this line for black borders
        ('SPAN', (2, 4), (3, 4)),  # Merge the third and fourth columns in row 4
    ])

    # Create the table with specified column widths
    table = Table(data, colWidths=col_widths)

    # Set a fixed height for each row in the table (adjust the height as needed)
    row_height = 30
    table_row_heights = [row_height for _ in range(len(data))]

    # Create the table with specified column widths and row heights
    table = Table(data, colWidths=col_widths, rowHeights=table_row_heights)

    # Apply the style to the table
    table.setStyle(style)

    # Calculate the table height
    table_width, table_height = table.wrapOn(c, width, height)

    # Calculate the position to center the table horizontally
    x_table_centered = (width - table_width) / 2

    # Calculate the position to place the table below the "Computerized Weight Slip" section
    y_table_position = y_label_table_position - 42  # Adjust the vertical position as needed

    # Draw the table on the canvas
    table.drawOn(c, x_table_centered, y_table_position - table_height)

        # Add a label "Sign:" after the table
    sign_label = "Sign:"
    sign_label_x = x_table_centered
    sign_label_y = y_table_position - table_height - 36  # Adjust the vertical position as needed

    # Draw the sign label
    c.setFont("Helvetica-Bold", 12)
    c.drawString(sign_label_x, sign_label_y, sign_label)

    # Add a line for writing the signature
    line_start_x = sign_label_x + c.stringWidth(sign_label, "Helvetica-Bold", 12) + 5
    line_start_y = sign_label_y - 4 # Adjusted position
    line_end_x = line_start_x + 200  # Adjusted length of the line
    line_end_y = line_start_y

    # Draw the line
    c.line(line_start_x, line_start_y, line_end_x, line_end_y)


# # Specify the file path where you want to save the report
##file_path = "./report_with_labels_and_table.pdf"


##app = QCoreApplication([])

# # Generate the report with labels and the wider table
##generate_report(1,1)

##app.quit()
