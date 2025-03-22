from prompt_toolkit.patch_stdout import patch_stdout
import serial.tools.list_ports
import questionary


class Menu:
    @staticmethod
    def _listar_portas():
        return [porta for porta in serial.tools.list_ports.comports() if
                'ttyUSB' in porta.device or 'ttyACM' in porta.device]

    @staticmethod
    async def _escolher_opcao(opcoes, titulo):
        return await questionary.select(
            titulo,
            choices=opcoes
        ).ask_async()

    async def escolha_de_conexao(self):
        opcoes = [porta.device for porta in self._listar_portas()] + ["WiFi"]
        escolha = await self._escolher_opcao(opcoes, "Conexão")
        if escolha == "WiFi":
            return None
        if not escolha:
            return None
        return escolha

    @staticmethod
    async def escolha_de_amostras_e_nome_do_arquivo():
        with patch_stdout():
            while True:
                try:
                    nome_arquivo = await questionary.text(
                        "Nome do arquivo:",
                        validate=lambda valor: (valor.islower() and " " not in valor) or
                                               "O nome do arquivo deve conter apenas letras minúsculas e sem espaços."
                    ).unsafe_ask_async()

                    numero = await questionary.text(
                        "Quantidade de amostras por segundos:",
                        validate=lambda valor: (valor.isdigit() and 0 <= int(
                            valor) <= 500) or "O número deve estar entre 0 e 500."
                    ).unsafe_ask_async()

                    tempo = await questionary.text(
                        "Tempo (segundos):",
                        validate=lambda valor: (valor.isdigit()) or "O valor deve ser um número."
                    ).unsafe_ask_async()
                    return nome_arquivo, int(numero), int(tempo)
                except ValueError:
                    print("❌ Por favor, insira um número válido.")
                except Exception as e:
                    print(f"❌ Erro inesperado: {e}")
