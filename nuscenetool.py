import csv
import customtkinter as ctk
from tkinter import ttk, messagebox
import psycopg2
import os
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class CRUDApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("nuScenes DB Tool")
        self.geometry("700x600")
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)
        self.iconbitmap("MDU_logo.ico")

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

        self.create_button = ctk.CTkButton(self.crud_frame, text="Insert", command=self.create_record, width=100,
                                           hover_color="#28a745", fg_color="#5cb85c")
        self.create_button.grid(row=0, column=0, padx=10, pady=10)

        self.update_button = ctk.CTkButton(self.crud_frame, text="Update", command=self.update_record, width=100,
                                           hover_color="#ffc107", fg_color="#f0ad4e")
        self.update_button.grid(row=0, column=1, padx=10, pady=10)

        self.delete_button = ctk.CTkButton(self.crud_frame, text="Delete", command=self.delete_record, width=100,
                                           hover_color="#dc3545", fg_color="#d9534f")
        self.delete_button.grid(row=0, column=2, padx=10, pady=10)

        self.download_button = ctk.CTkButton(self.crud_frame, text="Download DB", command=self.show_download_popup,
                                             width=100, hover_color="#17a2b8", fg_color="#0275d8", state="disabled")
        self.download_button.grid(row=0, column=3, padx=10, pady=10)

        self.grid_rowconfigure(2, weight=0)

    def toggle_connection(self):
        if self.connection is None:
            self.show_connection_popup()
        else:
            self.disconnect_from_db()

    def show_connection_popup(self):
        self.popup_window = ctk.CTkToplevel(self)
        self.popup_window.title("Database Connection")
        self.popup_window.geometry("400x350")
        self.popup_window.resizable(False, False)
        self.popup_window.iconbitmap("MDU_logo.ico")

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
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=20)

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
                self.tree.delete(*self.tree.get_children())
                self.table_var.set("Select a table")
                self.table_menu.configure(values=[])
                messagebox.showinfo("Disconnected", "Database connection closed successfully.")
            else:
                messagebox.showwarning("Warning", "No active connection to disconnect.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to disconnect: {e}")

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
        self.popup_window.title("Download Format")
        self.popup_window.geometry("300x150")
        self.popup_window.resizable(False, False)
        self.popup_window.iconbitmap("MDU_logo.ico")

        frame = ctk.CTkFrame(self.popup_window)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        label = ctk.CTkLabel(frame, text="Choose the format to download:", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=10)

        sql_button = ctk.CTkButton(frame, text="Download as SQL", command=lambda: self.download_database("sql"))
        sql_button.grid(row=1, column=0, padx=10, pady=10)

        csv_button = ctk.CTkButton(frame, text="Download as CSV", command=lambda: self.download_database("csv"))
        csv_button.grid(row=1, column=1, padx=10, pady=10)

    def download_database(self, file_type):
        if not self.check_connection():
            return

        # For SQL, we dump the whole database, but for CSV, we only dump the selected table
        table_name = self.table_var.get()

        if file_type == "csv" and (table_name == "Select a table" or not table_name):
            messagebox.showwarning("No Table Selected", "Please select a table before downloading as CSV.")
            return

        host = self.entry_vars['host'].get()
        port = self.entry_vars['port'].get()
        database = self.entry_vars['database'].get()
        user = self.entry_vars['user'].get()
        password = self.entry_vars['password'].get()

        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

        if file_type == "sql":
            # For SQL, we dump the entire database, not just the selected table
            pg_dump_path = "C:/PostgreSQL/bin/pg_dump.exe"
            dump_file_path = os.path.join(desktop_path, "nuSceneDB.sql")
            dump_command = f'"{pg_dump_path}" --dbname=postgresql://{user}:{password}@{host}:{port}/{database} -F c -b -v -f "{dump_file_path}"'

            try:
                subprocess.run(dump_command, shell=True, check=True)
                messagebox.showinfo("Success", f"Database successfully downloaded as '{os.path.basename(dump_file_path)}' on your Desktop!")
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to download the database: {e}")

        elif file_type == "csv":
            # For CSV, we can only dump a single table (selected in the dropdown)
            dump_file_path = os.path.join(desktop_path, f"{table_name}_nuSceneDB.csv")

            try:
                cursor = self.connection.cursor()
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                with open(dump_file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(columns)  # Write headers
                    writer.writerows(rows)    # Write data rows

                messagebox.showinfo("Success", f"CSV successfully downloaded as '{os.path.basename(dump_file_path)}' on your Desktop!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download CSV: {e}")
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

        self.show_form_dialog(is_create=True)

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
        form_window.iconbitmap("MDU_logo.ico")  

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
