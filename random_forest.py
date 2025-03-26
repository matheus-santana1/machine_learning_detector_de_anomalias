import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from data_analysis import LeitorCsv
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier(n_estimators=150, random_state=42))
])

classes = {"Vazio": 0, "Cheio": 1, "Sensor Parado": 2}

sensor_parado = LeitorCsv(titulo=f"Sensor Parado",
                          nome_arquivo=f"datasets/sensor_parado.csv",
                          taxa_amostragem=300)

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
                                  
liquidificador3_cheio = LeitorCsv(titulo=f"Liquidificador 3 Cheio",
                                  nome_arquivo=f"datasets/liquidificador3_cheio.csv",
                                  taxa_amostragem=300)

liquidificador3_vazio = LeitorCsv(titulo=f"Liquidificador 3 Vazio",
                                  nome_arquivo=f"datasets/liquidificador3_vazio.csv",
                                  taxa_amostragem=300)
                                  
liquidificador4_cheio = LeitorCsv(titulo=f"Liquidificador 4 Cheio",
                                  nome_arquivo=f"datasets/liquidificador4_cheio.csv",
                                  taxa_amostragem=300)

liquidificador4_vazio = LeitorCsv(titulo=f"Liquidificador 4 Vazio",
                                  nome_arquivo=f"datasets/liquidificador4_vazio.csv",
                                  taxa_amostragem=300)
                                  
liquidificador5_cheio = LeitorCsv(titulo=f"Liquidificador 5 Cheio",
                                  nome_arquivo=f"datasets/liquidificador5_cheio.csv",
                                  taxa_amostragem=300)

liquidificador5_vazio = LeitorCsv(titulo=f"Liquidificador 5 Vazio",
                                  nome_arquivo=f"datasets/liquidificador5_vazio.csv",
                                  taxa_amostragem=300)
                                  
liquidificador6_cheio = LeitorCsv(titulo=f"Liquidificador 6 Cheio",
                                  nome_arquivo=f"datasets/liquidificador6_cheio.csv",
                                  taxa_amostragem=300)

liquidificador6_vazio = LeitorCsv(titulo=f"Liquidificador 6 Vazio",
                                  nome_arquivo=f"datasets/liquidificador6_vazio.csv",
                                  taxa_amostragem=300)
                       
liquidificador7_cheio = LeitorCsv(titulo=f"Liquidificador 7 Cheio",
                                  nome_arquivo=f"datasets/liquidificador7_cheio.csv",
                                  taxa_amostragem=300)

liquidificador7_vazio = LeitorCsv(titulo=f"Liquidificador 7 Vazio",
                                  nome_arquivo=f"datasets/liquidificador7_vazio.csv",
                                  taxa_amostragem=300)
                                  
liquidificador8_cheio = LeitorCsv(titulo=f"Liquidificador 8 Cheio",
                                  nome_arquivo=f"datasets/liquidificador8_cheio.csv",
                                  taxa_amostragem=300)

liquidificador8_vazio = LeitorCsv(titulo=f"Liquidificador 8 Vazio",
                                  nome_arquivo=f"datasets/liquidificador8_vazio.csv",
                                  taxa_amostragem=300)

maquinadelavar_cheia = LeitorCsv(titulo=f"Máquina de Lavar Cheia",
                                 nome_arquivo=f"datasets/maquinadelavar_cheia.csv",
                                 taxa_amostragem=300)

maquinadelavar_vazia = LeitorCsv(titulo=f"Máquina de Lavar Vazia",
                                 nome_arquivo=f"datasets/maquinadelavar_vazia.csv",
                                 taxa_amostragem=300)

dataframe = pd.concat(objs=[sensor_parado.to_dataframe(estado=classes["Sensor Parado"]),
                            liquidificador_cheio.to_dataframe(estado=classes["Cheio"]),
                            liquidificador_vazio.to_dataframe(estado=classes["Vazio"]),
                            liquidificador2_cheio.to_dataframe(estado=classes["Cheio"]),
                            liquidificador2_vazio.to_dataframe(estado=classes["Vazio"]),
                            liquidificador3_cheio.to_dataframe(estado=classes["Cheio"]),
                            liquidificador3_vazio.to_dataframe(estado=classes["Vazio"]),
                            liquidificador4_cheio.to_dataframe(estado=classes["Cheio"]),
                            liquidificador4_vazio.to_dataframe(estado=classes["Vazio"]),
                            liquidificador5_cheio.to_dataframe(estado=classes["Cheio"]),
                            liquidificador5_vazio.to_dataframe(estado=classes["Vazio"]),
                            liquidificador6_cheio.to_dataframe(estado=classes["Cheio"]),
                            liquidificador6_vazio.to_dataframe(estado=classes["Vazio"]),
                            liquidificador7_cheio.to_dataframe(estado=classes["Cheio"]),
                            liquidificador7_vazio.to_dataframe(estado=classes["Vazio"]),
                            liquidificador8_cheio.to_dataframe(estado=classes["Cheio"]),
                            liquidificador8_vazio.to_dataframe(estado=classes["Vazio"]),
                            maquinadelavar_cheia.to_dataframe(estado=classes["Cheio"]),
                            maquinadelavar_vazia.to_dataframe(estado=classes["Vazio"]),
                            ], ignore_index=True)

X = dataframe[['ax', 'ay', 'az', 'gx', 'gy', 'gz']]  # Dados de entrada
Y = dataframe['estado']  # Labels (vazio ou cheio)

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42, stratify=Y)
pipeline.fit(X_train, y_train)

# Avaliar o modelo
y_pred = pipeline.predict(X_test)
acuracia = accuracy_score(y_test, y_pred)
print(f"Acurácia do modelo: {acuracia:.2f}")

print("\nMatriz de Confusão:")
print(confusion_matrix(y_test, y_pred))

print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred))

# joblib.dump(pipeline, 'pipeline.pkl')
