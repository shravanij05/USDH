import sqlite3
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import os

class DatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("USDH Database Viewer")
        self.root.geometry("800x600")
        self.root.configure(bg="#222")
        
        # Configure style for cyberpunk theme
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#111", 
                        foreground="#0ff", 
                        rowheight=25, 
                        fieldbackground="#111")
        style.map('Treeview', background=[('selected', '#0aa')])
        style.configure("TButton", 
                        background="#222", 
                        foreground="#0ff", 
                        borderwidth=1, 
                        focusthickness=3, 
                        focuscolor="#0ff")
        style.map('TButton', background=[('active', '#0aa')])
        
        # Create frame for database selection
        self.db_frame = tk.Frame(root, bg="#222", padx=10, pady=10)
        self.db_frame.pack(fill=tk.X)
        
        # Label and entry for database path
        self.db_label = tk.Label(self.db_frame, text="Database Path:", 
                                 bg="#222", fg="#0ff", font=("Arial", 12))
        self.db_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.db_path = tk.StringVar(value="users.db")
        self.db_entry = tk.Entry(self.db_frame, textvariable=self.db_path, 
                                 bg="#111", fg="#0ff", insertbackground="#0ff",
                                 width=50, font=("Arial", 12))
        self.db_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Connect button
        self.connect_btn = ttk.Button(self.db_frame, text="Connect", 
                                      command=self.connect_to_db)
        self.connect_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Create frame for table selection
        self.table_frame = tk.Frame(root, bg="#222", padx=10, pady=10)
        self.table_frame.pack(fill=tk.X)
        
        # Table selection dropdown
        self.table_label = tk.Label(self.table_frame, text="Select Table:", 
                                    bg="#222", fg="#0ff", font=("Arial", 12))
        self.table_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.table_var = tk.StringVar()
        self.table_dropdown = ttk.Combobox(self.table_frame, textvariable=self.table_var, 
                                           state="readonly", width=30, font=("Arial", 12))
        self.table_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.table_dropdown.bind("<<ComboboxSelected>>", self.load_table_data)
        
        # Refresh button
        self.refresh_btn = ttk.Button(self.table_frame, text="Refresh", 
                                      command=self.refresh_data)
        self.refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Create frame for data display
        self.data_frame = tk.Frame(root, bg="#222", padx=10, pady=10)
        self.data_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for data display
        self.tree = ttk.Treeview(self.data_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        self.vsb = ttk.Scrollbar(self.data_frame, orient="vertical", command=self.tree.yview)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.vsb.set)
        
        self.hsb = ttk.Scrollbar(root, orient="horizontal", command=self.tree.xview)
        self.hsb.pack(fill=tk.X)
        self.tree.configure(xscrollcommand=self.hsb.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, 
                                   bg="#111", fg="#0ff", anchor=tk.W, padx=10, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Try to connect to the default database on startup
        self.connect_to_db()
    
    def connect_to_db(self):
        db_path = self.db_path.get()
        
        if not db_path:
            messagebox.showerror("Error", "Please enter a database path")
            return
        
        if not os.path.exists(db_path):
            messagebox.showerror("Error", f"Database file not found: {db_path}")
            return
        
        try:
            # Connect to the database
            self.conn = sqlite3.connect(db_path)
            
            # Get list of tables
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Update table dropdown
            table_names = [table[0] for table in tables]
            self.table_dropdown['values'] = table_names
            
            if table_names:
                self.table_var.set(table_names[0])
                self.load_table_data(None)
                self.status_var.set(f"Connected to {db_path}")
            else:
                self.status_var.set(f"Connected to {db_path}, but no tables found")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.status_var.set(f"Error: {str(e)}")
    
    def load_table_data(self, event):
        if not hasattr(self, 'conn'):
            return
        
        table_name = self.table_var.get()
        if not table_name:
            return
        
        try:
            # Get table data
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.conn)
            
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Configure columns
            self.tree['columns'] = list(df.columns)
            self.tree['show'] = 'headings'
            
            # Set column headings
            for col in df.columns:
                self.tree.heading(col, text=col)
                # Adjust column width based on content
                max_width = max(
                    df[col].astype(str).map(len).max() * 10,
                    len(str(col)) * 10
                )
                self.tree.column(col, width=max_width, minwidth=100)
            
            # Insert data rows
            for _, row in df.iterrows():
                values = [row[col] for col in df.columns]
                self.tree.insert('', tk.END, values=values)
            
            self.status_var.set(f"Loaded {len(df)} rows from {table_name}")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
            self.status_var.set(f"Error: {str(e)}")
    
    def refresh_data(self):
        self.load_table_data(None)

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseViewer(root)
    root.mainloop()