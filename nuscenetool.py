import customtkinter as ctk
from tkinter import ttk, messagebox
import psycopg2
import os
from dotenv import load_dotenv
import subprocess  # For running the pg_dump command

# Load environment variables from .env file
load_dotenv()

# CustomTkinter setup
ctk.set_appearance_mode("dark")  # Default to dark mode
ctk.set_default_color_theme("green")


class CRUDApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.title("nuScenes DB Tool")
        self.geometry("700x600")  # Increased the size to allow more space for columns
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)  # Disable resizing
        self.iconbitmap("MDU_logo.ico")  # Ensure the path to the logo is correct

        # Variables
        self.connection = None
        self.tables = []
        self.selected_table = None
        self.sorting_order = {}

        # Configure grid layout for responsiveness
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Connect to DB and Select Table buttons in the same row, center-aligned
        self.connection_button = ctk.CTkButton(self, text="Connect to DB", command=self.toggle_connection,
                                               hover_color="#17a2b8", width=200)  # Keep button width fixed at 200px
        self.connection_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.table_var = ctk.StringVar(value="Select a table")
        self.table_menu = ctk.CTkOptionMenu(self, variable=self.table_var, values=[],
                                            command=self.load_table_data, width=150)  # Set a wider width
        self.table_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Center both the Connect and Select Table buttons by spanning both columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Frame for displaying table data
        self.table_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#2e2e2e")
        self.table_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        # Treeview to display data from the table with larger font and minimum width for each column
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=25)  # Increase font size and row height
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))  # Increase header font size

        self.tree = ttk.Treeview(self.table_frame, show='headings')
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Button-1>", self.handle_click)  # Bind click events to handle_click

        # Scrollbars for Treeview (vertical and horizontal)
        self.scrollbar_y = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar_y.set)
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")

        self.scrollbar_x = ctk.CTkScrollbar(self.table_frame, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(xscroll=self.scrollbar_x.set)
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Frame for CRUD buttons (center horizontally, at the very bottom)
        self.crud_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#2e2e2e")
        self.crud_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.crud_frame.grid_columnconfigure(0, weight=1)
        self.crud_frame.grid_columnconfigure(1, weight=1)
        self.crud_frame.grid_columnconfigure(2, weight=1)
        self.crud_frame.grid_columnconfigure(3, weight=1)

        # Update button order: Create, Update, Delete, Download
        self.create_button = ctk.CTkButton(self.crud_frame, text="Create", command=self.create_record, width=100,
                                           hover_color="#28a745", fg_color="#5cb85c")
        self.create_button.grid(row=0, column=0, padx=10, pady=10)

        self.update_button = ctk.CTkButton(self.crud_frame, text="Update", command=self.update_record, width=100,
                                           hover_color="#ffc107", fg_color="#f0ad4e")
        self.update_button.grid(row=0, column=1, padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.crud_frame, text="Delete", command=self.delete_record, width=100,
                                           hover_color="#dc3545", fg_color="#d9534f")
        self.delete_button.grid(row=0, column=2, padx=10, pady=10)

        self.download_button = ctk.CTkButton(self.crud_frame, text="Download DB", command=self.download_database, width=100,
                                             hover_color="#17a2b8", fg_color="#0275d8", state="disabled")
        self.download_button.grid(row=0, column=3, padx=10, pady=10)

        # Force the CRUD frame to the bottom of the app, removing unnecessary space
        self.grid_rowconfigure(2, weight=0)

    def toggle_connection(self):
        """Toggle between connecting and disconnecting from the database."""
        if self.connection is None:
            self.connect_to_db()
        else:
            self.disconnect_from_db()

    def connect_to_db(self):
        """Connect to PostgreSQL database using psycopg2 and fetch all tables."""
        host = os.getenv('DB_HOST', '127.0.0.1')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')

        try:
            if not password:
                raise ValueError("Database password not provided!")

            # Connect to PostgreSQL using psycopg2
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )

            # Fetch all tables from the database
            cursor = self.connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            self.tables = [table[0] for table in cursor.fetchall()]

            # Update table dropdown
            self.table_menu.configure(values=self.tables)

            # Enable download button after successful connection
            self.download_button.configure(state="normal")

            # Change button text to "Remove Connection"
            self.connection_button.configure(text="Remove Connection", fg_color="#dc3545", hover_color="#ff4d4d")
            messagebox.showinfo("Success", "Connected to the database successfully!")

        except Exception as e:
            self.connection = None
            self.connection_button.configure(text="Connect to DB", fg_color="#17a2b8", hover_color="#4CAF50")
            messagebox.showerror("Error", f"Failed to connect to database: {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def disconnect_from_db(self):
        """Disconnect from the database and reset table data."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.connection_button.configure(text="Connect to DB", fg_color="#17a2b8", hover_color="#4CAF50")

                # Disable download button when disconnected
                self.download_button.configure(state="disabled")

                # Clear the Treeview and reset table selection
                self.tree.delete(*self.tree.get_children())  # Clear table data
                self.table_var.set("Select a table")  # Reset the option menu to "Select a table"
                self.table_menu.configure(values=[])  # Clear the table list in the option menu

                messagebox.showinfo("Disconnected", "Database connection closed successfully.")
            else:
                messagebox.showwarning("Warning", "No active connection to disconnect.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect: {e}")

    def check_connection(self):
        """Ensure there's an active connection before CRUD actions."""
        if not self.connection:
            messagebox.showwarning("No Connection", "Please connect to the database first.")
            return False
        return True

    def load_table_data(self, table_name=None):
        """Load selected table data into the Treeview."""
        if not self.check_connection():
            return

        if not table_name:
            table_name = self.table_var.get()

        try:
            cursor = self.connection.cursor()

            # Clear existing Treeview data
            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = []

            # Fetch the table columns
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            columns = [desc[0] for desc in cursor.description]
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
                self.tree.column(col, width=200, minwidth=200)  # Set generous minwidth to avoid squeezing

            # Fetch table data
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            # Insert records into Treeview
            for row in rows:
                self.tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data: {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def sort_by_column(self, col):
        """Sort the rows by the clicked column."""
        # Get current sorting order
        order = self.sorting_order.get(col, False)
        self.sorting_order[col] = not order  # Toggle sorting order

        # Sort data in the Treeview
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        data.sort(reverse=order)

        for index, (val, item) in enumerate(data):
            self.tree.move(item, "", index)

        # Update headings with sorting indicators only after clicking
        for column in self.tree["columns"]:
            if column == col:
                order_symbol = "▲" if self.sorting_order[col] else "▼"
                self.tree.heading(column, text=f"{column} {order_symbol}")
            else:
                self.tree.heading(column, text=column)  # Reset others to normal

    def download_database(self):
        """Download the entire PostgreSQL database as a SQL file on the Desktop."""
        if not self.check_connection():
            return

        host = os.getenv('DB_HOST', '127.0.0.1')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')

        # Get the desktop path for the current user
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

        # Use the full path to pg_dump
        pg_dump_path = "C:/PostgreSQL/bin/pg_dump.exe"
        
        # Create the command for pg_dump to dump the entire database to the desktop
        dump_file_path = os.path.join(desktop_path, "nuSceneDB.sql")
        dump_command = f'"{pg_dump_path}" --dbname=postgresql://{user}:{password}@{host}:{port}/{database} -F c -b -v -f "{dump_file_path}"'

        try:
            # Execute the pg_dump command
            subprocess.run(dump_command, shell=True, check=True)
            messagebox.showinfo("Success", f"Database successfully downloaded as 'nuSceneDB.sql' on your Desktop!")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to download the database: {e}")

    def handle_click(self, event):
        """Handle click event to prevent resizing of columns."""
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"

    def create_record(self):
        """Create a new record in the selected table."""
        if not self.check_connection():
            return

        table_name = self.table_var.get()

        if table_name == "Select a table" or not table_name:
            messagebox.showwarning("No Table Selected", "Please select a table before creating a record.")
            return

        self.show_form_dialog(is_create=True)

    def update_record(self):
        """Update a selected record in the table."""
        if not self.check_connection():
            return
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to update.")
            return
        # Get selected record values
        values = self.tree.item(selected_item)['values']
        self.show_form_dialog(is_create=False, record_values=values)

    def delete_record(self):
        """Delete a selected record from the table with confirmation."""
        if not self.check_connection():
            return

        table_name = self.table_var.get()
        if not table_name:
            messagebox.showwarning("No Table Selected", "Please select a table first.")
            return

        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to delete.")
            return

        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this record?")
        if not confirm:
            return

        try:
            # Get selected record values
            values = self.tree.item(selected_item)['values']
            cursor = self.connection.cursor()

            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
            columns = [desc[0] for desc in cursor.fetchall()]

            # Delete the selected record based on the primary key
            sql = f"DELETE FROM {table_name} WHERE {columns[0]} = %s;"
            cursor.execute(sql, [values[0]])
            self.connection.commit()
            messagebox.showinfo("Success", f"Record deleted from {table_name} successfully!")
            self.load_table_data(table_name)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record: {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def show_form_dialog(self, is_create=True, record_values=None):
        """Show a unified form for creating/updating records with dynamic sizing based on table name."""
        table_name = self.table_var.get()
        if not table_name or table_name == "Select a table":
            messagebox.showwarning("No Table Selected", "Please select a table first.")
            return

        # Define window sizes for each table
        table_sizes = {
            "sample_data": "450x760",
            "instance": "420x430",
            "scene": "420x520",
            "map": "350x350",
            "sensor": "390x350",
            "log": "380x370",
            "attribute": "390x350",
            "visibility": "380x350",
            "calibrated_sensor": "410x400",
            "sample": "410x440",
            "ego_pose": "410x370",
            "category": "410x370",
            "lidarseg": "420x350",
            "sample_annotation": "450x760",
        }

        # Get the window size based on the table name, default to 400x400 if not found
        window_size = table_sizes.get(table_name, "400x400")

        # Create a new top-level window for the input form
        form_window = ctk.CTkToplevel(self)
        form_window.title(table_name)  # Display the entity (table name) in the title
        form_window.geometry(window_size)  # Set window size dynamically based on the table
        form_window.resizable(False, False)  # Disable resizing for the form window

        # Set the MDU logo icon, adjust the path as needed
        form_window.iconbitmap("MDU_logo.ico")  

        cursor = self.connection.cursor()
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = [desc[0] for desc in cursor.fetchall()]

        entry_vars = {}

        # Container frame for the form content
        form_frame = ctk.CTkFrame(form_window, fg_color="#333333")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        form_title = ctk.CTkLabel(form_frame, text=table_name, font=("Arial", 18, "bold"))
        form_title.grid(row=0, column=0, columnspan=2, pady=20, sticky="n")

        # Centering the labels and entry fields
        for i, col in enumerate(columns):
            label = ctk.CTkLabel(form_frame, text=col, font=("Arial", 14), anchor="center")
            label.grid(row=i + 1, column=0, padx=10, pady=10, sticky="e")

            entry_var = ctk.StringVar()
            entry = ctk.CTkEntry(form_frame, textvariable=entry_var, font=("Arial", 14), width=200)  # Adjusted width
            entry.grid(row=i + 1, column=1, padx=10, pady=10, sticky="w")

            # If updating, prefill with the current value
            if record_values:
                entry_var.set(record_values[i])

            entry_vars[col] = entry_var

        # Submit and Cancel Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="#333333", corner_radius=10)
        button_frame.grid(row=len(columns) + 1, column=0, columnspan=2, pady=20)

        submit_button = ctk.CTkButton(button_frame, text="Submit", command=lambda: self.submit_form(is_create, entry_vars, table_name, record_values), width=120, hover_color="#28a745", fg_color="#5cb85c")
        submit_button.grid(row=0, column=0, padx=10, pady=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=form_window.destroy, width=120, hover_color="#d9534f", fg_color="#dc3545")
        cancel_button.grid(row=0, column=1, padx=10, pady=10)

    def submit_form(self, is_create, entry_vars, table_name, record_values):
        """Submit the form values to the database."""
        cursor = self.connection.cursor()
        columns = list(entry_vars.keys())
        values = [entry_vars[col].get() for col in columns]

        try:
            if is_create:
                placeholders = ", ".join(["%s"] * len(columns))
                sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders});"
                cursor.execute(sql, values)
            else:
                set_clause = ", ".join([f"{col} = %s" for col in columns])
                sql = f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s;"
                cursor.execute(sql, values + [record_values[0]])
            self.connection.commit()
            messagebox.showinfo("Success", f"Record {'created' if is_create else 'updated'} successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit record: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()


if __name__ == '__main__':
    app = CRUDApp()
    app.mainloop()
