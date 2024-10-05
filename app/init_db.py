import sqlite3

connection = sqlite3.connect('alive_info.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

#cur.execute("INSERT INTO messages (name, value, client) VALUES (?, ?, ?)",
#            ('test', 'test', 'test')
#            )

connection.commit()
connection.close()