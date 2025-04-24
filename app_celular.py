import asyncio
from aiokafka import AIOKafkaProducer
import json
import time
from flet import Page, app, Text, AppBar, WEB_BROWSER, ElevatedButton
from flet_geolocator import Geolocator

# Configuração simplificada
KAFKA_BOOTSTRAP_SERVER = "192.168.15.5:9092"
KAFKA_TOPIC = "gps"

async def send_location_loop(page: Page, producer: AIOKafkaProducer, geolocator: Geolocator):
    while True:
        try:
            pos = await geolocator.get_current_position_async()
            if pos:
                data = {
                    "timestamp": time.time(),
                    "latitude": pos.latitude,
                    "longitude": pos.longitude
                }
                await producer.send_and_wait(KAFKA_TOPIC, json.dumps(data).encode("utf-8"))
                page.controls.append(Text(f"Enviado: {data}"))
                page.update()
        except Exception as e:
            page.controls.append(Text(f"Erro detalhado: {str(e)}"))
            page.update()
        await asyncio.sleep(5)

async def main(page: Page):
    page.scroll = "adaptive"
    page.appbar = AppBar(title=Text("GPS Kafka Sender"))
    
    # Inicializa o Geolocator
    gl = Geolocator()
    page.overlay.append(gl)
    page.update()

    async def request_permission(e):
        try:
            page.controls.clear()
            page.add(Text("Solicitando permissão..."))
            page.update()
            
            await gl.request_permission_async()
            
            # Testa se consegue obter a localização
            pos = await gl.get_current_position_async()
            if pos:
                page.controls.clear()
                page.add(Text("✅ Permissão concedida!"))
                page.add(Text(f"Localização inicial: {pos.latitude}, {pos.longitude}"))
                page.add(ElevatedButton("Iniciar Rastreamento", on_click=start_tracking))
                page.update()
            else:
                raise Exception("Não foi possível obter a localização")
        except Exception as e:
            page.controls.clear()
            page.add(Text("❌ Erro ao obter permissão"))
            page.add(Text(str(e)))
            page.add(ElevatedButton("Tentar Novamente", on_click=request_permission))
            page.update()

    async def start_tracking(e):
        try:
            page.controls.clear()
            page.add(Text("Iniciando rastreamento..."))
            page.update()
            
            # Configuração do producer
            producer = AIOKafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVER],
                request_timeout_ms=5000,
                api_version="0.10.2"
            )
            
            try:
                await producer.start()
                page.add(Text("✅ Conectado ao Kafka!"))
                page.update()
                
                await send_location_loop(page, producer, gl)
                await producer.stop()
            except Exception as ke:
                page.add(Text(f"❌ Erro ao conectar no Kafka: {str(ke)}"))
                page.add(ElevatedButton("Tentar Novamente", on_click=start_tracking))
                page.update()
                
        except Exception as e:
            page.controls.clear()
            page.add(Text(f"❌ Erro geral: {str(e)}"))
            page.add(ElevatedButton("Tentar Novamente", on_click=start_tracking))
            page.update()

    # Começa com o botão de permissão
    page.add(Text("Primeiro, precisamos da sua permissão para acessar a localização"))
    page.add(ElevatedButton("Permitir Localização", on_click=request_permission))
    page.update()

app(target=main, view=WEB_BROWSER)
