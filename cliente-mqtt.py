# pip install typing_extensions
# pip install aiomqtt[all]
# pip install flask aiomqtt mysql-connector-python pandas plotly

import asyncio
import sys
import os
from aiomqtt import Client
import json
import mysql.connector
from flask import Flask, render_template, redirect, url_for
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
# Mude apenas o Tópico para o seu projeto
TOPIC = 'Estufa'
BROKER = 'broker.hivemq.com'
PORT = 1883

#carrega o flask como objeto
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
    # devolve a resposta da consulta como um objeto
    return df

# Função para gerar o gráfico
def gerar_grafico(df):
    fig = go.Figure()
    # Linhas mais grossas (aumente 'line' width)
    fig.add_trace(go.Scatter(
        x=df['dado_data'],
        y=df['dado_temp'],
        mode='lines+markers',
        name='Temperatura (°C)',
        line=dict(width=4)  # mais grosso
    ))
    fig.add_trace(go.Scatter(
        x=df['dado_data'],
        y=df['dado_umid'],
        mode='lines+markers',
        name='Umidade (%)',
        line=dict(width=4)  # mais grosso
    ))
    # Layout com fundo preto e área do gráfico cinza
    fig.update_layout(
        title='Temperatura e Umidade ao longo do tempo',
        xaxis_title='Data',
        yaxis_title='Valor',
        plot_bgcolor='#23272e',   # cinza escuro para área do gráfico
        paper_bgcolor='#111215',  # preto para fundo geral
        font=dict(color='#e6eef6'),  # cor do texto
        legend=dict(
            #x=0, y=1,             # legenda à esquerda
            #xanchor='left',
            #yanchor='top',
            font=dict(size=24)    # legendas maiores
        )
    )
    # devolve o gráfico em formato de imagem para html
    return pio.to_html(fig, full_html=False)

# versão anterior mais simples apenas para fins educativos
'''
def gerar_grafico(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['dado_data'], y=df['dado_temp'], mode='lines+markers', name='Temperatura (°C)'))
    fig.add_trace(go.Scatter(x=df['dado_data'], y=df['dado_umid'], mode='lines+markers', name='Umidade (%)'))
    fig.update_layout(title='Temperatura e Umidade ao longo do tempo', xaxis_title='Data', yaxis_title='Valor')
    return pio.to_html(fig, full_html=False)
'''

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
    # devolve o dicionario stats populado com as informações já calculadas
    return stats

#função para inserir no banco de dados
def inserir_mysql(timestamp, temperatura, umidade):
    try:
        conexao = mysql.connector.connect(
            host="localhost",         # ou IP do servidor MySQL
            user="seu_usuario",       # substitua pelo seu usuário
            password="sua_senha",     # substitua pela sua senha
            database="mqtt_estufa"    # substitua pelo nome do seu banco
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
    # Renderiza o index.html ao acessar "/"
    return render_template("index.html")

# Rota do dashboard
@app.route('/dashboard')
def dashboard():
    #coleta dos dados
    df = buscar_dados()
    #gera o gráfico
    grafico_html = gerar_grafico(df)
    #calcula as estatisticas
    stats = calcular_estatisticas(df)
    #devolve o gráfico e as estatisticas como paramentos de html para o dashboard.html
    return render_template(
        "dashboard.html",
        grafico_html=grafico_html,
        stats=stats
    )

# função para iniciar o flask
def iniciar_flask():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

# função assíncrona pois não sabemos quando o Broker MQTT será alimentado
async def mqtt_main():
    try:
        async with Client(BROKER, PORT) as client:
            # espera conexão com o BROKER
            await client.subscribe(TOPIC)
            print(f'Subscrito ao tópico {TOPIC}')
            # quando receber a mensagem do tópico assinado
            async for message in client.messages:
                print("--")
                # a mensagem recebida está no formato MQTT e precisa ser decodificada para o python usá-la a resposta será uma string no formato JSON
                payload_str = message.payload.decode()
                print(f'Mensagem recebida no tópico {message.topic}: {payload_str}')
                try:
                    # Pegamos a string em formato JSON transformamos em um dicionário no Python  
                    dados = json.loads(payload_str)
                    # extraimos dado a dado que queremos usar baseado na chave de cada dado presente no dicionário
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
    
    # Iniciar Flask em uma thread, assim não concorre com a função de coleta de dados
    flask_thread = threading.Thread(target=iniciar_flask)
    flask_thread.start()
    
    # Iniciar MQTT com asyncio, assim só executa quando tem alteração
    asyncio.run(mqtt_main())
