import sys, os
sys.path.insert(0, r'c:/Users/ram com/Downloads/SQL-Project/Part2/Python App')
os.environ['USE_DEMO_DB'] = '1'
from db_connection import get_db_connection
print('get_db_connection imported')
db = get_db_connection()
print('Got instance:', type(db))
conn = db.connect()
print('Connected, connection type:', type(conn))
db.close()
print('Closed')
