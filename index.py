from flask import Flask, request, render_template
import sqlite3

server = Flask(__name__)  # object to be referenced by WSGI handler

server.config["TEMPLATES_AUTO_RELOAD"] = True

def get_db_connection():
    conn = sqlite3.connect('alive_info.db')
    conn.row_factory = sqlite3.Row
    return conn


@server.route("/")
def hello():
    return "Hello World!"

@server.route('/submit_data', methods=['POST'])
def submit_data():
#    return 'response'
    resp = []
    try:
        request_data = request.get_json()
    except:
        resp.append('cannot get JSON')
        return '; '.join(resp)
    if (request_data is not None) & (len(request_data) > 0):
        conn = get_db_connection()
        resp.append('db opened')
        if 'client' in request_data:
            client = request_data.pop('client', 'unknown')
            resp.append(client)
        for k,v in request_data.items():
            conn.execute('INSERT INTO messages (name, value, client) VALUES (?, ?, ?)', (k, v, client))
            resp.append('{0}: {1}'.format(k,v))
#                         
#        print('Written to database: ({0}, {1}, {2})'.format(client, k, v))
        conn.commit()
        conn.close()
        resp.append('db closed')
#    else:
#        print('IF clause is false')
#        
#    print(request_data)
    return '; '.join(resp)

@server.route('/info', methods=['GET'])
def serve_info():
    return '2222:127.0.0.1:22'

@server.route('/list_messages')
def index():
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages').fetchall()
    conn.close()
    return render_template('list_messages.html', messages=messages)


if __name__ == "__main__":
    #app.run_server(port=8888, debug=True)
    server.run(debug=True)