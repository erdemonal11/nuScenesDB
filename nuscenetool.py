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
        self.geometry("1000x600")  # Increased the size to allow more space for columns
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)  # Disable resizing
        self.iconbitmap("MDU_logo.ico")  # Set the app icon to the correct MDU logo

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
                                             hover_color="#17a2b8", fg_color="#0275d8")
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
        """Disconnect from the database."""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.connection_button.configure(text="Connect to DB", fg_color="#17a2b8", hover_color="#4CAF50")
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
        """Show a unified form for creating/updating records."""
        table_name = self.table_var.get()
        if not table_name:
            messagebox.showwarning("No Table Selected", "Please select a table first.")
            return

        # Create a new top-level window for input form
        form_window = ctk.CTkToplevel(self)
        form_window.title("Create Record" if is_create else "Update Record")
        form_window.geometry("400x500")
        form_window.resizable(False, False)  # Disable resizing for the form window
        form_window.iconbitmap("MDU_logo.ico")  # Set the icon

        cursor = self.connection.cursor()
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = [desc[0] for desc in cursor.fetchall()]

        entry_vars = {}

        # Centering elements in form_window
        form_window.grid_columnconfigure(0, weight=1)
        form_window.grid_columnconfigure(1, weight=1)

        # Display input fields for all columns
        for i, col in enumerate(columns):
            label = ctk.CTkLabel(form_window, text=col)
            label.grid(row=i, column=0, padx=10, pady=10, sticky="e")
            entry_var = ctk.StringVar()
            entry = ctk.CTkEntry(form_window, textvariable=entry_var)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")

            # If updating, prefill with the current value
            if record_values:
                entry_var.set(record_values[i])

            entry_vars[col] = entry_var

        # Frame for table schema
        schema_frame = ctk.CTkFrame(form_window, corner_radius=10, fg_color="#2e2e2e")
        schema_frame.grid(row=len(columns) + 1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        schema_frame.grid_columnconfigure(0, weight=1)

        # Fetch and display the table schema at the bottom
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = '{table_name}';
        """)
        schema_info = "\n".join(
            [f"{col[0]} {col[1]}{' PRIMARY KEY' if col[0] == columns[0] else ''}" for col in cursor.fetchall()]
        )

        schema_label = ctk.CTkLabel(schema_frame, text=f"Table Schema:\n{schema_info}", justify="left")
        schema_label.grid(row=0, column=0, padx=10, pady=10)

        def submit_form():
            """Submit the form values to the database."""
            # Check for empty fields
            if is_create and any(not entry_vars[col].get().strip() for col in columns):
                messagebox.showerror("Error", "All fields must be filled!")
                return

            try:
                values = [entry_vars[col].get() for col in columns]
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
                form_window.destroy()
                self.load_table_data(table_name)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to {'create' if is_create else 'update'} record: {e}")

            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()

        submit_button = ctk.CTkButton(form_window, text="Submit", command=submit_form)
        submit_button.grid(row=len(columns), column=0, columnspan=2, padx=10, pady=10)

if __name__ == '__main__':
    app = CRUDApp()
    app.mainloop()
