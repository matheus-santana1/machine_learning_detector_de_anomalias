import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from data_analisys import LeitorCsv

vazio = 0  # Equipamento funcionando normalmente
cheio = 1  # Equipamento com anomalia por exemplo

LIQUIDIFICADOR = "liquidificador"
MAQUINADELAVAR = "maquinadelavar"

liquidificador_cheio = LeitorCsv(titulo=f"Liquidificador Cheio",
                                 nome_arquivo=f"datasets/liquidificador_cheio.csv",
                                 taxa_amostragem=300)

liquidificador_vazio = LeitorCsv(titulo=f"Liquidificador Vazio",
                                 nome_arquivo=f"datasets/liquidificador_vazio.csv",
                                 taxa_amostragem=300)

liquidificador2_cheio = LeitorCsv(titulo=f"Liquidificador 2 Cheio",
                                  nome_arquivo=f"datasets/liquidificador2_cheio.csv",
                                  taxa_amostragem=300)

liquidificador2_vazio = LeitorCsv(titulo=f"Liquidificador 2 Vazio",
                                  nome_arquivo=f"datasets/liquidificador2_vazio.csv",
                                  taxa_amostragem=300)

maquinadelavar_cheia = LeitorCsv(titulo=f"Máquina de Lavar Cheia",
                                 nome_arquivo=f"datasets/maquinadelavar_cheia.csv",
                                 taxa_amostragem=300)

maquinadelavar_vazia = LeitorCsv(titulo=f"Máquina de Lavar Vazia",
                                 nome_arquivo=f"datasets/maquinadelavar_vazia.csv",
                                 taxa_amostragem=300)

dataframe = pd.concat(objs=[liquidificador_cheio.to_dataframe(estado=cheio),
                            liquidificador_vazio.to_dataframe(estado=vazio),
                            liquidificador2_cheio.to_dataframe(estado=cheio),
                            liquidificador2_vazio.to_dataframe(estado=vazio),
                            maquinadelavar_cheia.to_dataframe(estado=cheio),
                            maquinadelavar_vazia.to_dataframe(estado=vazio),
                            ], ignore_index=True)

X = dataframe[['ax', 'ay', 'az', 'gx', 'gy', 'gz']]  # Dados de entrada
Y = dataframe['estado']  # Labels (vazio ou cheio)

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42, stratify=Y)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
modelo = RandomForestClassifier(n_estimators=150, random_state=42)
modelo.fit(X_train, y_train)

# Avaliar o modelo
X_test = scaler.transform(X_test)
y_pred = modelo.predict(X_test)
acuracia = accuracy_score(y_test, y_pred)
print(f"Acurácia do modelo: {acuracia:.2f}")

print("\nMatriz de Confusão:")
print(confusion_matrix(y_test, y_pred))

print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))
