# PORTUGAL RADIATION PANEL (RADMAP)
# CODE: Pedro Lucas
# FILE: app.py

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from apscheduler.schedulers.background import BackgroundScheduler
import time
import fetch

locals = []
info_local = []

# Load sensitive information
load_dotenv('.env')
host = os.getenv('MONGO_HOST')
user = os.getenv('MONGO_USER')
password = os.getenv('MONGO_PASSWORD')
database_name = os.getenv('MONGO_DATABASE')
collection_name = os.getenv('MONGO_COLLECTION')

# Conectar ao MongoDB
client = MongoClient(f"mongodb://{host}/{database_name}")
db = client[database_name]
collection = db[collection_name]

def update_data():
    """Busca os dados do MongoDB e os converte para DataFrame"""
    data = list(collection.find())  # Pega todos os documentos da coleção
    for item in data:
        item.pop('_id', None)  # Remove o campo _id que é gerado automaticamente
    db_df = pd.DataFrame(data)
    return db_df

def get_place(place):
    """Obtém o último registro de um local específico."""
    global latest_data
    data = latest_data[latest_data['place'] == place]
    return data.iloc[-1] if not data.empty else None

def get_all_from_place(place):
    """Obtém todos os registros de um local específico."""
    global latest_data
    data = latest_data[latest_data['place'] == place]
    df = pd.DataFrame(data, columns=['hour', 'place', 'value', 'latitude', 'longitude'])
    return df

def create_dataframes():
    """Cria um DataFrame consolidado para os locais."""
    global latest_data
    data = []
    for place in latest_data['place'].unique():
        data.append(get_place(place))
    df = pd.DataFrame(data, columns=['hour', 'place', 'value', 'latitude', 'longitude'])
    return df

def fetch_and_update_data():
    """Busca novos dados a cada minuto e atualiza o DataFrame global."""
    global latest_data
    print("Atualizando dados...")
    fetch.data_processing()
    latest_data = update_data()
    print("Dados atualizados!")

# Inicializa os dados
fetch_and_update_data()
latest_data = update_data()

# Configura o agendador para atualizar os dados a cada 5 minutos
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_update_data, trigger="interval", minutes=5)
scheduler.start()

selected_place = "Lisboa"

# Cria a aplicação Dash
app = dash.Dash(__name__, title="Radioactivity Dashboard")

app.layout = html.Div([
    html.Div(
        id='info-title',
        className='info-title',
        children=[
            html.H1("Radioactivity Dashboard"),
            html.Div(
                id='history',
                className='history',
                children=[
                    dcc.Dropdown(
                        id='title-dropdown',
                        options=[],
                        value=None,
                        className='dropdown'
                    ),
                    html.Br(),
                    dcc.Graph(
                        id='history-graph',
                    )
            ])
        ]
    ),
    dcc.Graph(
        id='map',
    ),
    html.A(
        children=[
            html.Img(
                id='vostpt-logo',
                src="assets/VOSTPT_LOGO_2023_cores.svg",
            )
        ],
        href="https://vost.pt",
    ),
    dcc.Interval(
        id='interval-component',
        interval=60*5000,  # Update every 5 minutes
        n_intervals=0
    )
])

@app.callback(
    [Output('title-dropdown', 'options'),
     Output('title-dropdown', 'value')],
    Input('title-dropdown', 'value')
)
def update_dropdown(selected_place):
    """Atualiza as opções do dropdown com os locais disponíveis."""
    dropdown_options = [{'label': place, 'value': place} for place in latest_data['place'].unique()]

    # Define o valor inicial como Lisboa se não houver seleção
    if selected_place is None:
        initial_value = "Lisboa"
    else:
        initial_value = selected_place

    return dropdown_options, initial_value

@app.callback(
    Output("history-graph", "figure"), 
    Input("title-dropdown", "value"))
def update_history_graph(place):
    """Atualiza o gráfico histórico com base no local selecionado."""
    selected_place = place if place is not None else selected_place
    fig = px.line(
        get_all_from_place(selected_place),
        x="hour",
        y="value",
        color="place"
    )
    return fig

@app.callback(
    Output('map', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_map(n_intervals):
    figure=go.Figure(
        data=go.Scattermapbox(
            lat=create_dataframes()['latitude'],
            lon=create_dataframes()['longitude'],
            mode='markers',
            marker=dict(
                size=(create_dataframes()['value'] / 9) + 5,  # Ajustar o tamanho dos marcadores
                color=create_dataframes()['value'],
                colorscale='Viridis',  # Escala de cores para os marcadores
                colorbar=dict(
                    title='Radioactivity'
                )
            ),
            text=create_dataframes()['value'],
            customdata=create_dataframes()[['hour', 'place', 'value']],
            hovertemplate=(
                "<b>Hora:</b> %{customdata[0]}<br>"
                "<b>Local:</b> %{customdata[1]}<br>"
                "<b>Valor:</b> %{customdata[2]} nSv/h<br>"
                "<extra></extra>"
            )
        ),
        layout=go.Layout(
            mapbox=dict(
                style="open-street-map",  # Estilo do mapa
                center=dict(lat=create_dataframes()['latitude'].mean(), lon=create_dataframes()['longitude'].mean()),
                zoom=5
            ),
            margin=dict(r=0, t=0, l=0, b=0)
        )
    )
    return figure

if __name__ == '__main__':
    try:
        app.run_server(debug=False, host='0.0.0.0')
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
