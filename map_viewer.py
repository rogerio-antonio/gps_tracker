import asyncio
from aiokafka import AIOKafkaConsumer
import json
from datetime import datetime
import folium
from flet import (
    Page, app, Text, AppBar, WEB_BROWSER, 
    Column, Row, ElevatedButton, Container,
    alignment, colors, IconButton, icons,
    WebView
)

KAFKA_BOOTSTRAP_SERVER = "192.168.15.5:9092"
KAFKA_TOPIC = "gps"

class MapViewer:
    def __init__(self, page: Page):
        self.page = page
        self.positions = []
        self.map = None
        self.consumer = None
        self.is_running = False
        
        # Configuração inicial da página
        self.page.title = "GPS Tracker Viewer"
        self.page.scroll = True
        self.page.padding = 20
        
        # Componentes da UI
        self.status_text = Text("Aguardando dados...", size=16, color=colors.BLUE)
        self.last_position = Text("", size=14)
        self.total_points = Text("Total de pontos: 0", size=14)
        self.debug_text = Text("", size=12, color=colors.RED)
        
        # Botões de controle
        self.start_btn = ElevatedButton(
            "Iniciar Rastreamento",
            on_click=self.start_tracking,
            bgcolor=colors.GREEN
        )
        self.stop_btn = ElevatedButton(
            "Parar",
            on_click=self.stop_tracking,
            visible=False,
            bgcolor=colors.RED
        )
        self.clear_btn = ElevatedButton(
            "Limpar Histórico",
            on_click=self.clear_history,
            bgcolor=colors.BLUE
        )
        
        # Mapa
        self.create_initial_map()
        self.webview = WebView(
            url="mapa.html",
            height=500,
            width=800
        )
        
        # Layout
        self.page.add(
            AppBar(title=Text("GPS Tracker Viewer")),
            Column([
                Row([self.start_btn, self.stop_btn, self.clear_btn]),
                self.status_text,
                self.last_position,
                self.total_points,
                self.debug_text,
                Container(content=self.webview, margin=20)
            ])
        )
    
    def create_initial_map(self):
        """Cria o mapa inicial"""
        m = folium.Map(
            location=[-15.77972, -47.92972],  # Centro do Brasil
            zoom_start=4
        )
        m.save('mapa.html')
    
    def create_map(self):
        """Cria ou atualiza o mapa com todas as posições"""
        if not self.positions:
            self.create_initial_map()
            return
            
        # Criar mapa centralizado na última posição
        last_pos = self.positions[-1]
        m = folium.Map(
            location=[last_pos['latitude'], last_pos['longitude']],
            zoom_start=15
        )
        
        # Adicionar todos os pontos
        points = []
        for pos in self.positions:
            points.append([pos['latitude'], pos['longitude']])
            folium.Marker(
                [pos['latitude'], pos['longitude']],
                popup=f"Time: {datetime.fromtimestamp(pos['timestamp']).strftime('%H:%M:%S')}"
            ).add_to(m)
        
        # Desenhar a linha do trajeto
        if len(points) > 1:
            folium.PolyLine(
                points,
                weight=3,
                color='red',
                opacity=0.8
            ).add_to(m)
        
        m.save('mapa.html')
        self.webview.update()
    
    def update_stats(self, new_position):
        """Atualiza as estatísticas na UI"""
        self.last_position.value = f"Última posição: {new_position['latitude']:.6f}, {new_position['longitude']:.6f}"
        self.total_points.value = f"Total de pontos: {len(self.positions)}"
        self.debug_text.value = f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"
        self.page.update()
    
    async def start_tracking(self, e):
        """Inicia o rastreamento"""
        try:
            self.is_running = True
            self.start_btn.visible = False
            self.stop_btn.visible = True
            self.status_text.value = "Conectando ao Kafka..."
            self.page.update()
            
            self.consumer = AIOKafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
                group_id="map_viewer_group",
                auto_offset_reset='latest'
            )
            
            await self.consumer.start()
            self.status_text.value = "Rastreamento ativo..."
            self.page.update()
            
            try:
                async for msg in self.consumer:
                    if not self.is_running:
                        break
                        
                    data = json.loads(msg.value.decode('utf-8'))
                    self.positions.append(data)
                    self.update_stats(data)
                    self.create_map()
                    
            except Exception as e:
                self.debug_text.value = f"Erro ao receber mensagem: {str(e)}"
                self.page.update()
                    
        except Exception as e:
            self.debug_text.value = f"Erro ao conectar no Kafka: {str(e)}"
            self.status_text.value = "Erro de conexão"
            self.start_btn.visible = True
            self.stop_btn.visible = False
            self.page.update()
        finally:
            if self.consumer:
                await self.consumer.stop()
    
    async def stop_tracking(self, e):
        """Para o rastreamento"""
        self.is_running = False
        self.start_btn.visible = True
        self.stop_btn.visible = False
        self.status_text.value = "Rastreamento parado"
        self.page.update()
    
    async def clear_history(self, e):
        """Limpa o histórico de posições"""
        self.positions = []
        self.last_position.value = ""
        self.total_points.value = "Total de pontos: 0"
        self.status_text.value = "Histórico limpo"
        self.debug_text.value = ""
        self.page.update()
        self.create_map()

async def main(page: Page):
    viewer = MapViewer(page)

app(target=main, view=WEB_BROWSER) 