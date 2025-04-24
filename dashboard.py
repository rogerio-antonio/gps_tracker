import streamlit as st
import folium
from streamlit_folium import st_folium
from kafka import KafkaConsumer
import json

st.set_page_config(layout="wide")

consumer = KafkaConsumer(
    'localizacoes',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='mapa-tracker'
)

st.title("📍 Rastreamento em Tempo Real")

# Última posição
pos = {"latitude": -23.55, "longitude": -46.63}  # inicial

for msg in consumer:
    pos = msg.value
    break  # consome só uma para não travar a UI

# Mapa com Folium
m = folium.Map(location=[pos["latitude"], pos["longitude"]], zoom_start=17)
folium.Marker([pos["latitude"], pos["longitude"]], tooltip="Última posição").add_to(m)

st_folium(m, width=700, height=500)
