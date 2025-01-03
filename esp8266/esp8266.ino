#define PZEM_RX_PIN 13
#define PZEM_TX_PIN 12

#include <PZEM004Tv30.h>
#include <SoftwareSerial.h>
#include "ESP8266WiFi.h"
#include <ArduinoJson.h>
#include "WiFiUdp.h"
#include "NTPClient.h"
#include <Servo.h>

#include "mqttClinet.h"
#include "config.h"

const int device = 16; // pin  D0
int relay1_status = LOW;

SoftwareSerial pzemSWSerial(PZEM_RX_PIN, PZEM_TX_PIN);
PZEM004Tv30 pzem(pzemSWSerial);
WiFiUDP ntpUDP;
WiFiClient wifiClient;
MqttClient mqtt(wifiClient);
NTPClient timeClient(ntpUDP);

void onShareAttribute(String msg)
{
    Serial.println(msg);
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, msg);
    if (error)
    {
        Serial.print(msg);
        Serial.print(" | ");
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.f_str());
    }
    else
    {
        if (doc.containsKey("relay1"))
        {
            bool value = doc["relay1"];
            if (value)
            {
                relay1_status = HIGH;
            }
            else
            {
                relay1_status = LOW;
            }
        }
    }
}

void requestAttribute()
{
    DynamicJsonDocument doc(1024);
    doc["sharedKeys"] = "relay1";
    String msg;
    serializeJson(doc, msg);
    mqtt.requestAttribute(msg);
}

void updateAttribute()
{
    DynamicJsonDocument doc(1024);
    doc["SSID"] = WiFi.SSID();
    doc["RSSI_WIFI"] = WiFi.RSSI();
    doc["MAC_ADDRESS"] = WiFi.BSSIDstr();
    doc["IP_ADDRESS"] = WiFi.localIP();
    // doc["LOCAL_TIME"] = timeClient.getFormattedTime();
    // doc["BATTERY_VOLTAGE"] = 12;
    // doc["BATTERY PERCENTAGE"] = 90;
    doc["voltage"] = pzem.voltage();
    doc["current"] = pzem.current();
    doc["power"] = pzem.power();
    doc["energy"] = pzem.energy() * 1000;
    doc["frequency"] = pzem.frequency();
    doc["pf"] = pzem.pf();

    String msg = "";
    serializeJson(doc, msg);
    mqtt.updateAttribute(msg);
}

void updateTelemetry()
{
    DynamicJsonDocument doc(1024);
    doc["RSSI_WIFI"] = WiFi.RSSI();
    doc["voltage"] = pzem.voltage();
    doc["current"] = pzem.current();
    doc["power"] = pzem.power();
    doc["energy"] = pzem.energy() * 1000;
    doc["frequency"] = pzem.frequency();
    doc["pf"] = pzem.pf();

    String msg = "";
    serializeJson(doc, msg);
    mqtt.updateTelemetry(msg);
}

void callback(char *topic, byte *payload, unsigned int length)
{
    String myTopic = String(topic);
    String msg = "";
    for (unsigned int i = 0; i < length; i++)
    {
        msg += (char)payload[i];
    }
    if (mqtt.isShareAttribute(myTopic))
    {
        onShareAttribute(msg);
    }
}

void setup()
{
    Serial.begin(9600);
    WiFi.begin(ssid.c_str(), password.c_str());
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    timeClient.begin();
    timeClient.setTimeOffset((3600 * timeZone));
    requestAttribute();
    mqtt.begin(credential);
    mqtt.setCallback(callback);
    mqtt.usageAttribute(frequencyAttribute);
    mqtt.usageTelemetry(frequencyTelemetry);
    pinMode(device, OUTPUT); // pin device
    digitalWrite(device, LOW);
}

void loop()
{
    timeClient.update();
    unsigned long now = timeClient.getEpochTime();
    mqtt.run(now);
    updateAttribute();
    updateTelemetry();
}