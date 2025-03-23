from rich.console import Console
from python_utils.mdns_websocket import MdnsWebSocketServer
import pandas as pd
import joblib
import asyncio
import json

classes = {"Vazio": 0, "Cheio": 1, "Sensor Parado": 2}
pipeline = joblib.load('pipeline.pkl')
console = Console()


def nome_da_classe(value):
    inverted_classes = {v: k for k, v in classes.items()}
    return inverted_classes.get(value, "Classe desconhecida")


def cor_porcentagem(porcentagem):
    if porcentagem >= 70:
        return "[bold green]"
    elif 40 <= porcentagem < 70:
        return "[bold yellow]"
    else:
        return "[bold red]"


def on_message(message, websocket):
    if message != '1' and message != '0':
        data = pd.DataFrame(json.loads(message))
        previsao = pipeline.predict(data)
        probabilidade = pipeline.predict_proba(data)[0][previsao[0]] * 100
        cor = cor_porcentagem(probabilidade)
        msg = f"Previsão: [bold blue]{nome_da_classe(previsao[0])}[/] - Probabilidade: {cor}{probabilidade:.2f}%[/]"
        console.print(msg)


async def on_connect(websocket):
    await server.send_message(json.dumps({"quantidade": 1, "tempo": 9999}))


server = MdnsWebSocketServer(port=2350, on_message=on_message, on_connect=on_connect)


async def main():
    global server
    server_task = asyncio.create_task(server.run_server())
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        server_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
