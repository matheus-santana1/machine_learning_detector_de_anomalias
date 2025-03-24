#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <ArduinoJson.h>
#include <ESPmDNS.h>
#include <Wire.h>
#include <SPIFFS.h>

#define NAME_SERVER "websocket-py"
#define RECONNECT_INTERVAL 1000
#define LED_BUILTIN 2
#define LED 25

String wifiSSID = "";
String wifiPassword = "";

sensors_event_t a, g, temp;
WiFiMulti WiFiMulti;
WebSocketsClient webSocket;
Adafruit_MPU6050 mpu;
ArduinoJson::JsonDocument doc;
String json;
void buildJson()
{
  json = "";
  serializeJson(doc, json);
}

JsonArray json_ax,json_ay,json_az,json_gx,json_gy,json_gz;
int quantidadeAmostras = 0;
int tempoAmostras = 0;
int quantidadeTotalAmostras = 0;
bool amostrando = false;
bool conectadoSocket = false;


void initFS() {
  if (!SPIFFS.begin(true)) {
    Serial.println("Erro ao montar o sistema de arquivos SPIFFS");
    return;
  }
  Serial.println("Sistema de arquivos SPIFFS montado com sucesso");
}

void readWiFiCredentials() {
  File file = SPIFFS.open("/wifi_credentials.txt", "r");
  if (!file) {
    Serial.println("Arquivo de credenciais não encontrado, usando padrões");
    return;
  }
  wifiSSID = file.readStringUntil('\n');
  wifiPassword = file.readStringUntil('\n');
  wifiSSID.trim();
  wifiPassword.trim();
  file.close();
}

void saveWiFiCredentials(const String &ssid, const String &password) {
  File file = SPIFFS.open("/wifi_credentials.txt", "w");
  if (!file) {
    Serial.println("Erro ao abrir arquivo para escrita");
    return;
  }
  file.println(ssid);
  file.println(password);
  file.close();
}

void setup() {
  Serial.begin(115200);
  Serial.println("Serial iniciada!");
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED, OUTPUT);

  initFS();
  readWiFiCredentials();
  
  if (wifiSSID != "" && wifiPassword != "") {
    WiFiMulti.addAP(wifiSSID.c_str(), wifiPassword.c_str());
  }
  if(WiFiMulti.run() == WL_CONNECTED) {
    Serial.printf("Conectado ao wifi %s\n", WiFi.SSID().c_str());
    digitalWrite(LED_BUILTIN, HIGH);
  }else {
    Serial.printf("Não conectado ao wifi\n");
    digitalWrite(LED_BUILTIN, LOW);
  }

  if (!MDNS.begin("Esp32")) {
    Serial.println("Erro MDNS!");
    while (1) {
      delay(1000);
    }
  }

  if (!mpu.begin()) {
    Serial.println("Falha ao inicializar o MPU6050");
    while (1) {
      delay(10);
    }
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.println("MPU6050 iniciado!");

  xTaskCreatePinnedToCore(comunicacaoSocket, "TarefaSerial", 10000, NULL, 1, NULL, 0); // Núcleo 0
  xTaskCreatePinnedToCore(comunicacaoSerial, "TarefaWebSocket", 10000, NULL, 1, NULL, 1); // Núcleo 1
  xTaskCreatePinnedToCore(amostragem, "AmostragemWebSocket", 10000, NULL, 1, NULL, 1); // Núcleo 1
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
	switch(type) {
		case WStype_DISCONNECTED:
      conectadoSocket = false;
      digitalWrite(LED, LOW);
			break;
		case WStype_CONNECTED:
      conectadoSocket = true;
      digitalWrite(LED, HIGH);
			break;
		case WStype_TEXT:
      String mensagem;
      for (size_t i = 0; i < length; i++) {
        mensagem += (char)payload[i];
      }
			processarMensagem(mensagem);
			break;
	}
}

