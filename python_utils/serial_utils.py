import asyncio
import serial_asyncio


class Serial(asyncio.Protocol):
    def __init__(self, serial_port=None, on_message=None):
        self.SERIAL_PORT = serial_port
        self.transport = None
        self.buffer = ""
        self.on_message = on_message

    def connection_made(self, transport):
        self.transport = transport
        print(f"Conexão serial estabelecida em {self.SERIAL_PORT}")

    def data_received(self, data):
        try:
            self.buffer += data.decode()
            while "\n" in self.buffer:
                line, self.buffer = self.buffer.split("\n", 1)
                self.on_message(line)
        except UnicodeDecodeError as e:
            print(f"❌ Erro ao decodificar dados: {e}")

    def send(self, message):
        if self.transport:
            self.transport.write((message + '\n').encode())
        else:
            print("Erro: conexão serial não estabelecida.")

    @staticmethod
    async def handle_serial_connection(serial_port, baudrate=115200, on_message=None):
        while True:
            try:
                loop = asyncio.get_running_loop()
                protocol = Serial(serial_port=serial_port, on_message=on_message)
                transport, _ = await serial_asyncio.create_serial_connection(
                    loop, lambda: protocol, serial_port, baudrate=baudrate
                )
                return transport, protocol
            except Exception as e:
                print(e)
                await asyncio.sleep(1)
