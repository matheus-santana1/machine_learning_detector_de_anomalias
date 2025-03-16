#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <ArduinoJson.h>
#include <ESPmDNS.h>
#include <Wire.h>

#define SSID "MS"
#define PASSWORD "matheuss189"
#define NAME_SERVER "websocket-py"
#define RECONNECT_INTERVAL 1000

#define LED_BUILTIN 2
#define LED 25

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

void setup() {
  Serial.begin(115200);
  Serial.println("Serial iniciada!");
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED, OUTPUT);

  WiFiMulti.addAP(SSID, PASSWORD);
	while(WiFiMulti.run() != WL_CONNECTED) {
		delay(100);
	}
  Serial.printf("Conectado ao wifi %s\n", SSID);

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
  digitalWrite(LED_BUILTIN, HIGH);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
	switch(type) {
		case WStype_DISCONNECTED:
			Serial.printf("[WSc] Disconnected!\n");
      digitalWrite(LED, LOW);
			break;
		case WStype_CONNECTED:
			Serial.printf("[WSc] Connected to url: %s\n", payload);
			leitura();
      buildJson();
      webSocket.sendTXT(json);
      digitalWrite(LED, HIGH);
			break;
		case WStype_TEXT:
			Serial.printf("[WSc] get text: %s\n", payload);
			webSocket.sendTXT(payload);
			break;
		case WStype_BIN:
		case WStype_ERROR:			
		case WStype_FRAGMENT_TEXT_START:
		case WStype_FRAGMENT_BIN_START:
		case WStype_FRAGMENT:
		case WStype_FRAGMENT_FIN:
			break;
	}
}

void comunicacaoSerial(void *pvParameters) {
  while (true) {
    if (Serial.available()) {
      String mensagem = Serial.readString();
      Serial.println("Mensagem recebida via Serial: " + mensagem);
    }
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}

void comunicacaoSocket(void *pvParameters) {
  while (true) {
    int n = MDNS.queryService("ws", "tcp");
    if (n == 0) {
      Serial.println("Servidor Websocket/MDNS não encontrado.");
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
}

void loop() {
  //Vazio
}
