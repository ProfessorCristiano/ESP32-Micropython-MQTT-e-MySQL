import asyncio
from asyncio_mqtt import Client

TOPIC = 'Estufa'
BROKER = 'broker.hivemq.com'
PORT = 1883

async def main():
    async with Client(BROKER, PORT) as client:
        await client.subscribe(TOPIC)
        print(f'Subscrito ao tópico {TOPIC}')

        async with client.messages() as messages:
            async for message in messages:
                print(f'Mensagem recebida no tópico {message.topic}: {message.payload.decode()}')
                # acrescentar depois o código para  extrair as informações do message.payload.decode() e enviar para o mysql.

if __name__ == '__main__':
    asyncio.run(main())
