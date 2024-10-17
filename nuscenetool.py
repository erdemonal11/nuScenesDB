import csv
import customtkinter as ctk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import psycopg2
import os
import subprocess
from tabulate import tabulate

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class CRUDApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("nuScenes DB Tool")
        self.geometry("700x600")
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.connection = None
        self.tables = []
        self.selected_table = None
        self.sorting_order = {}
        self.db_config = {}
        self.primary_key_emoji = "🔑"
        self.foreign_key_emoji = "🔗"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.connection_button = ctk.CTkButton(self, text="Connect to DB", command=self.toggle_connection,
                                               hover_color="#17a2b8", width=200)
        self.connection_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.table_var = ctk.StringVar(value="Select a table")
        self.table_menu = ctk.CTkOptionMenu(self, variable=self.table_var, values=[],
                                            command=self.load_table_data, width=150)
        self.table_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.table_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#2e2e2e")
        self.table_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

        self.tree = ttk.Treeview(self.table_frame, show='headings')
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Button-1>", self.handle_click)

        self.scrollbar_y = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar_y.set)
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")

        self.scrollbar_x = ctk.CTkScrollbar(self.table_frame, orientation="horizontal", command=self.tree.xview)
        self.tree.configure(xscroll=self.scrollbar_x.set)
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")

        self.crud_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#2e2e2e")
        self.crud_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.crud_frame.grid_columnconfigure(0, weight=1)
        self.crud_frame.grid_columnconfigure(1, weight=1)
        self.crud_frame.grid_columnconfigure(2, weight=1)
        self.crud_frame.grid_columnconfigure(3, weight=1)
        self.crud_frame.grid_columnconfigure(4, weight=1)

        self.create_button = ctk.CTkButton(self.crud_frame, text="Insert", command=self.create_record, width=100,
                                           hover_color="#28a745", fg_color="#5cb85c")
        self.create_button.grid(row=0, column=0, padx=10, pady=10)

        self.update_button = ctk.CTkButton(self.crud_frame, text="Update", command=self.update_record, width=100,
                                           hover_color="#ffc107", fg_color="#f0ad4e")
        self.update_button.grid(row=0, column=1, padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.crud_frame, text="Delete", command=self.delete_record, width=100,
                                           hover_color="#dc3545", fg_color="#d9534f")
        self.delete_button.grid(row=0, column=2, padx=10, pady=10)

        self.download_button = ctk.CTkButton(self.crud_frame, text="Export DB", command=self.show_download_popup,
                                             width=100, hover_color="#17a2b8", fg_color="#0275d8", state="disabled")
        self.download_button.grid(row=0, column=3, padx=10, pady=10)

        self.sql_button = ctk.CTkButton(self.crud_frame, text="🔍 SQL", command=self.open_sql_query_window,
                                        width=100, hover_color="#17a2b8", fg_color="#0275d8", state="disabled")
        self.sql_button.grid(row=0, column=4, padx=10, pady=10)

        self.grid_rowconfigure(2, weight=0)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
            self.destroy()

    def toggle_connection(self):
        if self.connection is None:
            self.show_connection_popup()
        else:
            self.disconnect_from_db()

    def show_connection_popup(self):
        self.popup_window = ctk.CTkToplevel(self)
        self.popup_window.title("Database Connection")
        self.popup_window.geometry("360x350")
        self.popup_window.resizable(False, False)

        frame = ctk.CTkFrame(self.popup_window)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        labels = ["Host", "Port", "Database", "User", "Password"]
        self.entry_vars = {}
        for i, label in enumerate(labels):
            lbl = ctk.CTkLabel(frame, text=label, font=("Arial", 14))
            lbl.grid(row=i, column=0, padx=10, pady=10, sticky="e")

            entry_var = ctk.StringVar()
            entry = ctk.CTkEntry(frame, textvariable=entry_var, font=("Arial", 14), width=200)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="w")

            if label == "Password":
                entry.configure(show="*")

            self.entry_vars[label.lower()] = entry_var

        button_frame = ctk.CTkFrame(frame)
        button_frame.grid(row=len(labels), column=0, columnspan=30, pady=20)

        submit_button = ctk.CTkButton(button_frame, text="Submit", command=self.connect_to_db_from_popup)
        submit_button.grid(row=0, column=0, padx=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.popup_window.destroy)
        cancel_button.grid(row=0, column=1, padx=10)

    def connect_to_db_from_popup(self):
        host = self.entry_vars['host'].get()
        port = self.entry_vars['port'].get()
        database = self.entry_vars['database'].get()
        user = self.entry_vars['user'].get()
        password = self.entry_vars['password'].get()

        if not all([host, port, database, user, password]):
            messagebox.showwarning("Missing Details", "All fields are required!")
            return

        try:
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )

            cursor = self.connection.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            self.tables = [table[0] for table in cursor.fetchall()]

            self.table_menu.configure(values=self.tables)
            self.download_button.configure(state="normal")
            self.sql_button.configure(state="normal")
            self.connection_button.configure(text="Remove Connection", fg_color="#dc3545", hover_color="#ff4d4d")
            messagebox.showinfo("Success", "Connected to the database successfully!")
            self.popup_window.destroy()

        except Exception as e:
            self.connection = None
            self.connection_button.configure(text="Connect to DB", fg_color="#17a2b8", hover_color="#4CAF50")
            messagebox.showerror("Error", f"Failed to connect to database: {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def disconnect_from_db(self):
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.connection_button.configure(text="Connect to DB", fg_color="#17a2b8", hover_color="#4CAF50")
                self.download_button.configure(state="disabled")
                self.sql_button.configure(state="disabled")
                self.tree.delete(*self.tree.get_children())
                self.tree["columns"] = []
                self.tree.configure(columns=[])
                self.table_var.set("Select a table")
                self.table_menu.configure(values=[])

                messagebox.showinfo("Disconnected", "Database connection closed successfully.")
            else:
                messagebox.showwarning("Warning", "No active connection to disconnect.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect: {e}")

    def open_sql_query_window(self):
        if not self.check_connection():
            return

        query_window = ctk.CTkToplevel(self)
        query_window.title("SQL Command Line")
        query_window.geometry("600x470")
        query_window.resizable(False, False)

        frame = ctk.CTkFrame(query_window)
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        frame.grid_columnconfigure(0, weight=1)

        query_label = ctk.CTkLabel(frame, text="SQL Query", font=("Arial", 14))
        query_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.query_entry = scrolledtext.ScrolledText(frame, wrap="word", height=8, font=("Consolas", 12))
        self.query_entry.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        output_label = ctk.CTkLabel(frame, text="Query Output", font=("Arial", 14))
        output_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.output_text = scrolledtext.ScrolledText(frame, wrap="word", height=10, font=("Consolas", 12), state='disabled')
        self.output_text.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        button_frame = ctk.CTkFrame(frame)
        button_frame.grid(row=4, column=0, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        run_button = ctk.CTkButton(button_frame, text="Run", command=self.execute_sql_query, hover_color="#28a745", fg_color="#5cb85c")
        run_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        clear_button = ctk.CTkButton(button_frame, text="Clear", command=self.clear_sql_query, hover_color="#ffc107", fg_color="#f0ad4e")
        clear_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        save_button = ctk.CTkButton(button_frame, text="Save to CSV", command=self.save_to_csv, hover_color="#17a2b8", fg_color="#0275d8")
        save_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

    def execute_sql_query(self):
        query = self.query_entry.get("1.0", "end").strip()
        if not query:
            messagebox.showwarning("No Query", "Please enter an SQL query.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)

            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                self.query_result = {
                    "columns": columns,
                    "rows": rows
                }

                result = tabulate(rows, headers=columns, tablefmt="pipe", stralign="center")
                self.display_output(result)
            else:
                self.connection.commit()
                self.display_output("Query executed successfully.")
                self.query_result = None

        except Exception as e:
            self.connection.rollback()
            self.display_output(f"Error: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def display_output(self, text):
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, "end")
        self.output_text.insert("end", text)
        self.output_text.config(state="disabled")

    def load_table_from_query(self, columns, rows):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, minwidth=200)

        for idx, row in enumerate(rows):
            tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
            self.tree.insert("", "end", values=row, tags=(tag,))

        self.tree.tag_configure('oddrow', background='#f5f5dc')
        self.tree.tag_configure('evenrow', background='#f0e68c')

    def clear_sql_query(self):
        self.query_entry.delete("1.0", "end")
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, "end")
        self.output_text.config(state="disabled")

    def save_to_csv(self):
        if not hasattr(self, "query_result") or not self.query_result:
            messagebox.showwarning("No Data", "No query results available to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(self.query_result["columns"])
                writer.writerows(self.query_result["rows"])
            messagebox.showinfo("Success", f"Data successfully saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def check_connection(self):
        if not self.connection:
            messagebox.showwarning("No Connection", "Please connect to the database first.")
            return False
        return True

    def load_table_data(self, table_name=None):
        if not self.check_connection():
            return

        if not table_name:
            table_name = self.table_var.get()

        try:
            cursor = self.connection.cursor()
            self.tree.delete(*self.tree.get_children())
            self.tree["columns"] = []

            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
            columns = [desc[0] for desc in cursor.description]

            cursor.execute(f"""
                SELECT
                    kcu.column_name
                FROM
                    information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE
                    tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = '{table_name}';
            """)
            primary_keys = [item[0] for item in cursor.fetchall()]

            cursor.execute(f"""
                SELECT
                    kcu.column_name
                FROM
                    information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE
                    tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table_name}';
            """)
            foreign_keys = [item[0] for item in cursor.fetchall()]

            self.tree["columns"] = columns
            for col in columns:
                header_text = col
                if col in primary_keys:
                    header_text = f"{self.primary_key_emoji} {col}"
                elif col in foreign_keys:
                    header_text = f"{self.foreign_key_emoji} {col}"
                self.tree.heading(col, text=header_text, command=lambda c=col: self.sort_by_column(c, columns, primary_keys, foreign_keys))
                self.tree.column(col, width=200, minwidth=200)

            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            for idx, row in enumerate(rows):
                tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
                self.tree.insert("", "end", values=row, tags=(tag,))

            self.tree.tag_configure('oddrow', background='#f5f5dc')
            self.tree.tag_configure('evenrow', background='#f0e68c')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data: {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def sort_by_column(self, col, columns, primary_keys, foreign_keys):
        order = self.sorting_order.get(col, False)
        self.sorting_order[col] = not order

        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        data.sort(reverse=order)

        for index, (val, item) in enumerate(data):
            self.tree.move(item, "", index)

        for column in columns:
            header_text = column
            if column in primary_keys:
                header_text = f"{self.primary_key_emoji} {column}"
            elif column in foreign_keys:
                header_text = f"{self.foreign_key_emoji} {column}"
            order_symbol = "▲" if self.sorting_order.get(column, False) else "▼"
            self.tree.heading(column, text=f"{header_text} {order_symbol}")

        for idx, item in enumerate(self.tree.get_children("")):
            tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
            self.tree.item(item, tags=(tag,))

    def show_download_popup(self):
        self.popup_window = ctk.CTkToplevel(self)
        self.popup_window.title("Export Format")
        self.popup_window.geometry("360x150")
        self.popup_window.resizable(False, False)

        frame = ctk.CTkFrame(self.popup_window)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        label = ctk.CTkLabel(frame, text="Choose the format to export", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=10)

        sql_button = ctk.CTkButton(frame, text="SQL (DB)", command=lambda: self.download_database("sql"))
        sql_button.grid(row=1, column=0, padx=10, pady=10)

        csv_button = ctk.CTkButton(frame, text="CSV (Table)", command=lambda: self.download_database("csv"))
        csv_button.grid(row=1, column=1, padx=10, pady=10)

    def download_database(self, file_type):
        if not self.check_connection():
            return

        table_name = self.table_var.get()

        if file_type == "csv" and (table_name == "Select a table" or not table_name):
            messagebox.showwarning("No Table Selected", "Please select a table before exporting as CSV.")
            return

        host = self.entry_vars['host'].get()
        port = self.entry_vars['port'].get()
        database = self.entry_vars['database'].get()
        user = self.entry_vars['user'].get()
        password = self.entry_vars['password'].get()

        file_path = filedialog.asksaveasfilename(defaultextension=f".{file_type}", 
                                                filetypes=[(f"{file_type.upper()} files", f"*.{file_type}")],
                                                title=f"Save {file_type.upper()} file")

        if not file_path:
            return

        if file_type == "sql":
            pg_dump_path = "C:/PostgreSQL/bin/pg_dump.exe"
            dump_command = f'"{pg_dump_path}" --dbname=postgresql://{user}:{password}@{host}:{port}/{database} -F c -b -v -f "{file_path}"'

            try:
                subprocess.run(dump_command, shell=True, check=True)
                messagebox.showinfo("Success", f"Database successfully exported as '{os.path.basename(file_path)}'.")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to export the database: {e}")

        elif file_type == "csv":
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(columns)
                    writer.writerows(rows)

                messagebox.showinfo("Success", f"CSV successfully exported as '{os.path.basename(file_path)}'.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {e}")
            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()

        self.popup_window.destroy()

    def handle_click(self, event):
        if self.tree.identify_region(event.x, event.y) == "separator":
            return "break"

    def create_record(self):
        if not self.check_connection():
            return

        table_name = self.table_var.get()

        if table_name == "Select a table" or not table_name:
            messagebox.showwarning("No Table Selected", "Please select a table before creating a record.")
            return

        choice = messagebox.askyesno("Insert Data", "Do you want to import from a CSV file?")

        if choice:
            self.import_from_csv(table_name)
        else:
            self.show_form_dialog(is_create=True)

    def import_from_csv(self, table_name):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Select CSV file to import"
        )
        if not file_path:
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
            db_columns = [desc[0] for desc in cursor.fetchall()]

            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                csv_headers = next(reader)

                if len(csv_headers) != len(db_columns):
                    messagebox.showerror("Column Mismatch", f"CSV has {len(csv_headers)} columns, but the table '{table_name}' expects {len(db_columns)}.")
                    return

                for csv_col, db_col in zip(csv_headers, db_columns):
                    if csv_col != db_col:
                        messagebox.showerror("Column Mismatch", f"CSV column '{csv_col}' does not match table column '{db_col}'.")
                        return

                placeholders = ', '.join(['%s'] * len(db_columns))
                insert_query = f"INSERT INTO {table_name} ({', '.join(db_columns)}) VALUES ({placeholders})"

                for row in reader:
                    if len(row) != len(db_columns):
                        messagebox.showerror("Row Error", f"Row length {len(row)} does not match the expected {len(db_columns)} columns.")
                        return
                    cursor.execute(insert_query, row)

                self.connection.commit()
                messagebox.showinfo("Success", f"Data from {os.path.basename(file_path)} successfully inserted into {table_name}.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def update_record(self):
        if not self.check_connection():
            return
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record to update.")
            return
        values = self.tree.item(selected_item)['values']
        self.show_form_dialog(is_create=False, record_values=values)

    def delete_record(self):
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

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this record?")
        if not confirm:
            return

        try:
            values = self.tree.item(selected_item)['values']
            cursor = self.connection.cursor()

            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
            columns = [desc[0] for desc in cursor.fetchall()]

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
        table_name = self.table_var.get()
        if not table_name or table_name == "Select a table":
            messagebox.showwarning("No Table Selected", "Please select a table first.")
            return

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

        window_size = table_sizes.get(table_name, "400x400")

        form_window = ctk.CTkToplevel(self)
        form_window.title(table_name)
        form_window.geometry(window_size)
        form_window.resizable(False, False)

        cursor = self.connection.cursor()
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = [desc[0] for desc in cursor.fetchall()]

        entry_vars = {}

        form_frame = ctk.CTkFrame(form_window, fg_color="#333333")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        form_title = ctk.CTkLabel(form_frame, text=table_name, font=("Arial", 18, "bold"))
        form_title.grid(row=0, column=0, columnspan=2, pady=20, sticky="n")

        for i, col in enumerate(columns):
            label = ctk.CTkLabel(form_frame, text=col, font=("Arial", 14), anchor="center")
            label.grid(row=i + 1, column=0, padx=10, pady=10, sticky="e")

            entry_var = ctk.StringVar()
            entry = ctk.CTkEntry(form_frame, textvariable=entry_var, font=("Arial", 14), width=200)
            entry.grid(row=i + 1, column=1, padx=10, pady=10, sticky="w")

            if record_values:
                entry_var.set(record_values[i])

            entry_vars[col] = entry_var

        button_frame = ctk.CTkFrame(form_frame, fg_color="#333333", corner_radius=10)
        button_frame.grid(row=len(columns) + 1, column=0, columnspan=2, pady=20)

        submit_button = ctk.CTkButton(button_frame, text="Submit", command=lambda: self.submit_form(is_create, entry_vars, table_name, record_values, form_window), width=120, hover_color="#28a745", fg_color="#5cb85c")
        submit_button.grid(row=0, column=0, padx=10, pady=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=form_window.destroy, width=120, hover_color="#d9534f", fg_color="#dc3545")
        cancel_button.grid(row=0, column=1, padx=10, pady=10)

    def submit_form(self, is_create, entry_vars, table_name, record_values, form_window):
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
            self.load_table_data(table_name)
            form_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit record: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

if __name__ == '__main__':
    app = CRUDApp()
    app.mainloop()
