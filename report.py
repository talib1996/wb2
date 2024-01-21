import webbrowser
import tempfile
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from database_operations import DatabaseOperations
from datetime import datetime
# Set the LC_TIME environment variable to a specific value (e.g.,
# 'en_US.UTF-8' for English)
os.environ['LC_TIME'] = 'en_US.UTF-8'


def generate_report_datewise(fromDate, toDate, no_of_copies=1):
    db = DatabaseOperations()
    filter_criteria = [fromDate, toDate]
    filter_type = "datewise"
    data = db.fetchSelectedColumns(['serial_number',
                                    'vehicle_no',
                                    'first_weight',
                                    'second_weight',
                                    'tare_weight',
                                    'net_weight',
                                    'created_at'],
                                   filter_criteria,
                                   filter_type)
    db.close_cursor()
    if data:
        data_list = ["Computerized Weight Report Datewise",
                     "Date Range: " + fromDate + " - " + toDate]
        return generate_pdf(data_list, data, no_of_copies, "Vehicle #")
    else:
        return None


def generate_report_vehiclewise(vehicleNo, no_of_copies=1):
    db = DatabaseOperations()
    filter_criteria = [vehicleNo]
    filter_type = "vehiclewise"
    data = db.fetchSelectedColumns([
                                    'serial_number',
                                    'party_name',
                                    'first_weight',
                                    'second_weight',
                                    'tare_weight',
                                    'net_weight',
                                    'created_at'],
                                   filter_criteria,
                                   filter_type)
    db.close_cursor()
    # print(data_list[1])
    if data:
        data_list = [
            "Computerized Weight Report VehicleWise",
            "Vehicle No: " + vehicleNo]
        # print(data)
        return generate_pdf(data_list, data, no_of_copies, "Party Name")

    else:
        return None


def generate_report_partywise(partyName, no_of_copies=1):
    db = DatabaseOperations()
    filter_criteria = [partyName]
    filter_type = "partywise"
    data = db.fetchSelectedColumns(['serial_number',
                                    'vehicle_no',
                                    'first_weight',
                                    'second_weight',
                                    'tare_weight',
                                    'net_weight',
                                    'created_at'],
                                   filter_criteria,
                                   filter_type)
    db.close_cursor()
    # print(data_list[1])
    if data:
        data_list = [
            "Computerized Weight Report PartyWise",
            "Party Name: " + partyName]
        return generate_pdf(data_list, data, no_of_copies, "Vehicle #")
    else:
        return None


