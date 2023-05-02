import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import sqlalchemy as sa
import datetime
import urllib
# from threading import Timer
# import webbrowser

# Get the environment variables
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Create the database URL
db_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create a SQLAlchemy engine object
engine = sa.create_engine(db_url)

# Define external stylesheets
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# Create the app and server objects
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# server = app.server
app.title="Ark_Biotech Dashboard"

# Define the layout
app.layout = html.Div([
    html.H1("Process Trending Dashboard", style={'text-align': 'center'}),
    html.Div([
        html.H2("Select the time window", style={'text-align': 'center'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=datetime.date(2021, 1, 1),
            max_date_allowed=datetime.datetime.now().date(),
            initial_visible_month=datetime.datetime.now().date(),
            start_date=datetime.date(2023, 4, 4),
            end_date=datetime.date(2023,4,30)
        ),
        html.Button('Refresh Data', id='refresh-button', n_clicks=0, style={'text-align': 'center'}),
        html.A(
            html.Button('Download as CSV'),
            id='download-link',
            download="data.csv",
            href="",
            target="_blank",
            style={'text-align': 'center'}
        )
    ], style={'text-align': 'center'}),
    html.Div([
        html.Div([
            dcc.Graph(id='temperature-graph', style={'height': '300px'})
        ], className="six columns"),

        html.Div([
            dcc.Graph(id='ph-graph', style={'height': '300px'})
        ], className="six columns")
    ], className="row"),

    html.Div([
        html.Div([
            dcc.Graph(id='oxygen-graph', style={'height': '300px'})
        ], className="six columns"),

        html.Div([
            dcc.Graph(id='pressure-graph', style={'height': '300px'})
        ], className="six columns")
    ], className="row")
])

# Define the callbacks
@app.callback(
    Output('temperature-graph', 'figure'),
    Output('ph-graph', 'figure'),
    Output('oxygen-graph', 'figure'),
    Output('pressure-graph', 'figure'),
    Output('download-link', 'href'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('refresh-button', 'n_clicks')
)
def update_graph(start_date, end_date, n_clicks):
    # Fetch data from the database
    query = f"""
        SELECT time, value
        FROM "CM_HAM_DO_AI1/Temp_value"
        WHERE time BETWEEN '{start_date}' AND '{end_date}'
    """
    df_temp = pd.read_sql_query(query,  con=engine)

    query = f"""
        SELECT time, value
        FROM "CM_HAM_PH_AI1/pH_value"
        WHERE time BETWEEN '{start_date}' AND '{end_date}'
    """
    df_ph = pd.read_sql_query(query, con=engine)

    query = f"""
        SELECT time, value
        FROM "CM_PID_DO/Process_DO"
        WHERE time BETWEEN '{start_date}' AND '{end_date}'
    """
    df_oxygen = pd.read_sql_query(query, con=engine)

    query = f"""
        SELECT time, value
        FROM "CM_PRESSURE/Output"
        WHERE time BETWEEN '{start_date}' AND '{end_date}'
    """
    df_pressure = pd.read_sql_query(query, con=engine)

    # Create the figures
    fig_temp = {
        'data': [{'x': df_temp['time'], 'y': df_temp['value'], 'type': 'line'}],
        'layout': {
            'title': 'Temperature vs Time',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Temperature (Celsius)'}
        }
    }

    fig_ph = {
        'data': [{'x': df_ph['time'],
        'y': df_ph['value'], 'type': 'line'}],
    'layout': {
        'title': 'pH vs Time',
        'xaxis': {'title': 'Time'},
        'yaxis': {'title': 'pH'}
        }
    }

    fig_oxygen = {
        'data': [{'x': df_oxygen['time'], 'y': df_oxygen['value'], 'type': 'line'}],
        'layout': {
            'title': 'Distilled Oxygen vs Time',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Distilled Oxygen (%)'}
        }
    }

    fig_pressure = {
        'data': [{'x': df_pressure['time'], 'y': df_pressure['value'], 'type': 'line'}],
        'layout': {
            'title': 'Pressure vs Time',
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Pressure (psi)'}
        }
    }

    # Create the CSV file
    csv_string = df_temp.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)

    
    # Return the figures and the download link
    return fig_temp, fig_ph, fig_oxygen, fig_pressure, csv_string

# def open_browser():
#     webbrowser.open_new('http://localhost:8888/')

# Run the app
if __name__ == '__main__':
    print("******  (All the bonus features added)  ****** \n\n *****  Dashboard can also be viewed at http://localhost:8888/ ****** \n")
    # Timer(5, open_browser).start()
    app.run_server(host='0.0.0.0', port=8888, debug=True)
    