import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agritech.settings')
django.setup()

def execute_sql_file(file_path):
    with open(file_path, 'r') as f:
        sql = f.read()
    
    with connection.cursor() as cursor:
        # Split the SQL into individual statements
        statements = sql.split(';')
        for statement in statements:
            if statement.strip():
                print(f"Executing: {statement[:50]}...")
                cursor.execute(statement)
    
    print(f"Executed SQL from {file_path}")

# Execute SQL files in order
try:
    execute_sql_file('sql_data/01_users.sql')
    execute_sql_file('sql_data/02_farmers_and_products.sql')
    execute_sql_file('sql_data/03_sponsors.sql')
    execute_sql_file('sql_data/04_sponsorships.sql')
    execute_sql_file('sql_data/05_transactions_and_ratings.sql')
    print("All SQL files executed successfully!")
except Exception as e:
    print(f"Error executing SQL: {e}")
