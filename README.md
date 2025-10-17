# ESP32-Micropython-MQTT-e-MySQL
Solução para um exemplo de aplicação para ESP32 em MicroPython publicando em um MQTT e outra aplicação e transferindo os dados do MQTT para um banco de dados MySQL.

Funcionamento:
- Os arquivos main.py e boot.py não os arquivos para rodar no ESP32 com acesso a internet via wi-fi o sensor DHT11 coletando os dados e enviando para o Broker MQTT HyveMQ em https://www.hivemq.com/demos/websocket-client/.

- O arquivo cliente-mqtt.py tem que rodar em um computador com acesso a internet e acesso a um banco de dados MariaDB ou MySQL (script para a criação do exemplo em 'dados.sql'), no caso desse código o serviço do banco roda no próprio computador que executa a aplicação, mas pode ser outro inclusive recomendado que seja um banco acessivel via internet.

- Após isso será possivel acessar um dashboard simples com os dados do banco de dados exibidos em forma de gráfico de linhas.

OBS: o gráfico pode ficar visualmente feio se a base de dados estiver com intervalos de tempo grandes, como por exemplo dias entre as utilizações. A Sugestão é para demonstração sempre excluir a base no banco e recriá-la na hora da demonstração. 
