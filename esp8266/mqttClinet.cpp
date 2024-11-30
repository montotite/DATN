#include "mqttClinet.h"
#include "Arduino.h"

const String mqttTopicTELEMETRY = "/devices/me/telemetry";
const String mqttTopicATTRIBUTE = "/devices/me/attributes";
const String mqttTopicATTRIBUTE_REQ = "/devices/me/attributes/request";
const String mqttTopicATTRIBUTE_RES = "/devices/me/attributes/response";

MqttClient::MqttClient(Client &client)
{
    mqttClient.setClient(client);
}
// void MqttClient::onMsg(char *topic, byte *payload, unsigned int length)
// {
//     String myTopic = String(topic);
//     String msg = "";
//     for (unsigned int i = 0; i < length; i++)
//     {
//         msg += (char)payload[i];
//     }
//     if ((myTopic == ATTRIBUTE_RES) && onAttribute)
//     {
//         onAttribute(msg);
//     }
// }

void MqttClient::begin(String credential)
{
    mqttClientId = credential;
    TELEMETRY = credential + mqttTopicTELEMETRY;
    ATTRIBUTE = credential + mqttTopicATTRIBUTE;
    ATTRIBUTE_REQ = credential + mqttTopicATTRIBUTE_REQ;
    ATTRIBUTE_RES = credential + mqttTopicATTRIBUTE_RES;

    mqttClient.setServer(mqtt_server, mqtt_server_port);
    // mqttClient.setCallback(onMsg);
}

void MqttClient::usageTelemetry(int seconds)
{
    telemetryFrequency = seconds * 1000;
}

void MqttClient::usageAttribute(int seconds)
{
    attributeFrequency = seconds * 1000;
}

MqttClient &MqttClient::setCallback(CALLBACK_SIGNATURE)
{
    mqttClient.setCallback(callback);
    // this->onAttribute = onAttribute;
    return *this;
}

void MqttClient::reconnected()
{
    String mqttUser = "";
    String mqttPassword = "";
    unsigned long now = millis();
    if (now - lastReconnected > 5000)
    {
        lastReconnected = now;
        if (mqttClient.connect(mqttClientId.c_str(), mqttUser.c_str(), mqttPassword.c_str()))
        {
            Serial.println("connected");
            mqttClient.subscribe(ATTRIBUTE_RES.c_str());
            if (attributeRequestMsg != "")
            {
                mqttClient.publish(ATTRIBUTE_REQ.c_str(), attributeRequestMsg.c_str());
                Serial.print("Request attribute values: ");
                Serial.println(attributeRequestMsg);
            }
        }
        else
        {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" will try again in 5 seconds");
        }
    }
}

void MqttClient::run(unsigned long now)
{
    if (!mqttClient.connected())
    {
        reconnected();
    }
    else
    {
        currentMillis = now * 1000;
        sendAttribute(attributeFrequency);
        sendTelemetry(telemetryFrequency);
        mqttClient.loop();
    }
}

bool MqttClient::isShareAttribute(String topic)
{
    if (topic == ATTRIBUTE_RES)
    {
        return true;
    }
    else
    {
        return false;
    }
}

void MqttClient::requestAttribute(String msg)
{
    attributeRequestMsg = msg;
}

void MqttClient::updateAttribute(String msg)
{
    attributeMsg = msg;
}

void MqttClient::updateTelemetry(String msg)
{
    telemetryMsg = msg;
}

void MqttClient::sendAttribute(unsigned long DELAY_TIME)
{
    if ((DELAY_TIME > 0) && ((currentMillis - lastAttribute) > DELAY_TIME) && (attributeMsg != ""))
    {
        lastAttribute = currentMillis;

        mqttClient.publish(ATTRIBUTE.c_str(), attributeMsg.c_str());
        Serial.println(attributeMsg);
    }
}

void MqttClient::sendTelemetry(unsigned long DELAY_TIME)
{
    if ((DELAY_TIME > 0) && ((currentMillis - lastTelemetry) > DELAY_TIME) && (telemetryMsg != ""))
    {
        lastTelemetry = currentMillis;

        mqttClient.publish(TELEMETRY.c_str(), telemetryMsg.c_str());
        Serial.println(telemetryMsg);
    }
}