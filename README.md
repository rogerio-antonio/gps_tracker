# Geolocalização com Flet

Aplicação para visualização de dados de geolocalização em tempo real usando Flet e Kafka.

## Requisitos

- Python 3.8+
- Kafka
- Pip

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/geolocalizacao2_flet.git
cd geolocalizacao2_flet
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=localizacao
```

## Uso

1. Inicie o servidor Kafka

2. Execute a aplicação:
```bash
python main.py
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes. 
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 