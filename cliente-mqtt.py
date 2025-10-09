# pip install typing_extensions
# pip install aiomqtt[all]

import asyncio
import sys
import os
from aiomqtt import Client
import json
import mysql.connector

# Corrigir o loop no Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# Configurações do MQTT
TOPIC = 'Estufa'
BROKER = 'broker.hivemq.com'
PORT = 1883


#função para inserir no banco de dados
def inserir_mysql(timestamp, temperatura, umidade):
    try:
        conexao = mysql.connector.connect(
            host="localhost",         # ou IP do servidor MySQL
            user="seu_usuario",       # substitua pelo seu usuário
            password="sua_senha",     # substitua pela sua senha
            database="nome_do_banco"  # substitua pelo nome do seu banco
        )

        cursor = conexao.cursor()

        sql = """
        INSERT INTO estufa_dados (timestamp, temperatura, umidade)
        VALUES (%s, %s, %s)
        """
        valores = (timestamp, temperatura, umidade)

        cursor.execute(sql, valores)
        conexao.commit()

        print("Dados inseridos no MySQL com sucesso!")

    except mysql.connector.Error as erro:
        print(f"Erro ao inserir no MySQL: {erro}")

    finally:
        if conexao.is_connected():
            cursor.close()
            conexao.close()





async def main():
    try:
        async with Client(BROKER, PORT) as client:
            await client.subscribe(TOPIC)
            print(f'Subscrito ao tópico {TOPIC}')

            async for message in client.messages:
                print("--")
                payload_str = message.payload.decode()
                print(f'Mensagem recebida no tópico {message.topic}: {payload_str}')
                try:
                    dados = json.loads(payload_str)
                    temperatura = dados.get("Temperatura")
                    umidade = dados.get("Umidade")
                    timestamp = dados.get("Timestamp")

                    print(f"Temperatura: {temperatura} °C")
                    print(f"Umidade: {umidade} %")
                    print(f"Timestamp: {timestamp}")

                    # Aqui você pode adicionar o código para extrair e enviar os dados para o MySQL
                    inserir_mysql(timestamp, temperatura, umidade)

                except json.JSONDecodeError:
                    print("Erro ao decodificar o payload JSON.")


                    
    except Exception as e:
        print(f'Erro inesperado: {e}')

if __name__ == '__main__':
    asyncio.run(main())
