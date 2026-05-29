from flask import Flask, request, render_template_string
import gspread
import pyodbc  
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ======================================================
# CONFIGURAÇÕES E INICIALIZAÇÃO
# ======================================================

app = Flask(__name__)

# String de conexão para o seu SQL Server local
db_config = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;"
    "Database=SEI;"
    "Trusted_Connection=yes;"
)

# Caminho do seu arquivo de credenciais do Google Cloud
credenciais_json = r"C:\Users\Aluno\Desktop\S.E.I\ProjetoESP\credencial.json"

# Permissões necessárias para o Google Drive / Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

sheet = None

# Autenticação no Google Sheets
try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(credenciais_json, scope)
    client = gspread.authorize(creds)
    
    # Conecta na planilha "S.E.I." e na aba "S.E.I."
    sheet = client.open("S.E.I.").worksheet("S.E.I.")
    print(" [SUCESSO] Google Sheets conectado com êxito!")
except Exception as e:
    print(f" [AVISO GOOGLE] Não foi possível conectar ao Google Sheets no início: {e}")


# ======================================================
# ROTA PRINCIPAL: EXIBE A INTERFÁCE GRÁFICA (IGUAL À IMAGEM)
# ======================================================
@app.route('/')
def home():
    conexao = None
    cursor = None
    
    # Valores iniciais padrão caso ocorra algum erro ou banco esteja vazio
    sensor_display = "Temperatura Sala"
    temperatura_display = "0.00"
    data_hora_display = "Sem registros"
    status_wifi = "Conectado"
    ip_esp = "10.106.202.39"

    try:
        # Busca o último registro de leitura direto do seu banco de dados atual
        conexao = pyodbc.connect(db_config)
        cursor = conexao.cursor()
        cursor.execute("SELECT TOP 1 sensor, temperatura, data_hora FROM leituras ORDER BY id DESC")
        linha = cursor.fetchone()
        
        if linha:
            # Se o nome no banco for o técnico 'ESP8266_TEMP', exibe amigável como no seu print
            if "TEMP" in str(linha[0]).upper():
                sensor_display = "Temperatura Sala"
            else:
                sensor_display = linha[0]
                
            temperatura_display = f"{float(linha[1]):.2f}"
            # Usa a data e hora exata gravada pelo banco/Arduino
            data_hora_display = linha[2].strftime("%d/%m/%Y %H:%M:%S")
            status_wifi = "Conectado"
    except Exception as e:
        data_hora_display = "Erro servidor"
        status_wifi = "Erro de Conexão"
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

    # Estrutura HTML/CSS injetada para montar o layout idêntico à imagem enviada
    html_dashboard = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Projeto IoT</title>
        <style>
            body {
                background-color: #121824;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: #1e2640;
                width: 360px;
                padding: 40px 20px;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.4);
                text-align: center;
                border: 1px solid #2a365c;
            }
            .titulo {
                color: #4da6ff;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 25px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            .label {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                margin-top: 20px;
                margin-bottom: 5px;
            }
            .valor-texto {
                font-size: 18px;
                color: #d1d5db;
                margin-bottom: 15px;
            }
            .temperatura {
                color: #00cc66;
                font-size: 46px;
                font-weight: bold;
                margin: 25px 0;
            }
        </style>
        <meta http-equiv="refresh" content="2">
    </head>
    <body>
        <div class="card">
            <div class="titulo">🌡️ Projeto IoT</div>
            
            <div class="label">Sensor:</div>
            <div class="valor-texto">{{ sensor }}</div>
            
            <div class="temperatura">{{ temperatura }} °C</div>
            
            <div class="label">Data/Hora:</div>
            <div class="valor-texto">{{ data_hora }}</div>
            
            <div class="label">Status WiFi:</div>
            <div class="valor-texto" style="color: #00cc66;">{{ status_wifi }}</div>
            
            <div class="label">IP do ESP:</div>
            <div class="valor-texto">{{ ip_esp }}</div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_dashboard, sensor=sensor_display, temperatura=temperatura_display, data_hora=data_hora_display, status_wifi=status_wifi, ip_esp=ip_esp)


# ======================================================
# ROTA DO ESP8266 (/S.E.I.) - INTACTA
# ======================================================
@app.route('/S.E.I.')
def receber():
    global sheet
    conexao = None
    cursor = None
    
    try:
        # 1. CAPTURA OS PARÂMETROS VINDOS DA URL DO ESP8266
        sensor_nome = request.args.get('sensor', 'ESP8266_TEMP')
        temperatura = request.args.get('temperatura', '0')
        umidade = request.args.get('umidade', '0')
        agora = datetime.now()

        print("\n================================")
        print("         NOVO DADO RECEBIDO     ")
        print(f" Sensor: {sensor_nome}")
        print(f" Temperatura: {temperatura}°C")
        print(f" Umidade: {umidade}%")
        print("================================")
        
        # Conecta ao SQL Server
        conexao = pyodbc.connect(db_config)
        cursor = conexao.cursor()
        
        # 2. SALVAR NO SQL SERVER (Usando a estrutura estável da imagem: sensor, temperatura, umidade, data_hora)
        query_sql_server = """
            INSERT INTO leituras (
                sensor,        
                temperatura,
                umidade,
                data_hora
            )
            VALUES (?, ?, ?, ?) 
        """
        
        cursor.execute(query_sql_server, (
            sensor_nome, 
            float(temperatura.replace(',', '.')), 
            float(umidade.replace(',', '.')), 
            agora
        ))
        conexao.commit()
        print(" -> Salvo no SQL Server com sucesso!")
        
        # 3. SALVAR NO GOOGLE SHEETS
        if sheet is not None:
            try:
                data_formatada = agora.strftime("%d/%m/%Y %H:%M:%S")
                sheet.append_row([
                    sensor_nome,
                    temperatura,
                    data_formatada
                ])
                print(" -> Enviado para o Google Sheets com sucesso!")
            except Exception as erro_sheets:
                print(f" [ERRO GOOGLE SHEETS]: Falha ao adicionar linha: {erro_sheets}")
        else:
            print(" -> [AVISO]: Google Sheets ignorado porque a planilha não está conectada.")

        return "OK", 200

    except Exception as erro:
        print(f" [ERRO NA REQUISIÇÃO]: {erro}")
        return f"Erro interno do servidor: {erro}", 500
        
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
            print(" -> Conexão SQL Server fechada com segurança.")


# ======================================================
# EXECUÇÃO DO SERVIDOR
# ======================================================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
