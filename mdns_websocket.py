import asyncio
import websockets
from zeroconf import Zeroconf, ServiceInfo
import socket
import logging


class MdnsWebSocketServer:
    def __init__(self, port, on_message=None, on_connect=None, on_disconnect=None):
        self.port = port
        self.on_message = on_message
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.clients = set()

    @staticmethod
    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        except Exception as e:
            logging.error(e)
            local_ip = socket.gethostname()
        finally:
            s.close()
        return local_ip

    async def register_mdns_service(self):
        zeroconf = Zeroconf()
        ip = self.get_local_ip()
        info = ServiceInfo(
            type_="_ws._tcp.local.",
            name="esp32serverpy._ws._tcp.local.",
            addresses=[socket.inet_aton(ip)],
            port=self.port,
            properties={"path": "/"},
            server="websocket-py.local.",
        )
        await zeroconf.async_register_service(info)
        print(f"Serviço mDNS registrado em {ip}:{self.port}")

    async def handler(self, websocket):
        self.clients.add(websocket)
        if self.on_connect:
            await self.on_connect(websocket)
        try:
            async for message in websocket:
                await self.on_message(message, websocket)
        except (websockets.exceptions.ConnectionClosed, websockets.exceptions.ConnectionClosedError):
            pass
        finally:
            self.clients.remove(websocket)
            if self.on_disconnect:
                await self.on_disconnect(websocket)

    async def run_server(self):
        await self.register_mdns_service()
        async with websockets.serve(self.handler, "", self.port):
            print(f"Servidor WebSocket iniciado na porta {self.port}")
            await asyncio.Future()

    def start(self):
        asyncio.run(self.run_server())


if __name__ == "__main__":
    server = MdnsWebSocketServer(port=2350)
    server.start()
