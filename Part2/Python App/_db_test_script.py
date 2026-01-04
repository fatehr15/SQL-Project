import sys
sys.path.insert(0, r'c:/Users/ram com/Downloads/SQL-Project/Part2/Python App')
from db_connection import get_db_connection
from db_connection_demo import get_demo_db_connection
print('Imported modules')
# Test PostgreSQL connection object creation (won't attempt to connect)
db = get_db_connection()
print('DB type:', type(db))
# Test demo connection connect/close
demo = get_demo_db_connection()
print('Demo type:', type(demo))
try:
    demo.connect()
    print('Demo connected OK')
    demo.close()
    print('Demo closed OK')
except Exception as e:
    print('Demo connection error:', e)
