# Professor Cristiano Teixeira.
# Mudanças do original Sob Licença Apache 2.0

"""
Para visualizar os dados:

1. Vá para http://www.hivemq.com/demos/websocket-client/
2. Clique em "Connect"
3. Em "Subscriptions", clique em "Add New Topic Subscription"
4. No campo Tópico, digite "Estufa" e clique em "Subscribe"

Agora clique no sensor DHT22 na simulação,
altere a temperatura/umidade e você verá
a mensagem aparece no MQTT Broker, no painel "Mensagens".
"""

import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "Estufa"

sensor = dht.DHT22(Pin(12))

def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    return client

print("Conectando ao MQTT server... ", end="")
client = connect_mqtt()
print("Conectado!")

prev_weather = ""
while True:
    #acrescentado um try... except pois dava muito erro de conexão com o MQTT na versão física
    try:
        print("Realizando Medições... ", end="")
        sensor.measure()
        message = ujson.dumps({
            "Temperatura": sensor.temperature(),
            "Humidade": sensor.humidity(),
        })
        if message != prev_weather:
            print("Atualizado!")
            print("Publicando no Tópico do MQTT{}: {}".format(MQTT_TOPIC, message))
            client.publish(MQTT_TOPIC, message)
            prev_weather = message
        else:
            print("Sem mudanças")
        time.sleep(1)
    except OSError as e:
        print("Erro de conexão, tentando reconectar...")
        client = connect_mqtt()
