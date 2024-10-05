import psycopg2
import os

# Database connection parameters from environment variables
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '5432')
database = os.getenv('DB_NAME', 'nuScene')
user = os.getenv('DB_USER', 'erdem')
password = os.getenv('DB_PASSWORD', 'erdem')

# Path to your SQL file
sql_file_path = '/app/nuScene.sql'

# Initialize variables
connection = None
cursor = None

try:
    # Connect to the PostgreSQL server
    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    # Create a cursor object
    cursor = connection.cursor()

    # Read the SQL file
    with open(sql_file_path, 'r') as file:
        sql_commands = file.read()

    # Execute the SQL commands
    cursor.execute(sql_commands)
    
    # Commit the changes
    connection.commit()
    print("SQL script executed successfully!")

except Exception as error:
    print(f"An error occurred: {error}")

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()