void processarMensagem(String mensagem) {
  ArduinoJson::JsonDocument response;
  DeserializationError error = deserializeJson(response, mensagem.c_str());
  if (error) {
    Serial.printf("Falha na deserialização: %s\n", error.f_str());
  }
  else if (response.containsKey("ssid") && response.containsKey("password")) {
    String newSSID = response["ssid"].as<String>();
    String newPassword = response["password"].as<String>();
    saveWiFiCredentials(newSSID, newPassword);
    if(conectadoSocket) {
      webSocket.sendTXT("{\"status\":\"WiFi credentials updated\"}");
    } else {
      Serial.println("{\"status\":\"WiFi credentials updated\"}");
    }
    ESP.restart();
  }
  else if (response.containsKey("quantidade") && response.containsKey("tempo")) {
    quantidadeAmostras = response["quantidade"];
    tempoAmostras = response["tempo"];
    quantidadeTotalAmostras = quantidadeAmostras * tempoAmostras;
    if(conectadoSocket){
      webSocket.sendTXT("1");
      delay(200);
      amostrando = true;
    }else{
      Serial.printf("%d\n", 1);
      delay(200);
      amostrando = true;
    }
  } else {
    Serial.printf("Chave não encontrada no JSON.\n");
  }
}

void limparArrays() {
  json_ax = doc.createNestedArray("ax");
  json_ay = doc.createNestedArray("ay");
  json_az = doc.createNestedArray("az");
  json_gx = doc.createNestedArray("gx");
  json_gy = doc.createNestedArray("gy");
  json_gz = doc.createNestedArray("gz");
}


void amostragem(void *pvParameters){
  int enviados = 0;
  int qtd_leituras = 0;
  limparArrays();
  while(true){
    if(amostrando){      
      leitura();
      qtd_leituras++;
      vTaskDelay(pdMS_TO_TICKS(1000/quantidadeAmostras));
      if(qtd_leituras%quantidadeAmostras == 0){
        buildJson();
        if(conectadoSocket){
          webSocket.sendTXT(json);
        }else{
          Serial.print(json+"\n");
        }
        limparArrays();
        qtd_leituras = 0;
        enviados++;
      }
      if(enviados*quantidadeAmostras >= quantidadeTotalAmostras) {
        if(conectadoSocket){
          webSocket.sendTXT("0");
          delay(200);
          amostrando = false;
        }else{
          Serial.printf("%d\n", 0);
          delay(200);
          amostrando = false;
        }
        enviados=0;
      } 
    }
    else{
      vTaskDelay(pdMS_TO_TICKS(100));
    }
  }
}


void comunicacaoSerial(void *pvParameters) {
  while (true) {
    if (Serial.available()) {
      processarMensagem(Serial.readString());
    }
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}

void comunicacaoSocket(void *pvParameters) {
  while (true) {
    int n = MDNS.queryService("ws", "tcp");
    if (n == 0) {
      continue;
    }
    else if (MDNS.hostname(0) == NAME_SERVER) {
      webSocket.begin(MDNS.address(0), MDNS.port(0), "/");
	    webSocket.onEvent(webSocketEvent);
	    webSocket.setReconnectInterval(RECONNECT_INTERVAL);
      while(true){
        webSocket.loop();
        vTaskDelay(pdMS_TO_TICKS(10));
      }
    }
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}

void leitura() {
  mpu.getEvent(&a, &g, &temp);
  json_ax.add(a.acceleration.x);
  json_ay.add(a.acceleration.y);
  json_az.add(a.acceleration.z);
  json_gx.add(g.gyro.x);
  json_gy.add(g.gyro.y);
  json_gz.add(g.gyro.z);
}

void loop() {
  //Vazio
  //leitura();
  //buildJson();
  //webSocket.sendTXT(json);
  /*void leitura() {
  mpu.getEvent(&a, &g, &temp);
  doc.clear();
  JsonArray aceleracao = doc.createNestedArray("aceleracao");
  aceleracao.add(a.acceleration.x); //X
  aceleracao.add(a.acceleration.y); //Y
  aceleracao.add(a.acceleration.z); //Z
  JsonArray gyro = doc.createNestedArray("gyro");
  gyro.add(g.gyro.x); //X
  gyro.add(g.gyro.y); //Y
  gyro.add(g.gyro.z); //Z
  doc["temp"] = temp.temperature;
  */
}


