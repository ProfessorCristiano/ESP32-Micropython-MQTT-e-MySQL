# Professor Cristiano Teixeira.
# Mudanças do original Sob Licença Apache 2.0
# Baseado no original de Copyright (C) 2022, Uri Shaked.
# https://wokwi.com/arduino/projects/315787266233467457

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
from time import localtime
import ntptime
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

#As Instruções abaixo são somente para conectar a internet no wokwi. 
#Remova esssas linhas no projeto físico, ou ajuste-as no arquivo boot.py para sua rede wi-fi.
'''
print("Conectando no WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Conectado no Wi-Fi com Sucesso!")
'''
#Fim da conexão Wi-fi do wokwi


# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "Estufa"

# Definir servidor NTP brasileiro
ntptime.host = "a.st1.ntp.br"

def ajustar_horario_brasil():
    try:
        ntptime.settime()
        print("Horário sincronizado com sucesso!")
        
        # Ajustar fuso horário manualmente (UTC-3)
        rtc = machine.RTC()
        ano, mes, dia, hora, minuto, segundo, _, _ = rtc.datetime()
        rtc.datetime((ano, mes, dia, hora - 3, minuto, segundo, 0, 0))
        print("Horário ajustado para UTC-3")
    except Exception as e:
        print("Falha ao sincronizar horário via NTP:", e)

ajustar_horario_brasil()

sensor = dht.DHT22(Pin(12))

def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    return client

print("Conectando ao MQTT server... ", end="")
client = connect_mqtt()
print("Conectado!")

temperatura_anterior = ""
umidade_anterior = ""

while True:
    #acrescentado um try... except pois dava muito erro de conexão com o MQTT na versão física
    try:
        
        # Ajuste de data e hora.
        print("Ajustando data e hora... ", end="")
        ano, mes, dia, hora, minuto, segundo, _, _ = localtime()
        
        hora -= 3  # Ajuste para UTC-3
        if hora < 0:
            hora += 24
            dia -= 1  # ajuste simples

        timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(ano, mes, dia, hora, minuto, segundo)

        print("Realizando Medições... ", end="")
        sensor.measure()
        temperatura = sensor.temperature()
        umidade = sensor.humidity()
        
        if (umidade != umidade_anterior or temperatura != temperatura_anterior):
            print("Atualizado!")
            message = ujson.dumps({
                "Temperatura": sensor.temperature(),
                "Umidade": sensor.humidity(),
                "Timestamp": timestamp
            })
            print("Publicando no Tópico do MQTT {}: {}".format(MQTT_TOPIC, message))
            client.publish(MQTT_TOPIC, message)
            umidade_anterior = umidade
            temperatura_anterior = temperatura
        else:
            print("Sem mudanças")
        time.sleep(1)
    except OSError as e:
        print("Erro de conexão, tentando reconectar...")
        client = connect_mqtt()
