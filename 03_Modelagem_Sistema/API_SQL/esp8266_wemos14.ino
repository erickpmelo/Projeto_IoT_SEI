#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <DHT.h>

// ======================================================
// DHT11
// ======================================================

#define DHTPIN D2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// ======================================================
// BUZZER
// ======================================================

#define BUZZER D5

// ======================================================
// WIFI
// ======================================================

const char* ssid = "Cyber-Projeto";
const char* password = "Senai@122";

// ======================================================
// IP DO COMPUTADOR
// ======================================================

String servidor = "10.106.202.32";

// ======================================================
// NOME SENSOR
// ======================================================

String nomeSensor = "ESP8266_TEMP";

// ======================================================
// CONTROLE TEMPO
// ======================================================

unsigned long tempoAnterior = 0;

// ======================================================
// SETUP
// ======================================================

void setup() {

  Serial.begin(115200);

  pinMode(BUZZER, OUTPUT);

  dht.begin();

  Serial.println();
  Serial.println("==================================");
  Serial.println("      SISTEMA IOT INICIADO");
  Serial.println("==================================");

  // ======================================================
  // CONECTAR WIFI
  // ======================================================

  WiFi.begin(ssid, password);

  Serial.print("Conectando WiFi");

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("==================================");
  Serial.println("WiFi CONECTADO!");
  Serial.print("IP ESP8266 : ");
  Serial.println(WiFi.localIP());
  Serial.println("==================================");
}

// ======================================================
// LOOP
// ======================================================

void loop() {

  // ======================================================
  // EXECUTA A CADA 5 SEGUNDOS
  // ======================================================

  if (millis() - tempoAnterior > 5000) {

    // ======================================================
    // VERIFICA WIFI
    // ======================================================

    if (WiFi.status() != WL_CONNECTED) {

      Serial.println();
      Serial.println("WiFi DESCONECTADO!");

      WiFi.begin(ssid, password);

      while (WiFi.status() != WL_CONNECTED) {

        delay(500);
        Serial.print(".");
      }

      Serial.println();
      Serial.println("WiFi RECONECTADO!");
    }

    // ======================================================
    // LEITURA DHT11
    // ======================================================

    float temperatura = dht.readTemperature();
    float umidade = dht.readHumidity();

    // ======================================================
    // VALIDAR LEITURA
    // ======================================================

    if (isnan(temperatura) || isnan(umidade)) {

      Serial.println();
      Serial.println("ERRO AO LER DHT11");

      delay(2000);

      return;
    }

    // ======================================================
    // MOSTRAR DADOS
    // ======================================================

    Serial.println();
    Serial.println("========== DADOS ==========");

    Serial.print("Sensor      : ");
    Serial.println(nomeSensor);

    Serial.print("Temperatura : ");
    Serial.print(temperatura, 1);
    Serial.println(" C");

    Serial.print("Umidade     : ");
    Serial.print(umidade, 1);
    Serial.println(" %");

    Serial.println("===========================");

    // ======================================================
    // BUZZER ALERTA
    // ======================================================

    if (temperatura >= 27) {

      digitalWrite(BUZZER, HIGH);

      delay(300);

      digitalWrite(BUZZER, LOW);
    }

    // ======================================================
    // URL API FLASK
    // ======================================================

    String url = "http://" + servidor +
                 ":5000/S.E.I.?sensor=" + nomeSensor +
                 "&temperatura=" + String(temperatura, 1) +
                 "&umidade=" + String(umidade, 1);

    Serial.println();
    Serial.println("Enviando dados...");
    Serial.println(url);

    // ======================================================
    // HTTP
    // ======================================================

    WiFiClient client;

    HTTPClient http;

    http.begin(client, url);

    int httpCode = http.GET();

    // ======================================================
    // RESPOSTA SERVIDOR
    // ======================================================

    if (httpCode == 200) {

      String resposta = http.getString();

      Serial.println();
      Serial.println("DADOS ENVIADOS COM SUCESSO!");
      Serial.print("Servidor: ");
      Serial.println(resposta);

    } else {

      Serial.println();
      Serial.println("ERRO AO ENVIAR!");

      Serial.print("HTTP CODE: ");
      Serial.println(httpCode);

      Serial.println();
      Serial.println("VERIFIQUE:");
      Serial.println("- Flask aberto");
      Serial.println("- IP correto");
      Serial.println("- Firewall Windows");
      Serial.println("- Mesmo WiFi");
    }

    http.end();

    // ======================================================
    // TEMPO
    // ======================================================

    tempoAnterior = millis();
  }
}

esse é o codigo que eu usei no arduino IDE pra se conectr com o vs code e dps o vs code vai se conectar com o google sheets, pra salvar no github dentro da minha pasta api eu faço como
