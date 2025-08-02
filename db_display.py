import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
from tkinter import messagebox

class DatabaseViewer:
    def __init__(self, root, db_path):
        self.root = root
        self.root.title("Database Content Viewer")
        self.root.geometry("1000x600")
        self.db_path = db_path
        
        # Set up the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table selection area
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Database Tables", padding="5")
        self.table_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Get table names
        self.tables = self.get_table_names()
        
        # Create table selection dropdown
        ttk.Label(self.table_frame, text="Select Table:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.table_var = tk.StringVar()
        self.table_combo = ttk.Combobox(self.table_frame, textvariable=self.table_var, values=self.tables, state="readonly", width=30)
        self.table_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.table_combo.bind("<<ComboboxSelected>>", self.load_table_data)
        
        # Search area
        self.search_frame = ttk.LabelFrame(self.main_frame, text="Search", padding="5")
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Search Column:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_col_var = tk.StringVar()
        self.search_col_combo = ttk.Combobox(self.search_frame, textvariable=self.search_col_var, state="readonly", width=20)
        self.search_col_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(self.search_frame, text="Search Text:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_data)
        self.search_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        
        self.reset_button = ttk.Button(self.search_frame, text="Reset", command=self.reset_search)
        self.reset_button.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        
        # Create data display area with a Treeview
        self.data_frame = ttk.LabelFrame(self.main_frame, text="Data", padding="5")
        self.data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview with scrollbars
        self.tree_frame = ttk.Frame(self.data_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree_scroll_y = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=self.tree_scroll_y.set, xscrollcommand=self.tree_scroll_x.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)
        
        # Select the first table by default if available
        if self.tables:
            self.table_combo.current(0)
            self.load_table_data(None)
        
    def get_table_names(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall() if table[0] != 'sqlite_sequence']
            conn.close()
            return tables
        except Exception as e:
            messagebox.showerror("Database Error", f"Error getting tables: {str(e)}")
            return []
    
    def load_table_data(self, event):
        table_name = self.table_var.get()
        if not table_name:
            return
        
        try:
            # Clear existing treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get data from the selected table
            conn = sqlite3.connect(self.db_path)
            query = f"SELECT * FROM '{table_name}' LIMIT 1000"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Update column dropdown for search
            column_names = list(df.columns)
            self.search_col_combo.config(values=column_names)
            if column_names:
                self.search_col_combo.current(0)
            
            # Configure treeview columns
            self.tree['columns'] = column_names
            self.tree.column('#0', width=0, stretch=tk.NO)
            
            # Set up column headings
            for col in column_names:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, stretch=tk.YES)
            
            # Add data to treeview
            for i, row in df.iterrows():
                values = [str(row[col]) if pd.notna(row[col]) else "" for col in column_names]
                self.tree.insert('', tk.END, values=values)
            
            row_count = len(df)
            self.status_var.set(f"Table: {table_name} | Rows: {row_count}")
            
        except Exception as e:
            messagebox.showerror("Data Error", f"Error loading data: {str(e)}")
    
    def search_data(self):
        table_name = self.table_var.get()
        search_col = self.search_col_var.get()
        search_text = self.search_var.get()
        
        if not (table_name and search_col and search_text):
            messagebox.showinfo("Search", "Please select a table, column and enter search text")
            return
        
        try:
            # Clear existing treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get filtered data from the selected table
            conn = sqlite3.connect(self.db_path)
            query = f"SELECT * FROM '{table_name}' WHERE `{search_col}` LIKE ? LIMIT 1000"
            df = pd.read_sql_query(query, conn, params=['%' + search_text + '%'])
            conn.close()
            
            # Add filtered data to treeview
            column_names = list(df.columns)
            for i, row in df.iterrows():
                values = [str(row[col]) if pd.notna(row[col]) else "" for col in column_names]
                self.tree.insert('', tk.END, values=values)
            
            row_count = len(df)
            self.status_var.set(f"Search Results: {row_count} rows match '{search_text}' in '{search_col}'")
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Error searching data: {str(e)}")
    
    def reset_search(self):
        self.search_var.set("")
        self.load_table_data(None)

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseViewer(root, "data/USDH.db")  # Replace with your actual database path
    root.mainloop()