from flask import Flask, jsonify, request, url_for
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
import ipdb

server = Flask(__name__)
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css], server=server)

end_date = datetime.date.today()
start_date = end_date - relativedelta(months=1)

def get_db_connection():
    conn = sqlite3.connect('alive_info.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_data(start_date, end_date):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, client, created, name, value FROM messages WHERE DATE(created) BETWEEN ? AND ?", (start_date, end_date))
    rows = c.fetchall()
    conn.close()
    data = []
    for row in rows:
        data.append({'id': row[0], 'client': row[1], 'name': row[3], 'value': row[4], 'created': row[2]})
    return pd.DataFrame(data)

# @app.server.route('/data')
# def data():
#     start_date_str = request.args.get('start_date')
#     end_date_str = request.args.get('end_date')
#     start_date = datetime.datetime.fromisoformat(start_date_str).date()
#     end_date = datetime.datetime.fromisoformat(end_date_str).date()
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT id, client, created, name, value FROM messages WHERE DATE(created) BETWEEN ? AND ?", (start_date, end_date))
#     rows = c.fetchall()
#     conn.close()
#     data = []
#     for row in rows:
#         data.append({'id': row[0], 'client': row[1], 'name': row[3], 'value': row[4], 'created': row[2]})
#     return jsonify(data)

@app.callback(Output('table', 'data'),
              Output('name-dropdown', 'options'),
              Input('date-range-picker', 'start_date'),
              Input('date-range-picker', 'end_date'),
              Input('name-dropdown', 'value'))
def update_data(start_date, end_date, value):
    df = get_data(start_date, end_date)
    #url = url_for('data', _external=True, start_date=start_date, end_date=end_date)
    #response = requests.get(url)
    #df = pd.read_json(response.content)
    list_of_options = df['name'].sort_values().unique()
    dropdown = [{'label': x,  'value': x} for x in list_of_options ]

    if (dropdown is not None) and (len(dropdown) > 0) and (value is not None) and (len(value) > 0):
        value = [x for x in value if x in list_of_options]
        print(value)
        print(list_of_options)
        if len(value) > 0:
            df = df[df['name'].isin(value)]

    return df.to_dict('records'), dropdown


app.layout = html.Div(children=[
    html.Div([
        html.H1('DataTable Example'),
        dcc.Dropdown(id='name-dropdown', options=[], multi=True),
        dcc.DatePickerRange(
            id='date-range-picker',
            min_date_allowed=dt(2000, 1, 1),
            max_date_allowed=dt.now(),
            initial_visible_month=dt.now(),
            start_date_placeholder_text='Start Date',
            end_date_placeholder_text='End Date',
            start_date=start_date,
            end_date=end_date
        ),
        #dcc.Interval(id='interval', interval=5000, n_intervals=0),
        dash_table.DataTable(
            id='table',
            columns=[
                {'name': 'ID', 'id': 'id'},
                {'name': 'Client', 'id': 'client'},
                {'name': 'Key', 'id': 'name'},
                {'name': 'Value', 'id': 'value'},
                {'name': 'Timestamp (UTC)', 'id': 'created'}
            ],
            page_size=50,
            style_table={'overflowX': 'scroll'},
            filter_action='native',
            sort_action='native',
            sort_mode='single',
            sort_by=[{'column_id': 'created', 'direction': 'desc'}],
            style_cell={'textAlign': 'left'},
            style_data={
                'color': 'black',
                'backgroundColor': 'white'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(220, 220, 220)',
                }
            ],
            style_header={
                'backgroundColor': 'rgb(210, 210, 210)',
                'color': 'black',
                'fontWeight': 'bold'
            }
            
        )
    ], className="dbc")], style={'margin': '200px'})


if __name__ == '__main__':
    app.run_server(debug=True)
