import psycopg2
from psycopg2 import Error

def connect_to_rds():
    try:
        # Connection parameters
        connection = psycopg2.connect(
            host="mydbinstance.cpi8oo84o2my.ap-south-1.rds.amazonaws.com",  # RDS endpoint
            database="masterdatabase",
            user="postgres",
            password="nehruworkshop2025",
            port="5432"  # Default PostgreSQL port
        )

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        
        # Print PostgreSQL details
        print("PostgreSQL server information:")
        print(connection.get_dsn_parameters())
        
        # Execute a test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("Connected to:", version)

        return connection, cursor

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        return None, None

def close_connection(connection, cursor):
    if cursor:
        cursor.close()
    if connection:
        connection.close()
        print("PostgreSQL connection closed")

# Usage example
if __name__ == "__main__":
    connection, cursor = connect_to_rds()
    
    if connection:
        # Perform your database operations here
        
        # Example query
        # cursor.execute("SELECT * FROM your_table;")
        # records = cursor.fetchall()
        
        # Don't forget to close the connection
        close_connection(connection, cursor)