from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console
from python_utils.mdns_websocket import MdnsWebSocketServer
from python_utils.serial_utils import Serial
from python_utils.menu import Menu
import asyncio
import json
import csv

nome_arquivo = ""
arquivo = None
gravando_arquivo = False
total_amostras = 0
amostras_recebidas = 0
amostras_sec = 0
console = Console()


def on_message(message, websocket=None):
    global nome_arquivo, arquivo, gravando_arquivo, amostras_recebidas
    if message == "1" and not gravando_arquivo:
        try:
            arquivo = open(f"datasets/{nome_arquivo}.csv", mode="w", newline="")
        except FileNotFoundError:
            exit()
        arquivo_csv = csv.writer(arquivo)
        arquivo_csv.writerow(["time", "ax", "ay", "az", "gx", "gy", "gz"])
        gravando_arquivo = True
    elif message == "0" and gravando_arquivo:
        arquivo.close()
        gravando_arquivo = False
    elif gravando_arquivo:
        try:
            dados = json.loads(message)
            ax = dados.get("ax", [])
            ay = dados.get("ay", [])
            az = dados.get("az", [])
            gx = dados.get("gx", [])
            gy = dados.get("gy", [])
            gz = dados.get("gz", [])
            csv.writer(arquivo).writerow([int(asyncio.get_event_loop().time()), ax, ay, az, gx, gy, gz])
            amostras_recebidas += amostras_sec
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
    else:
        print(message)


async def progress_bar():
    global gravando_arquivo, total_amostras, amostras_recebidas, nome_arquivo
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage][green]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(f"[green] Gravando {nome_arquivo}...", total=total_amostras)
        while amostras_recebidas < total_amostras:
            progress.update(task, completed=amostras_recebidas)
            await asyncio.sleep(0.2)
        progress.update(task, completed=total_amostras)
        progress.stop()
        console.print("[bold green]Gravação concluída e arquivo salvo.[/]")


async def main():
    global nome_arquivo, gravando_arquivo, total_amostras, amostras_sec, amostras_recebidas
    menu = Menu()
    SERIAL_PORT = await menu.escolha_de_conexao()
    if SERIAL_PORT:
        transport, protocol = await Serial().handle_serial_connection(SERIAL_PORT, on_message=on_message)
        try:
            while True:
                if not gravando_arquivo:
                    amostras_recebidas = 0
                    [nome_arquivo, amostras_sec, tempo] = await menu.escolha_de_amostras_e_nome_do_arquivo()
                    total_amostras = amostras_sec * tempo
                    protocol.send(json.dumps({"quantidade": amostras_sec, "tempo": tempo}))
                    await progress_bar()
                await asyncio.sleep(1)
        finally:
            transport.close()
    else:
        server = MdnsWebSocketServer(port=2350, on_message=on_message)
        server_task = asyncio.create_task(server.run_server())
        try:
            while True:
                if not gravando_arquivo:
                    amostras_recebidas = 0
                    [nome_arquivo, amostras_sec, tempo] = await menu.escolha_de_amostras_e_nome_do_arquivo()
                    total_amostras = amostras_sec * tempo
                    await server.send_message(json.dumps({"quantidade": amostras_sec, "tempo": tempo}))
                    await progress_bar()
                await asyncio.sleep(1)
        finally:
            server_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