def generate_pdf(data_list, data, no_of_copies, second_column_name=""):
    # Specify the page size
    width, height = A4
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        # Create a canvas
        c = canvas.Canvas(temp_file.name, pagesize=(width, height))

        # Add content to the report
        # Add headings at the top center
        company_name = "Ideal Fluting and Craft Paper (Pvt) Ltd"
        address = "2-km, Sharaqpur Road, Near Murad-E-Khurad, Sheikhupura"
        contact_info = "Contact: 0321-4433500, 0321-4248644"

        # Create a canvas using the temporary file
        for _ in range(no_of_copies):  # Print the report three times

            # Set the font for the company name to 18px and bold
            c.setFont("Helvetica-Bold", 18)

            # Calculate the width and height of the company name text to be
            # centered
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

            # Calculate the width and height of the contact info text to be
            # centered
            contact_width = c.stringWidth(contact_info, "Helvetica", 12)
            contact_height = 12  # Font size is 12px

            # Center the contact info text horizontally
            x_contact_centered = (width - contact_width) / 2

            # Set the position for the third line with reduced margin
            y_third_line = y_second_line - address_height - 4  # Reduced margin

            # Draw the centered contact information
            c.drawString(x_contact_centered, y_third_line, contact_info)

            # Add "Computerized Weight Slip" with borders, centered text, and
            # padding
            c.setFont("Helvetica-Bold", 12)
            weight_slip_text = data_list[0]
            padding = 3  # Adjust the padding as needed

            weight_slip_width = c.stringWidth(
                weight_slip_text, "Helvetica-Bold", 12)
            weight_slip_x = x_contact_centered  # Centered with the contact info
            weight_slip_y = y_third_line - 5  # Adjusted position

            # Calculate center positions for the text inside the borders with
            # padding
            text_center_x = weight_slip_x + \
                (weight_slip_width + 4 + 2 * padding) / 2
            # Adjusted calculation for vertical centering
            text_center_y = weight_slip_y - 2 - 28 / 2 - padding

            # Calculate borders with padding
            border_x_start = text_center_x - \
                (weight_slip_width + 4 + 2 * padding) / 2
            border_y_start = weight_slip_y - 2 - padding
            border_x_end = text_center_x + \
                (weight_slip_width + 4 + 2 * padding) / 2
            border_y_end = border_y_start - 14 + 2 * padding  # Adjusted height

            # Draw the borders with padding
            c.rect(border_x_start, border_y_start, weight_slip_width +
                   4 + 2 * padding, -14 - 2 * padding)

            # Draw the centered text inside the borders with padding
            c.drawCentredString(text_center_x, text_center_y, weight_slip_text)

            # Add the date range beneath the centered text with a clearer
            # format
            date_range_text = data_list[1]
            date_range_font_size = 15
            date_range_color = colors.black  # You can choose the color you prefer
            date_range_width = c.stringWidth(
                date_range_text, "Times-Bold", date_range_font_size)
            x_date_range_centered = (width - date_range_width) / 2
            y_date_range = text_center_y - 25  # Adjusted margin

            # Set the font to Times New Roman and bold
            c.setFont("Times-Bold", date_range_font_size)
            c.setFillColor(date_range_color)

            # Draw the date range with the improved format
            c.drawString(x_date_range_centered, y_date_range, date_range_text)

            # Define the table data
            table_data = [["Serial Number",
                            second_column_name,
                           "First Weight",
                           "Second Weight",
                           "Tare Weight",
                           "Net Weight",
                           "Created At"]]

            for row in data:
                # Convert the original date string to a datetime object
                created_at = datetime.fromisoformat(row[-1])

                # Format the datetime object as "YYYY-MM-DD"
                formatted_date = created_at.strftime("%d-%m-%Y")

                # Convert the tuple to a list, modify the list, and then
                # convert it back to a tuple
                row_list = list(row)
                row_list[-1] = formatted_date
                row = tuple(row_list)

                table_data.append(list(map(str, row)))

                # Define the style for the table
                style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                    ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                                    # Set header font size to 12
                                    ('FONTSIZE', (0, 0), (-1, 0), 12.5),
                                    # Set the desired font size
                                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                    ('GRID', (0, 0), (-1, -1), 1, colors.black)])    # Adjust as needed

            # Create the table
            pdf_table = Table(
                table_data, colWidths=[
                    90, 90, 90, 90, 80, 80, 80])

            # Apply the style to the table
            pdf_table.setStyle(style)

            # Use the wrap method to get the width and height of the table
            table_width, table_height = pdf_table.wrap(width, height)

            # Calculate the x-coordinate to center the table
            x_table_centered = (width - table_width) / 2

            # Check if there is enough space on the current page for the table
            if weight_slip_y - table_height - 30 < 30:
                # Start a new page if there isn't enough space
                c.showPage()
                y_date_range = height - 30  # Reset the position for the third line

            # Draw the table on the canvas, centered horizontally
            pdf_table.drawOn(
                c,
                x_table_centered,
                y_date_range -
                table_height -
                10)
            c.showPage()

            # Save the PDF content in the temporary file
        c.save()
        webbrowser.open(temp_file.name)
        return 1

    # # Save the canvas to a file
    # c.save()
# # Specify the file path where you want to save the report
# file_path = "./report_with_labels_and_table.pdf"

# # Specify the page size
# width, height = A4

# # Generate the report with labels and the wider table
# generate_report_datewise("01/01/2024", "31/01/2024", 1)

# Example usage
# current_os = get_operating_system()
# if current_os == "Windows":
#     print("Running on Windows.")
# elif current_os == "Linux":
#     print("Running on Linux.")
# elif current_os == "Darwin":
#     print("Running on macOS.")
# else:
#     print("Operating system not recognized.")
