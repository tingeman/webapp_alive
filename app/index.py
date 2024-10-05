from flask import Flask, jsonify, request, url_for, make_response
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dash_table.Format import Group
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import requests
import datetime
import pandas as pd
import sqlite3
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

server = Flask(__name__)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css], server=server)

end_date = datetime.date.today()
start_date = end_date - relativedelta(months=1)

# -------------------------------------------------------------------------
# Support functions

def get_db_connection():
    # establish database connection
    conn = sqlite3.connect('alive_info.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_data(start_date, end_date):
    # obtain messages from database within daterange
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, client, created, name, value, message_id FROM messages WHERE DATE(created) BETWEEN ? AND ?", (start_date, end_date))
    rows = c.fetchall()
    conn.close()
    data = []
    for row in rows:
        mid = row[5][:13] if len(row[5]) > 13 else row[5]
        data.append({'id': row[0], 'client': row[1], 'name': row[3], 'value': row[4], 'created': row[2], 'message_id': mid})
    return pd.DataFrame(data)

# -------------------------------------------------------------------------
# Functions related to submission of messages

@server.route('/submit_data', methods=['POST'])
def submit_data():
    # Store posted messages to database
    resp = []
    resp_code = None
    try:
        request_data = request.get_json()
    except:
        resp.append('cannot get JSON')
        resp_code = 400
    else:
        if (request_data is not None) & (len(request_data) > 0):
            #import ipdb as pdb; pdb.set_trace()
            conn = get_db_connection()
            c = conn.cursor()

            #if 'client' in request_data:
            client = request_data.pop('client', 'unknown')
            #if 'id' in request_data:
            message_id = request_data.pop('id', 'unknown')
            c.execute("SELECT * FROM messages WHERE message_id=?", (message_id,))
            row = c.fetchone()
            
            if (message_id == 'unkown') or (not row):
                # if message doesn't have an id, or if it does not already exist in the database
                # commit message to database
                for k,v in request_data.items():
                    c.execute('INSERT INTO messages (name, value, client, message_id) VALUES (?, ?, ?, ?)', (k, v, client, message_id))
                conn.commit()
            conn.close()
        resp.append('Payload processed')
        resp_code = 200
    return make_response(jsonify(resp), resp_code)


@server.route('/info', methods=['GET'])
def serve_info():
    # provide return message to client
    # message is currently not used on client
    # but feature could be implemented to update settings on client.
    return '2222:127.0.0.1:22'

# -------------------------------------------------------------------------
# Functions related to serving of message list

@app.callback(Output('table', 'data'),
              Output('name-dropdown', 'options'),
              Input('date-range-picker', 'start_date'),
              Input('date-range-picker', 'end_date'),
              Input('name-dropdown', 'value'),
              Input('reload-button', 'n_clicks'))
def update_data(start_date, end_date, value, bt_clicks):
    # Update table data (list of messages)
    df = get_data(start_date, end_date)
    list_of_options = df['name'].sort_values().unique()
    dropdown = [{'label': x,  'value': x} for x in list_of_options ]

    if (dropdown is not None) and (len(dropdown) > 0) and (value is not None) and (len(value) > 0):
        value = [x for x in value if x in list_of_options]
        print(value)
        print(list_of_options)
        if len(value) > 0:
            df = df[df['name'].isin(value)]

    return df.to_dict('records'), dropdown

# -------------------------------------------------------------------------
# definition of app layout

app.layout = html.Div(children=[
    html.Div([
        dbc.Row(dbc.Col(html.H1('Alive messages from RPi control boxes...'), width="auto")),
        dbc.Row([dbc.Col(html.Div(dcc.DatePickerRange(id='date-range-picker',
                                             min_date_allowed=dt(2000, 1, 1),
                                             max_date_allowed=dt.now(),
                                             initial_visible_month=dt.now(),
                                             start_date_placeholder_text='Start Date',
                                             end_date_placeholder_text='End Date',
                                             start_date=start_date,
                                             end_date=end_date,
                                             persistence=True,
                                             persistence_type='session',), className='dash-bootstrap'), width=3),
                 dbc.Col(html.Div(dcc.Dropdown(id='name-dropdown', options=[], multi=True, persistence=True), className='dash-bootstrap')),
                 dbc.Col(dbc.Button('Reload', id='reload-button'), width=3),]),
        dbc.Row(dash_table.DataTable(id='table',
                                     columns=[{'name': 'ID', 'id': 'id'},
                                              {'name': 'Client', 'id': 'client'},
                                              {'name': 'Key', 'id': 'name'},
                                              {'name': 'Value', 'id': 'value'},
                                              {'name': 'Timestamp (UTC)', 'id': 'created'},
                                              {'name': 'MessageID', 'id': 'message_id'}],
                                     page_size=50,
                                     style_table={'overflowX': 'scroll'},
                                     filter_action='native',
                                     sort_action='native',
                                     sort_mode='single',
                                     sort_by=[{'column_id': 'created', 'direction': 'desc'}],
                                     style_cell={'textAlign': 'left'},
                                     style_data={'color': 'black',
                                                'backgroundColor': 'white'},
                                     style_data_conditional=[{'if': {'row_index': 'odd'},
                                                              'backgroundColor': 'rgb(220, 220, 220)',}],
                                     style_header={'backgroundColor': 'rgb(210, 210, 210)',
                                                   'color': 'black',
                                                   'fontWeight': 'bold'})),
    ], className="dbc")], style={'margin': '200px'})


        # html.H1('Alive messages from RPi control boxes...'),
        # dcc.Dropdown(id='name-dropdown', options=[], multi=True, persistence=True),
        # dcc.DatePickerRange(
        #     id='date-range-picker',
        #     min_date_allowed=dt(2000, 1, 1),
        #     max_date_allowed=dt.now(),
        #     initial_visible_month=dt.now(),
        #     start_date_placeholder_text='Start Date',
        #     end_date_placeholder_text='End Date',
        #     start_date=start_date,
        #     end_date=end_date,
        #     persistence=True,
        #     persistence_type='session',
        # ),
        # html.Button('Reload', id='reload-button'),
        # dash_table.DataTable(
        #     id='table',
        #     columns=[
        #         {'name': 'ID', 'id': 'id'},
        #         {'name': 'Client', 'id': 'client'},
        #         {'name': 'Key', 'id': 'name'},
        #         {'name': 'Value', 'id': 'value'},
        #         {'name': 'Timestamp (UTC)', 'id': 'created'}
        #     ],
        #     page_size=50,
        #     style_table={'overflowX': 'scroll'},
        #     filter_action='native',
        #     sort_action='native',
        #     sort_mode='single',
        #     sort_by=[{'column_id': 'created', 'direction': 'desc'}],
        #     style_cell={'textAlign': 'left'},
        #     style_data={
        #         'color': 'black',
        #         'backgroundColor': 'white'
        #     },
        #     style_data_conditional=[
        #         {
        #             'if': {'row_index': 'odd'},
        #             'backgroundColor': 'rgb(220, 220, 220)',
        #         }
        #     ],
        #     style_header={
        #         'backgroundColor': 'rgb(210, 210, 210)',
        #         'color': 'black',
        #         'fontWeight': 'bold'
        #     }
            
        # )
    #], className="dbc")], style={'margin': '200px'})


if __name__ == '__main__':
    app.run_server(debug=True)
