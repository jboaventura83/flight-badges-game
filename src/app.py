import pandas as pd
import folium
from folium.plugins import MarkerCluster
import json
import os
import streamlit as st
from streamlit_folium import st_folium
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

# Carregar dataset e preparar dropdown
principais = carregar_aeroportos()
display_to_iata = dict(zip(principais['display'], principais['iata_code']))

# Carregar progresso
if os.path.exists(visited_path):
    with open(visited_path, 'r') as f:
        visited = json.load(f)
else:
    visited = []

# Inicializar session_state
if 'aeroporto_proximo' not in st.session_state:
    st.session_state['aeroporto_proximo'] = None
if 'distancia_km' not in st.session_state:
    st.session_state['distancia_km'] = None

# Layout do app
st.set_page_config(page_title="Flight Badges Game", layout="wide")

st.title("🛫 Flight Badges Game")
st.write("Marque aeroportos visitados clicando no mapa ou selecionando no menu abaixo.")

col1, col2 = st.columns(2)

# --- Seção 1: Registro manual via dropdown ---
with col1:
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

# Mostrar total de aeroportos visitados
with col2:
    st.subheader("📊 Progresso")
    st.markdown(f"**Total de aeroportos visitados: {len(visited)}**")

# --- Seção 2: Mapa interativo com visual bonito ---
st.subheader("🌍 Clique no mapa para registrar")

# Criar o mapa com tiles modernos
mapa = folium.Map(location=[20, 0], zoom_start=2, tiles='CartoDB positron')
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

# Exibir o mapa
st_data = st_folium(mapa, width=1200, height=700, use_container_width=True)

# Processar clique no mapa e armazenar estado
if st_data and st_data['last_clicked']:
    click_lat = st_data['last_clicked']['lat']
    click_lon = st_data['last_clicked']['lng']

    def encontrar_aeroporto_mais_proximo(lat, lon):
        min_dist = float('inf')
        aeroporto_proximo = None

        for _, row in principais.iterrows():
            aeroporto_lat = row['latitude_deg']
            aeroporto_lon = row['longitude_deg']
            distancia = geodesic((lat, lon), (aeroporto_lat, aeroporto_lon)).km

            if distancia < min_dist:
                min_dist = distancia
                aeroporto_proximo = row

        return aeroporto_proximo, min_dist

    aeroporto_proximo, distancia_km = encontrar_aeroporto_mais_proximo(click_lat, click_lon)

    st.session_state['aeroporto_proximo'] = aeroporto_proximo
    st.session_state['distancia_km'] = distancia_km

# Mostrar confirmação se houver aeroporto candidato
if st.session_state['aeroporto_proximo'] is not None:
    aeroporto_proximo = st.session_state['aeroporto_proximo']
    distancia_km = st.session_state['distancia_km']

    iata = aeroporto_proximo['iata_code']
    nome = aeroporto_proximo['name']
    pais = aeroporto_proximo['iso_country']

    if distancia_km <= 50:
        if iata not in visited:
            if st.button(f"✅ Confirmar registro de {iata} - {nome} ({pais})"):
                visited.append(iata)
                with open(visited_path, 'w') as f:
                    json.dump(visited, f)
                st.success(f"Aeroporto {iata} registrado com sucesso!")
                st.session_state['aeroporto_proximo'] = None
        else:
            st.info(f"Você já registrou o aeroporto {iata}.")
            st.session_state['aeroporto_proximo'] = None
    else:
        st.warning(f"Nenhum aeroporto próximo (distância: {distancia_km:.1f} km)")
        st.session_state['aeroporto_proximo'] = None