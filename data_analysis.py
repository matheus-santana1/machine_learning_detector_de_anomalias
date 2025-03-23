import mpld3
import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

from data_extractor import nome_arquivo


class LeitorCsv:
    def __init__(self, titulo, nome_arquivo, taxa_amostragem, web=False):
        self.titulo = titulo
        self.nome_arquivo = nome_arquivo
        self.taxa_amostragem = taxa_amostragem
        self.web = web
        self.ax_list = []
        self.ay_list = []
        self.az_list = []
        self.gx_list = []
        self.gy_list = []
        self.gz_list = []
        self._arquivo = None
        self._ler_arquivo(nome_arquivo)
        self._tempo_total = np.arange(len(self.ax_list)) / taxa_amostragem

    def _ler_arquivo(self, nome_arquivo):
        self._arquivo = pd.read_csv(nome_arquivo)
        for _, row in self._arquivo.iterrows():
            ax_values = ast.literal_eval(row.iloc[1])
            ay_values = ast.literal_eval(row.iloc[2])
            az_values = ast.literal_eval(row.iloc[3])
            gx_values = ast.literal_eval(row.iloc[4])
            gy_values = ast.literal_eval(row.iloc[5])
            gz_values = ast.literal_eval(row.iloc[6])
            self.ax_list.extend(ax_values)
            self.ay_list.extend(ay_values)
            self.az_list.extend(az_values)
            self.gx_list.extend(gx_values)
            self.gy_list.extend(gy_values)
            self.gz_list.extend(gz_values)

    def to_dataframe(self, estado):
        dados = {
            'ax': self.ax_list,
            'ay': self.ay_list,
            'az': self.az_list,
            'gx': self.gx_list,
            'gy': self.gy_list,
            'gz': self.gz_list,
            'estado': estado
        }
        return pd.DataFrame(dados)

    @staticmethod
    def _normalizar(dados):
        scaler = StandardScaler()
        return scaler.fit_transform(np.array(dados).reshape(-1, 1)).flatten()

    def normalizar_todos_dados(self):
        self.ax_list = self._normalizar(self.ax_list)
        self.ay_list = self._normalizar(self.ay_list)
        self.az_list = self._normalizar(self.az_list)
        self.gx_list = self._normalizar(self.gx_list)
        self.gy_list = self._normalizar(self.gy_list)
        self.gz_list = self._normalizar(self.gz_list)

    def criar_figure(self):
        plt.figure(figsize=(12, 8))
        plt.suptitle(self.titulo, fontsize=18, ha="center")

    def plotar_acelerometro(self):
        plt.subplot(2, 2, 1)
        plt.plot(self._tempo_total, self.ax_list, label='ax')
        plt.plot(self._tempo_total, self.ay_list, label='ay')
        plt.plot(self._tempo_total, self.az_list, label='az')
        plt.xlabel('Tempo (s)')
        plt.ylabel('Aceleração')
        plt.title('Dados de Acelerômetro')
        plt.legend()
        plt.grid()

    def plotar_giroscopio(self):
        plt.subplot(2, 2, 2)
        plt.plot(self._tempo_total, self.gx_list, label='gx')
        plt.plot(self._tempo_total, self.gy_list, label='gy')
        plt.plot(self._tempo_total, self.gz_list, label='gz')
        plt.xlabel('Tempo (s)')
        plt.ylabel('Giroscópio')
        plt.title('Dados de Giroscópio')
        plt.legend()
        plt.grid()

    def _plotar_fft(self, dados, label):
        n = len(dados)
        freq = np.fft.fftfreq(n, d=1 / self.taxa_amostragem)
        mascara = freq > 0
        fft_calculo = np.fft.fft(dados)
        fft_abs = 2.0 * np.abs(fft_calculo / n)
        plt.plot(freq[mascara], fft_abs[mascara], label=label)

    def plotar_fft_acelerometro(self):
        plt.subplot(2, 2, 3)
        self._plotar_fft(self.ax_list, label='ax')
        self._plotar_fft(self.ay_list, label='ay')
        self._plotar_fft(self.az_list, label='az')
        plt.xlabel('Frequência (Hz)')
        plt.ylabel('Magnitude')
        plt.title('FFT - Acelerômetro')
        plt.legend()
        plt.grid()

    def plotar_fft_giroscopio(self):
        plt.subplot(2, 2, 4)
        self._plotar_fft(self.gx_list, label='gx')
        self._plotar_fft(self.gy_list, label='gy')
        self._plotar_fft(self.gz_list, label='gz')
        plt.xlabel('Frequência (Hz)')
        plt.ylabel('Magnitude')
        plt.title('FFT - Giroscópio')
        plt.legend()
        plt.grid()

    def exibir_e_salvar_plot(self, nome_png):
        plt.tight_layout()
        plt.savefig(f"images/{nome_png}.png", dpi=300)
        if self.web:
            mpld3.show()
        plt.close()


nome = "Máquina de Lavar Cheia"
arquivo = "maquinadelavar_cheia"

if __name__ == "__main__":
    csv = LeitorCsv(titulo=nome,
                    nome_arquivo=f"datasets/{arquivo}.csv",
                    taxa_amostragem=300)
    csv.normalizar_todos_dados()
    csv.criar_figure()
    csv.plotar_acelerometro()
    csv.plotar_giroscopio()
    csv.plotar_fft_acelerometro()
    csv.plotar_fft_giroscopio()
    csv.exibir_e_salvar_plot(nome_png=f"{arquivo}")
