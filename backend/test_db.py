#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import sys
from tabulate import tabulate

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection"""
    try:
        return psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=RealDictCursor
        )
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def execute_query(query):
    """Execute query and return results"""
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                
                # If SELECT query, fetch and display results
                if query.strip().lower().startswith('select'):
                    results = cur.fetchall()
                    if results:
                        # Convert results to list of dicts
                        columns = [desc[0] for desc in cur.description]
                        table_data = [[row[col] for col in columns] for row in results]
                        
                        # Print results in table format
                        print("\nQuery Results:")
                        print(tabulate(table_data, headers=columns, tablefmt="psql"))
                        print(f"\nTotal rows: {len(results)}")
                    else:
                        print("No results found")
                else:
                    # For INSERT, UPDATE, DELETE show affected rows
                    print(f"Query executed successfully. Rows affected: {cur.rowcount}")
                
    except psycopg2.Error as e:
        print(f"Error executing query: {e}")
    finally:
        conn.close()

def main():
    if len(sys.argv) > 1:
        # Execute query from command line argument
        query = " ".join(sys.argv[1:])
    else:
        # Get query from user input
        query = input("Enter your SQL query: ")
    
    if query.strip().lower() in ['exit', 'quit', 'q']:
        sys.exit(0)
        
    execute_query(query)

if __name__ == "__main__":
    main()