import sqlite3
from datetime import datetime

class DatabaseOperations:
    def __init__(self):
        print("Allah!")
        # Specify the path and name of the new database file
        self.db_file = "./db/weight_balance.db"
        self.table_name = "weighment"
        # Connect to the database (this will create the file if it doesn't exist)
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.init_table()
        self.close_cursor()

    def init_table(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                serial_number INTEGER PRIMARY KEY,
                vehicle_no TEXT,
                party_name TEXT,
                item_name TEXT,
                bag_weight REAL,
                bag_quantity INTEGER,
                tare_weight REAL,
                first_weight REAL,
                second_weight REAL,
                net_weight REAL,
                first_weight_driver TEXT,
                second_weight_driver TEXT,
                first_weight_date_and_time TEXT,
                second_weight_date_and_time TEXT,
                created_at TEXT,
                modified_at TEXT
            )
        ''')
        self.conn.commit()

    def insert(self, data_to_insert):
        # Execute the INSERT statement
   # Define the SQL INSERT statement dynamically based on the dictionary keys
        columns = ', '.join(data_to_insert.keys())
        placeholders = ', '.join(['?'] * len(data_to_insert))
        insert_query = f'''
            INSERT INTO {self.table_name}
            ({columns})
            VALUES ({placeholders})
        '''
      # Extract values from the dictionary and insert data into the database
        values = tuple(data_to_insert.values())
        self.cursor.execute(insert_query, values)

        # Commit the transaction to save the changes
        self.conn.commit()
        
        # Get the ID of the last inserted row
        last_inserted_id = self.cursor.lastrowid

        # Close the cursor and connection
        self.close_cursor()


        return last_inserted_id
    def update(self, data_to_update, serialNumber):
        # Execute the INSERT statement
   # Define the SQL INSERT statement dynamically based on the dictionary keys
        columns = ', '.join(data_to_update.keys())
        placeholders = ', '.join(['?'] * len(data_to_update))
        update_query = f'''
            UPDATE {self.table_name} SET
            ({columns}) = ({placeholders}) 
            WHERE serial_number = {serialNumber}
        '''
      # Extract values from the dictionary and insert data into the database
        values = tuple(data_to_update.values())
        self.cursor.execute(update_query, values)

        # Commit the transaction to save the changes
        self.conn.commit()
        
        print(self.cursor.rowcount) 
        # # Get the ID of the last inserted row
        # last_inserted_id = self.cursor.lastrowid

        # # Close the cursor and connection
        # self.close_cursor()


        # return last_inserted_id
    def open_cursor(self):
        self.cursor = self.conn.cursor()
    def close_cursor(self):
        self.cursor.close()
    def close_connection(self):
        self.conn.close()
    def getSerialNumber(self):
        print("getting serialnumber")
        self.cursor = self.conn.cursor()
        # Execute a SQL query to count the rows in the table
        self.cursor.execute(f"""SELECT serial_number
                            FROM {self.table_name}
                            ORDER BY serial_number DESC
                            LIMIT 1;
                            """)
        
        # Fetch the result
        result = self.cursor.fetchone()
        self.close_cursor()
        if result is not None:
            last_serial_number = result[0]
            return str(last_serial_number + 1) 
        else:
            return "1"
        # return self.cursor.fetchone()[0]
    def fetchOneRow(self, serialNumber):
        self.open_cursor()
        self.cursor.execute("SELECT * FROM {} WHERE serial_number = ?".format(self.table_name), (serialNumber,))
        row = self.cursor.fetchone()
        if row:
            return row
        else:
            print('No row found with Serial Number', serialNumber)
            return None
    def fetchAllRows(self):
        # Build and execute the SQL query to fetch all rows
        query = f'SELECT * FROM {self.table_name}'

        self.open_cursor()
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.close_cursor()
        return rows
    # def fetchSelectedColumns(self):
    #     self.open_cursor()
    #     self.cursor.execute(f'SELECT serial_number, vehicle_no, first_weight, second_weight FROM {self.table_name}')
    #     rows = self.cursor.fetchall()
    #     self.close_cursor()
    #     return rows
    def fetchSelectedColumnsVehicleWise(self, selected_columns, fromDate, toDate):
        if not selected_columns:
            raise ValueError("Selected columns list cannot be empty.")
        # Build the comma-separated string of selected columns
        columns_str = ", ".join(selected_columns)
        # Ensure that the dates are in the correct format
        start_date = datetime.strptime(fromDate, "%d/%m/%Y").strftime("%Y-%m-%d")
        end_date = datetime.strptime(toDate, "%d/%m/%Y").strftime("%Y-%m-%d")
        # Build and execute the SQL query with date range filter
        query = f'SELECT {columns_str} FROM {self.table_name} WHERE created_at BETWEEN ? AND ?'

        self.open_cursor()
        self.cursor.execute(query, (start_date, end_date))
        rows = self.cursor.fetchall()
        self.close_cursor()
        return rows
    def fetchSelectedColumns(self, selected_columns, filter_criteria=[], filter_type=None):
        if not selected_columns:
                raise ValueError("Selected columns list cannot be empty.")
                    # Build the comma-separated string of selected columns
        columns_str = ", ".join(selected_columns)

        if (filter_type == "datewise"):
            print("data_list")
            # Ensure that the dates are in the correct format
            start_date = datetime.strptime(filter_criteria[0], "%d/%m/%Y").strftime("%Y-%m-%d")
            end_date = datetime.strptime(filter_criteria[1], "%d/%m/%Y").strftime("%Y-%m-%d")
            # Build and execute the SQL query with date range filter
            query = f'SELECT {columns_str} FROM {self.table_name} WHERE created_at BETWEEN ? AND ?'

            self.open_cursor()
            self.cursor.execute(query, (start_date, end_date))
            rows = self.cursor.fetchall()
            self.close_cursor()
            return rows
        elif (filter_type == "vehiclewise"):
            # Build and execute the SQL query
            query = f'SELECT {columns_str} FROM {self.table_name} WHERE vehicle_no = ?'
            self.open_cursor()
            self.cursor.execute(query, (filter_criteria[0],))  # Pass vehicleNo as a single-element tuple
            rows = self.cursor.fetchall()
            self.close_cursor()
            return rows
        elif (filter_type == "partywise"):
            # Build and execute the SQL query
            query = f'SELECT {columns_str} FROM {self.table_name} WHERE party_name = ?'
            self.open_cursor()
            self.cursor.execute(query, (filter_criteria[0],))  # Pass vehicleNo as a single-element tuple
            rows = self.cursor.fetchall()
            self.close_cursor()
            return rows

        else:
            # Build and execute the SQL query
            query = f'SELECT {columns_str} FROM {self.table_name}'
            self.open_cursor()
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            self.close_cursor()
            return rows


    def check_if_exists(self, serialNumber):
        self.open_cursor()
        self.cursor.execute("SELECT 1 FROM {} WHERE serial_number = ?".format(self.table_name), (serialNumber,))
        row = self.cursor.fetchone()
        if row:
            return True
        else:
            return None
        # def getColumnData(self, ColumnName):
        #     self.open_cursor()
        #     self.cursor.execute(f"""SELECT DISTINCT {ColumnName}  FROM {self.table_name};""")
        #     # row = [item[0] for item in self.cursor.fetchall()]
        #     # row.insert(0,"")
        #     rows = [item[0] for item in self.cursor.fetchall() if item[0] is not "" and item[0] != ""]
        #     rows.insert(0,"")
            
        #     return rows
    def getColumnData(self, ColumnName):
        self.open_cursor()
        self.cursor.execute(f"""SELECT DISTINCT {ColumnName} FROM {self.table_name};""")
        rows = [item[0] for item in self.cursor.fetchall() if item[0] != ""]  # Use != for comparison
        rows.insert(0, "")
        return rows
# if __name__ == "__main__":
    # app = DatabaseOperations()
