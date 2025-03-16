from mdns_websocket import MdnsWebSocketServer


async def on_message(message, websocket):
    print(f"📩 Mensagem recebida: {message}")


async def on_connect(websocket):
    print("🔗 Cliente conectado!")


async def on_disconnect(websocket):
    print("❌ Cliente desconectado!")


server = MdnsWebSocketServer(port=2350,
                             on_message=on_message,
                             on_connect=on_connect,
                             on_disconnect=on_disconnect)

server.start()
