import sqlite3
import pandas as pd

def explore_sqlite_database(db_path):
    """
    Function to explore the contents of an SQLite database.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        print(f"Successfully connected to {db_path}")
        
        # Get list of all tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\nTables in the database: {[table[0] for table in tables]}")
        
        # Explore each table
        for table in tables:
            table_name = table[0]
            print(f"\n--- Table: {table_name} ---")
            
            # Get schema information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"Row count: {row_count}")
            
            # Display sample data (first 5 rows)
            query = f"SELECT * FROM {table_name} LIMIT 5"
            df = pd.read_sql_query(query, conn)
            print("\nSample data:")
            print(df)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Function to query specific tables
def query_table(db_path, table_name, limit=None):
    """
    Function to query a specific table in the database.
    
    Args:
        db_path (str): Path to the SQLite database file
        table_name (str): Name of the table to query
        limit (int, optional): Limit the number of rows returned
    
    Returns:
        DataFrame: A pandas DataFrame containing the query results
    """
    try:
        conn = sqlite3.connect(db_path)
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error querying table {table_name}: {e}")
        return None

# Example usage
if __name__ == "__main__":
    db_path = "data/USDH.db"
    
    # Explore the entire database
    explore_sqlite_database(db_path)
    
    # Optional: Query specific tables with more rows if needed
    # books_data = query_table(db_path, "books", limit=10)
    # courses_data = query_table(db_path, "courses", limit=10)
    # courses2_data = query_table(db_path, "courses2", limit=10)
    # scholarships_data = query_table(db_path, "scholarships", limit=10)
    
    # # Display the specific data if needed
    # print("\nMore books data:")
    # print(books_data)