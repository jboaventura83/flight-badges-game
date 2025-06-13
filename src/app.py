import pandas as pd
import pydeck as pdk
import streamlit as st
import json
import os
from geopy.distance import geodesic

# Caminhos dos arquivos
dataset_path = 'data/airports.csv'
visited_path = 'data/visited.json'

# Função para carregar dados
@st.cache_data
def carregar_aeroportos():
    df = pd.read_csv(dataset_path)
    df = df[df['type'].isin(['large_airport', 'medium_airport'])]
    df = df.dropna(subset=['latitude_deg', 'longitude_deg', 'iata_code'])
    df['display'] = df['iata_code'] + ' - ' + df['name']
    return df

principais = carregar_aeroportos()
display_to_iata = dict(zip(principais['display'], principais['iata_code']))

# Carregar progresso
if os.path.exists(visited_path):
    with open(visited_path, 'r') as f:
        visited = json.load(f)
else:
    visited = []

st.set_page_config(page_title="Flight Badges Game", layout="wide")
st.title("🚀 Flight Badges Game - Versão Super Rápida ⚡")

# Dropdown manual
st.subheader("📍 Seleção manual")
iata_display_selected = st.selectbox("Selecione o aeroporto visitado:", sorted(principais['display']))

if st.button("Marcar via seleção"):
    iata_selected = display_to_iata[iata_display_selected]
    if iata_selected not in visited:
        visited.append(iata_selected)
        with open(visited_path, 'w') as f:
            json.dump(visited, f)
        st.success(f"Aeroporto {iata_selected} registrado com sucesso!")
    else:
        st.warning("Este aeroporto já foi registrado anteriormente.")

st.subheader("📊 Progresso")
st.markdown(f"**Total de aeroportos visitados: {len(visited)}**")

# Adiciona coluna de visitado
principais['visited'] = principais['iata_code'].isin(visited)

# Configuração do mapa
st.subheader("🌍 Mapa Interativo (ultra rápido)")
view_state = pdk.ViewState(
    latitude=20,
    longitude=0,
    zoom=1.5,
    pitch=0
)

# Camada de aeroportos não visitados
layer_nao_visitados = pdk.Layer(
    "ScatterplotLayer",
    data=principais[principais['visited'] == False],
    get_position='[longitude_deg, latitude_deg]',
    get_color='[0, 122, 255, 160]',  # azul semi-transparente
    get_radius=30000,
    pickable=True
)

# Camada de aeroportos visitados
layer_visitados = pdk.Layer(
    "ScatterplotLayer",
    data=principais[principais['visited'] == True],
    get_position='[longitude_deg, latitude_deg]',
    get_color='[255, 0, 0, 180]',  # vermelho semi-transparente
    get_radius=35000,
    pickable=True
)

# Monta o mapa
r = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",  # visual bonito
    initial_view_state=view_state,
    layers=[layer_nao_visitados, layer_visitados],
    tooltip={"text": "{display}"}
)

clicked = st.pydeck_chart(r)

# (Ainda não temos clique interativo, vamos adicionar isso depois)