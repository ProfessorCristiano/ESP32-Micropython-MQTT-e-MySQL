# pip install typing_extensions
# pip install aiomqtt[all]
# pip install flask aiomqtt mysql-connector-python pandas plotly

import asyncio
import sys
import os
from aiomqtt import Client
import json
import mysql.connector
from flask import Flask, render_template_string
from markupsafe import Markup
import mysql.connector
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import threading

# Corrigir o loop no Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

# Configurações do MQTT
TOPIC = 'Estufa'
BROKER = 'broker.hivemq.com'
PORT = 1883

app = Flask(__name__)

# Função para conectar ao banco de dados e buscar os dados
def buscar_dados():
    conexao = mysql.connector.connect(
        host="localhost",
        user="seu_usuario",
        password="sua_senha",
        database="mqtt_estufa"
    )
    consulta = """
        SELECT dado_data, dado_temp, dado_umid
        FROM dados_estufa
        ORDER BY dado_data
    """
    df = pd.read_sql(consulta, conexao)
    conexao.close()
    return df

# Função para gerar o gráfico
def gerar_grafico(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['dado_data'], y=df['dado_temp'], mode='lines+markers', name='Temperatura (°C)'))
    fig.add_trace(go.Scatter(x=df['dado_data'], y=df['dado_umid'], mode='lines+markers', name='Umidade (%)'))
    fig.update_layout(title='Temperatura e Umidade ao longo do tempo', xaxis_title='Data', yaxis_title='Valor')
    return pio.to_html(fig, full_html=False)

# Função para calcular estatísticas
def calcular_estatisticas(df):
    stats = {
        'umidade_max': df['dado_umid'].max(),
        'umidade_max_data': df.loc[df['dado_umid'].idxmax(), 'dado_data'],
        'umidade_min': df['dado_umid'].min(),
        'umidade_min_data': df.loc[df['dado_umid'].idxmin(), 'dado_data'],
        'temperatura_max': df['dado_temp'].max(),
        'temperatura_max_data': df.loc[df['dado_temp'].idxmax(), 'dado_data'],
        'temperatura_min': df['dado_temp'].min(),
        'temperatura_min_data': df.loc[df['dado_temp'].idxmin(), 'dado_data'],
        'umidade_media': df['dado_umid'].mean(),
        'temperatura_media': df['dado_temp'].mean()
    }
    return stats

#função para inserir no banco de dados
def inserir_mysql(timestamp, temperatura, umidade):
    try:
        conexao = mysql.connector.connect(
            host="localhost",         # ou IP do servidor MySQL
            user="root",       # substitua pelo seu usuário
            password="@ITB123456",     # substitua pela sua senha
            database="mqtt_estufa"  # substitua pelo nome do seu banco
        )

        cursor = conexao.cursor()

        sql = """
        INSERT INTO dados_estufa (dado_data, dado_temp, dado_umid)
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

# Rota principal do site
@app.route('/')
def index():
    df = buscar_dados()
    grafico_html = Markup(gerar_grafico(df))
    stats = calcular_estatisticas(df)

    html = f"""
<html>
<head>
    <title>Dashboard Estufa</title>
    <script>
        setTimeout(function() {{
            window.location.reload();
        }}, 10000); // 10000 ms = 10 segundos
    </script>
</head>
<body>
    <h1>Dashboard Estufa</h1>
    {{% raw %}}
    {grafico_html}
    {{% endraw %}}
    <h2>Estatísticas</h2>
    <ul>
        <li>Umidade Máxima: {stats['umidade_max']}% em {stats['umidade_max_data']}</li>
        <li>Umidade Mínima: {stats['umidade_min']}% em {stats['umidade_min_data']}</li>
        <li>Temperatura Máxima: {stats['temperatura_max']}°C em {stats['temperatura_max_data']}</li>
        <li>Temperatura Mínima: {stats['temperatura_min']}°C em {stats['temperatura_min_data']}</li>
        <li>Média da Umidade: {stats['umidade_media']:.2f}%</li>
        <li>Média da Temperatura: {stats['temperatura_media']:.2f}°C</li>
    </ul>
</body>
</html>
"""
    
    
    return render_template_string(html)


def iniciar_flask():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)


async def mqtt_main():
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
    
    # Iniciar Flask em uma thread
    flask_thread = threading.Thread(target=iniciar_flask)
    flask_thread.start()
    
    # Iniciar MQTT com asyncio
    asyncio.run(mqtt_main())
