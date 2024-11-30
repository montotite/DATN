#include "PubSubClient.h"
#include "Client.h"
#if defined(ESP8266) || defined(ESP32)
#include <functional>
// #define CALLBACK_SIGNATURE std::function<void(String)> onAttribute
#define CALLBACK_SIGNATURE std::function<void(char *, uint8_t *, unsigned int)> callback
#else
#define CALLBACK_SIGNATURE void (*callback)(char *, uint8_t *, unsigned int)
// #define CALLBACK_SIGNATURE void (*onAttribute)(String)
#endif
class MqttClient
{
public:
    MqttClient(Client &client);

    bool isShareAttribute(String);
    void begin(String);
    void updateAttribute(String);
    void updateTelemetry(String);
    void run(unsigned long);
    void requestAttribute(String);
    void usageTelemetry(int);
    void usageAttribute(int);

    MqttClient &setCallback(CALLBACK_SIGNATURE);

private:
    CALLBACK_SIGNATURE;
    // MQTT_CALLBACK_SIGNATURE;
    PubSubClient mqttClient;
    void onMsg(char *, uint8_t *, unsigned int);

    const char *mqtt_server = "103.176.251.60";
    const uint16_t mqtt_server_port = 32792;

    String TELEMETRY = "";
    String ATTRIBUTE = "";
    String ATTRIBUTE_REQ = "";
    String ATTRIBUTE_RES = "";

    unsigned long lastAttribute = 0;
    unsigned long lastTelemetry = 0;
    unsigned long lastReconnected = 0;
    unsigned long ATTRIBUTE_TIME = 0;
    unsigned long TELEMETRY_TIME = 0;
    unsigned long currentMillis = 0;

    String mqttClientId = "";
    String attributeMsg = "";
    String telemetryMsg = "";
    String attributeRequestMsg = "";

    int attributeFrequency = 0;
    int telemetryFrequency = 0;

    void reconnected();
    void sendAttribute(unsigned long);
    void sendTelemetry(unsigned long);
};
