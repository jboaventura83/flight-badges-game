import pandas as pd
import folium
from folium.plugins import MarkerCluster
import json
import os
import streamlit as st
from streamlit_folium import st_folium

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

# Carregar dataset e preparar dropdown
principais = carregar_aeroportos()
display_to_iata = dict(zip(principais['display'], principais['iata_code']))

# Carregar progresso
if os.path.exists(visited_path):
    with open(visited_path, 'r') as f:
        visited = json.load(f)
else:
    visited = []

# Título
st.title("🌎 Flight Badges Game")
st.write("Selecione os aeroportos que já visitou e monte seu mapa de conquistas!")

# Seleção de aeroporto
iata_display_selected = st.selectbox("Selecione o aeroporto visitado:", sorted(principais['display']))

# Botão de confirmação
if st.button("Marcar como visitado"):
    iata_selected = display_to_iata[iata_display_selected]
    
    if iata_selected not in visited:
        visited.append(iata_selected)
        with open(visited_path, 'w') as f:
            json.dump(visited, f)
        st.success(f"Aeroporto {iata_selected} registrado com sucesso!")
    else:
        st.warning("Este aeroporto já foi registrado anteriormente.")

# Mostrar total de aeroportos visitados
st.markdown(f"**Total de aeroportos visitados: {len(visited)}**")

# Criar o mapa com Folium
mapa = folium.Map(location=[20, 0], zoom_start=2)
cluster = MarkerCluster().add_to(mapa)

for _, aeroporto in principais.iterrows():
    location = [aeroporto['latitude_deg'], aeroporto['longitude_deg']]
    popup = f"{aeroporto['name']} ({aeroporto['iata_code']}) - {aeroporto['iso_country']}"

    icon_color = 'red' if aeroporto['iata_code'] in visited else 'blue'
    folium.Marker(
        location=location,
        popup=popup,
        icon=folium.Icon(color=icon_color)
    ).add_to(cluster)

# Mostrar o mapa interativo no Streamlit
st_data = st_folium(mapa, width=700, height=500)