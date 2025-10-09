# pip install typing_extensions
# pip install aiomqtt[all]

import asyncio
import sys
import os
from aiomqtt import Client

# Corrigir o loop no Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# Configurações do MQTT
TOPIC = 'Estufa'
BROKER = 'broker.hivemq.com'
PORT = 1883

async def main():
    try:
        async with Client(BROKER, PORT) as client:
            await client.subscribe(TOPIC)
            print(f'Subscrito ao tópico {TOPIC}')

            async for message in client.messages:
                print(f'Mensagem recebida no tópico {message.topic}: {message.payload.decode()}')
                # Aqui você pode adicionar o código para extrair e enviar os dados para o MySQL
    except Exception as e:
        print(f'Erro inesperado: {e}')

if __name__ == '__main__':
    asyncio.run(main())

