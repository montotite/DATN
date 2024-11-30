#include "ESP8266WiFi.h"
#include <ArduinoJson.h>
#include "WiFiUdp.h"
#include "NTPClient.h"
#include <Servo.h>

#include "mqttClinet.h"
#include "config.h"



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
        if (doc.containsKey("key1"))
        {
            bool value = doc["key1"];
        }
    }
}

void requestAttribute()
{
    DynamicJsonDocument doc(1024);
    // doc["clientKeys"] = "locker1,locker2,locker3,locker4";
    doc["sharedKeys"] = "locker1,locker2,locker3,locker4";
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
    doc["LOCAL_TIME"] = timeClient.getFormattedTime();
    // doc["BATTERY_VOLTAGE"] = 12;
    // doc["BATTERY PERCENTAGE"] = 90;
    String msg = "";
    serializeJson(doc, msg);
    mqtt.updateAttribute(msg);
}

void updateTelemetry()
{
    DynamicJsonDocument doc(1024);
    doc["RSSI_WIFI"] = WiFi.RSSI();
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
}

void loop()
{
    timeClient.update();
    unsigned long now = timeClient.getEpochTime();
    mqtt.run(now);
    updateAttribute();
    updateTelemetry();
}