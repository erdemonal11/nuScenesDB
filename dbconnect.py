import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
database = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

if os.path.exists('/.dockerenv'):
    sql_file_path = '/app/nuScene.sql'
else:
    sql_file_path = r'C:\Users\mrifk\Desktop\nuScenesDB\nuScene.sql'

connection = None
cursor = None

try:
    connection = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    cursor = connection.cursor()

    
    with open(sql_file_path, 'r') as file:
        sql_commands = file.read()

    cursor.execute(sql_commands)
    
    connection.commit()
    print("SQL script executed successfully!")

except Exception as error:
    print(f"An error occurred: {error}")

finally:
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()
