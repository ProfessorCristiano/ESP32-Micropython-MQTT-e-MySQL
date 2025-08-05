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

if __name__ == '__main__':
    asyncio.run(main())
