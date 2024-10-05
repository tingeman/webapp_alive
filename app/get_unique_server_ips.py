import sqlite3
import pandas as pd

def get_db_connection():
    conn = sqlite3.connect('alive_info.db')
    conn.row_factory = sqlite3.Row
    return conn
	
conn = get_db_connection()
#messages = conn.execute('SELECT * FROM messages').fetchall()
#conn.close()

df = pd.read_sql('SELECT * FROM messages', conn)
conn.close()

df[df['name']=='public_ip'].sort_values(by=['created','client']).drop(columns='id')

df_ips = df[df['name']=='public_ip']

df_ips_unique = df_ips.drop_duplicates(subset=['value','client'], keep='last')



