import flet as ft
import folium
from kafka import KafkaConsumer
import json
from dotenv import load_dotenv
import os
from threading import Thread
import tempfile
import webbrowser
from geopy.geocoders import Nominatim
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

# Configurações Kafka
BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC = os.getenv('KAFKA_TOPIC', 'localizacao')

class GeoApp:
    def __init__(self):
        self.consumer = KafkaConsumer(
            TOPIC,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.locations = []
        self.map_file = None
        self.geolocator = Nominatim(user_agent="geoapp")
        
    def update_map(self):
        if not self.locations:
            return
        
        # Cria mapa centralizado na última localização
        last_loc = self.locations[-1]
        m = folium.Map(location=[last_loc['lat'], last_loc['lon']], zoom_start=13)
        
        # Adiciona marcadores e linha do trajeto
        coordinates = [[loc['lat'], loc['lon']] for loc in self.locations]
        
        # Adiciona linha do trajeto
        folium.PolyLine(
            coordinates,
            weight=3,
            color='red',
            opacity=0.8
        ).add_to(m)
        
        # Adiciona marcadores
        for loc in self.locations:
            popup_text = f"""
            Horário: {loc['timestamp']}
            Endereço: {loc.get('address', 'Não disponível')}
            """
            folium.Marker(
                [loc['lat'], loc['lon']],
                popup=popup_text
            ).add_to(m)
        
        # Salva mapa em arquivo temporário
        if self.map_file:
            m.save(self.map_file)
        
    def get_address(self, lat, lon):
        try:
            location = self.geolocator.reverse(f"{lat}, {lon}")
            return location.address
        except:
            return "Endereço não encontrado"
        
    def kafka_consumer(self):
        for message in self.consumer:
            data = message.value
            data['timestamp'] = datetime.now().strftime("%H:%M:%S")
            data['address'] = self.get_address(data['lat'], data['lon'])
            self.locations.append(data)
            self.update_map()
            
    def main(self, page: ft.Page):
        page.title = "Geolocalização em Tempo Real"
        page.theme_mode = "dark"
        page.padding = 20
        
        # Cria arquivo temporário para o mapa
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        self.map_file = temp.name
        temp.close()
        
        # Componentes da UI
        title = ft.Text("Rastreamento em Tempo Real", size=30, weight=ft.FontWeight.BOLD)
        status = ft.Text("Aguardando dados...", color="grey")
        map_view = ft.WebView(
            url=f"file://{self.map_file}",
            width=800,
            height=600
        )
        
        # Layout
        page.add(
            ft.Column([
                title,
                status,
                map_view
            ])
        )
        
        # Inicia consumidor Kafka em thread separada
        Thread(target=self.kafka_consumer, daemon=True).start()
        
        # Cria mapa inicial
        m = folium.Map(location=[-23.550520, -46.633308], zoom_start=12)
        m.save(self.map_file)

if __name__ == "__main__":
    app = GeoApp()
    ft.app(target=app.main, view=ft.WEB_BROWSER) 