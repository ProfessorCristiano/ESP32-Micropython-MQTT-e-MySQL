import network
import time

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando à rede...', ssid)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    wlan_mac = wlan_sta.config('mac')
    print("MAC Address:",ubinascii.hexlify(wlan_mac).decode().upper())
    print('Conexão estabelecida:', wlan.ifconfig())

# Substitua 'seu_ssid' e 'sua_senha' pelos dados da sua rede Wi-Fi
connect_wifi('seu_ssid', 'sua_senha')
