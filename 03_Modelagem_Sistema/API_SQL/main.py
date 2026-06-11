from flask import Flask, request, render_template_string, session, redirect, url_for
import gspread
import mysql.connector
from mysql.connector import Error
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ======================================================
# CONFIGURAÇÕES E INICIALIZAÇÃO
# ======================================================

app = Flask(__name__)
app.secret_key = "chave_secreta_para_cookies"

# Token de segurança para o Modo Administrador
TOKEN_SECRETO = "sei123"

# Configuração para conectar ao seu MySQL Workbench local
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Senai@122',
    'database': 'sei'
}

# 🛠️ AJUSTE DE BANCO: Cria tabelas e colunas de controle se não existirem
def configurar_banco_de_dados():
    conexao = None
    cursor = None
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        
        # 1. Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(50) NOT NULL UNIQUE,
                senha VARCHAR(255) NOT NULL,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Garante coluna de status
        cursor.execute("SHOW COLUMNS FROM usuarios LIKE 'status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE usuarios ADD COLUMN status VARCHAR(20) DEFAULT 'Ativo'")

        # 2. Tabela de dispositivos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispositivos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(50) NOT NULL UNIQUE,
                localizacao VARCHAR(50) DEFAULT 'Não Definido',
                mac_address VARCHAR(30) DEFAULT '00:00:00:00:00:00',
                status VARCHAR(20) DEFAULT 'Ativo',
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """)
        
        # Insere dispositivo de teste padrão caso esteja vazio
        cursor.execute("SELECT COUNT(*) FROM dispositivos")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO dispositivos (nome, localizacao, mac_address, status) 
                VALUES ('Sala_TI', '1º Andar', 'CC:50:E3:DA:B2:2C', 'Ativo')
            """)
            
        conexao.commit()
        print(" [BANCO] Estrutura validada com sucesso!")
    except Exception as e:
        print(f" [ERRO BANCO] Falha ao configurar tabelas: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

configurar_banco_de_dados()

# Integração Google Sheets
credenciais_json = r"C:\Users\Aluno\Desktop\3SEI\credencial.json"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
sheet = None

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(credenciais_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open("S.E.I.").worksheet("S.E.I.")
except Exception as e:
    print(f" [AVISO GOOGLE] Sem Google Sheets: {e}")


# ======================================================
# ROTA PRINCIPAL: ESTILO INSTAGRAM PROFILE
# ======================================================
@app.route('/')
def home():
    if not session.get('usuario_logado'):
        return redirect(url_for('login'))

    conexao = None
    cursor = None
    
    # Valores padrões do card principal
    sensor_display = "Temperatura Sala"
    temperatura_display = "0.00"
    data_hora_display = "Sem registros"
    status_wifi = "Conectado"
    ip_esp = "10.106.202.39"
    temp_minima = "0.00"
    temp_maxima = "0.00"

    # Listas para o feed (as fotos do insta)
    lista_leituras = []
    lista_usuarios = []
    lista_dispositivos = []
    lista_alertas = []

    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        
        # Segurança: Verifica se foi bloqueado em tempo real
        cursor.execute("SELECT status FROM usuarios WHERE usuario = %s", (session.get('usuario_logado'),))
        status_atual_user = cursor.fetchone()
        if status_atual_user and status_atual_user[0] == 'Bloqueado':
            session.clear()
            return redirect(url_for('login', erro="Sua conta foi bloqueada por um administrador!"))
        
        # Último registro geral
        cursor.execute("SELECT sensor, temperatura, data_hora FROM leituras ORDER BY id DESC LIMIT 1")
        linha = cursor.fetchone()
        if linha:
            if "TEMP" in str(linha[0]).upper(): sensor_display = "Temperatura Sala"
            else: sensor_display = linha[0]
            temperatura_display = f"{float(linha[1]):.2f}"
            data_hora_display = linha[2].strftime("%d/%m/%Y %H:%M:%S")

        # Mínima e Máxima
        cursor.execute("SELECT MIN(temperatura), MAX(temperatura) FROM leituras")
        valores_min_max = cursor.fetchone()
        if valores_min_max and valores_min_max[0] is not None:
            temp_minima = f"{float(valores_min_max[0]):.2f}"
            temp_maxima = f"{float(valores_min_max[1]):.2f}"

        # Carrega dados para alimentar as abas do Grid
        cursor.execute("SELECT id, sensor, temperatura, umidade, data_hora FROM leituras ORDER BY id DESC LIMIT 12")
        lista_leituras = cursor.fetchall()

        cursor.execute("SELECT id, usuario, data_cadastro, status FROM usuarios ORDER BY id DESC")
        lista_usuarios = cursor.fetchall()

        cursor.execute("SELECT id, nome, localizacao, mac_address, status, ultima_atualizacao FROM dispositivos ORDER BY id DESC")
        lista_dispositivos = cursor.fetchall()

        cursor.execute("SELECT sensor, temperatura, data_hora FROM leituras WHERE temperatura > 26.0 OR temperatura < 18.0 ORDER BY id DESC LIMIT 12")
        lista_alertas = cursor.fetchall()

    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()

    html_instagram = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InstaIoT - @{{ usuario }}</title>
        <style>
            :root {
                --bg-main: #000000;
                --bg-container: #121212;
                --border-color: #262626;
                --text-primary: #f5f5f5;
                --text-secondary: #a8a8a8;
                --insta-blue: #0095f6;
                --insta-danger: #ed4956;
                --insta-success: #0095f6;
                --card-grid: #1c1c1e;
            }
            body { background-color: var(--bg-main); color: var(--text-primary); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; }
            
            /* Container do app (Simula tela de smartphone centralizada ou tela web limpa) */
            .insta-container { width: 100%; max-width: 600px; min-height: 100vh; background-color: var(--bg-main); border-left: 1px solid var(--border-color); border-right: 1px solid var(--border-color); padding-bottom: 60px; }
            
            /* HEADER DO PERFIL (Igual ao topo da foto do Insta) */
            .profile-header { padding: 25px 20px 10px 20px; display: flex; flex-direction: column; gap: 20px; }
            .profile-top-row { display: flex; align-items: center; justify-content: space-between; }
            .profile-pic-container { width: 77px; height: 77px; border-radius: 50%; background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); display: flex; align-items: center; justify-content: center; }
            .profile-pic { width: 71px; height: 71px; border-radius: 50%; background: #262626; border: 2px solid black; display: flex; align-items: center; justify-content: center; font-size: 32px; }
            
            /* Contadores lado a lado (Posts, Followers, Following) */
            .profile-stats { display: flex; gap: 25px; text-align: center; justify-content: flex-end; flex: 1; margin-left: 20px; }
            .stat-box { flex: 1; }
            .stat-num { font-size: 16px; font-weight: 700; color: var(--text-primary); }
            .stat-label { font-size: 13px; color: var(--text-secondary); }
            
            /* Bio do Perfil */
            .profile-bio { font-size: 14px; line-height: 1.4; padding: 0 5px; }
            .profile-username { font-size: 20px; font-weight: 300; display: inline-block; margin-right: 15px; }
            .bio-name { font-weight: 600; }
            .bio-desc { color: var(--text-secondary); }
            
            /* Botões de Ação estilo Insta */
            .profile-actions { display: flex; gap: 8px; margin-top: 15px; }
            .btn-insta { flex: 1; background-color: #363636; border: none; color: var(--text-primary); padding: 7px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; }
            .btn-insta:hover { background-color: #454545; }
            .btn-primary-insta { background-color: var(--insta-blue); }
            .btn-primary-insta:hover { background-color: #1877f2; }

            /* ABAS DE NAVEGAÇÃO (Ícones abaixo da bio) */
            .insta-tabs { display: flex; border-top: 1px solid var(--border-color); margin-top: 15px; }
            .tab-btn { flex: 1; background: none; border: none; padding: 15px 0; cursor: pointer; display: flex; justify-content: center; align-items: center; opacity: 0.4; transition: opacity 0.2s; border-top: 2px solid transparent; }
            .tab-btn.active { opacity: 1; border-top: 2px solid var(--text-primary); }
            .tab-btn svg { width: 22px; height: 22px; fill: var(--text-primary); }

            /* GRID DE FOTOS / CARDS DE INFORMAÇÃO */
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            
            /* Grid clássico de 3 colunas do Instagram */
            .photo-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px; padding: 3px 0; }
            
            /* Cada "Foto" vira um card moderno contendo os dados */
            .grid-card { background-color: var(--card-grid); aspect-ratio: 1 / 1; display: flex; flex-direction: column; justify-content: space-between; padding: 12px; box-sizing: border-box; border: 1px solid #2c2c2e; position: relative; font-size: 11px; overflow: hidden; }
            .card-top { display: flex; justify-content: space-between; align-items: center; font-weight: bold; color: var(--text-secondary); border-bottom: 1px solid #2c2c2e; padding-bottom: 4px; font-size: 10px; }
            .card-center { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; gap: 2px; }
            .card-main-val { font-size: 20px; font-weight: 800; margin: 4px 0; }
            .card-bottom { font-size: 9px; color: var(--text-secondary); text-align: center; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; }

            /* Customizações de cores para status interno dos cards */
            .val-temp { color: #30d158; }
            .val-umid { color: #0a84ff; }
            .val-alert { color: #ff453a; }
            
            /* Estilo das ações rápidas dentro dos cards */
            .btn-card-action { background: #3a3a3c; border: none; color: white; padding: 3px 6px; border-radius: 4px; font-size: 9px; font-weight: bold; cursor: pointer; text-decoration: none; margin-top: 4px; }
            .btn-card-block { background: var(--insta-danger); }
            .btn-card-unblock { background: #30d158; color: black; }
        </style>
    </head>
    <body>

        <div class="insta-container">
            
            <div class="profile-header">
                <div class="profile-top-row">
                    <div class="profile-pic-container">
                        <div class="profile-pic">🚀</div>
                    </div>
                    
                    <div class="profile-stats">
                        <div class="stat-box">
                            <div class="stat-num">{{ lista_leituras|length }}</div>
                            <div class="stat-label">Leituras</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-num">{{ lista_dispositivos|length }}</div>
                            <div class="stat-label">Dispositivos</div>
                        </div>
                        <div class="stat-box" style="cursor:pointer;" onclick="document.getElementById('btn-tab-alertas').click();">
                            <div class="stat-num" style="color:var(--insta-danger)">{{ lista_alertas|length }}</div>
                            <div class="stat-label">Alertas</div>
                        </div>
                    </div>
                </div>
                
                <div class="profile-bio">
                    <div class="profile-username">@{{ usuario }}</div>
                    <div class="bio-name">Painel de Controle S.E.I. 🌡️</div>
                    <div class="bio-desc">Monitoramento de Hardware & Segurança IoT integrado ao MySQL local.</div>
                    <div style="font-size: 12px; margin-top: 5px; color:var(--text-secondary);">⏰ Sessão iniciada às: <b>{{ horario_login }}</b></div>
                </div>

                <div class="profile-actions">
                    {% if modo_admin %}
                    <a href="/trancar_admin" class="btn-insta" style="background-color: #e6a23c;">🔒 Trancar Funções</a>
                    {% else %}
                    <a href="/verificar_token" class="btn-insta btn-primary-insta">🔑 Ativar Modo Admin</a>
                    {% endif %}
                    <a href="/logout" class="btn-insta">Sair da Conta</a>
                </div>
            </div>

            <div class="insta-tabs">
                <button class="tab-btn active" onclick="switchTab('feed', this)" title="Feed Principal">
                    <svg viewBox="0 0 24 24"><path d="M22 12c0-5.52-4.48-10-10-10S2 6.48 2 12s4.48 10 10 10 10-4.48 10-10zm-10 8c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
                <button class="tab-btn" onclick="switchTab('usuarios', this)" title="Usuários">
                    <svg viewBox="0 0 24 24"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 1.34 5 3s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
                </button>
                <button class="tab-btn" onclick="switchTab('dispositivos', this)" title="Dispositivos">
                    <svg viewBox="0 0 24 24"><path d="M17 1.01L7 1c-1.1 0-1.99.9-1.99 2v18c0 1.1.89 2 1.99 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/></svg>
                </button>
                <button class="tab-btn" id="btn-tab-alertas" onclick="switchTab('alertas', this)" title="Alertas Críticos">
                    <svg viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
                </button>
            </div>

            <div id="tab-feed" class="tab-content active">
                <div style="padding: 10px 15px; font-size: 13px; color: var(--text-secondary); font-weight: bold;">📊 ÚLTIMAS CAPTURAS (LIVE COLETAS)</div>
                <div class="photo-grid">
                    
                    <div class="grid-card" style="background: #1c2e24; border: 1px solid #30d158;">
                        <div class="card-top">
                            <span>🔴 LIVE</span>
                            <span>{{ status_wifi }}</span>
                        </div>
                        <div class="card-center">
                            <span style="font-size: 8px; text-transform: uppercase; color:#30d158;">{{ sensor }}</span>
                            <div class="card-main-val val-temp">{{ temperatura }}°C</div>
                            <span style="font-size: 9px; color: #a8a8a8;">Min: {{ temp_min }}°C</span>
                        </div>
                        <div class="card-bottom" style="color:#30d158;">IP: {{ ip_esp }}</div>
                    </div>

                    {% for leitura in lista_leituras %}
                    <div class="grid-card">
                        <div class="card-top">
                            <span>#{{ leitura[0] }}</span>
                            <span>📊 DATA</span>
                        </div>
                        <div class="card-center">
                            <div class="card-main-val val-temp">{{ "%0.1f" | format(leitura[2]) }}°C</div>
                            <div class="val-umid">💧 {{ "%0.0f" | format(leitura[3]) }}%</div>
                        </div>
                        <div class="card-bottom">{{ leitura[4].strftime("%d/%m %H:%M:%S") }}</div>
                    </div>
                    {% endfor %}
                    
                </div>
            </div>

            <div id="tab-usuarios" class="tab-content">
                <div style="padding: 10px 15px; font-size: 13px; color: var(--text-secondary); font-weight: bold;">👥 CONTROLE DE CONTAS CADASTRADAS</div>
                <div class="photo-grid">
                    {% for user in lista_usuarios %}
                    <div class="grid-card" {% if user[3] == 'Bloqueado' %}style="background:#2c1414;"{% endif %}>
                        <div class="card-top">
                            <span>ID #{{ user[0] }}</span>
                            <span style="color:{% if user[3] == 'Ativo' %}var(--insta-blue){% else %}var(--insta-danger){% endif %}; font-size:9px;">● {{ user[3] }}</span>
                        </div>
                        <div class="card-center">
                            <span style="font-size: 14px; font-weight: bold; word-break: break-all;">@{{ user[1] }}</span>
                            
                            {% if user[1] == session.get('usuario_logado') %}
                                <span style="font-size:9px; color: var(--text-secondary); font-style:italic; margin-top:5px;">Sua Conta</span>
                            {% else %}
                                {% if session.get('modo_admin') %}
                                    {% if user[3] == 'Ativo' %}
                                        <a href="/alterar_status_usuario/{{ user[0] }}/Bloqueado" class="btn-card-action btn-card-block">Bloquear</a>
                                    {% else %}
                                        <a href="/alterar_status_usuario/{{ user[0] }}/Ativo" class="btn-card-action btn-card-unblock">Liberar</a>
                                    {% endif %}
                                {% else %}
                                    <span style="font-size:8px; color: #ff9f43; margin-top:4px;">Requer Admin</span>
                                {% endif %}
                            {% endif %}
                        </div>
                        <div class="card-bottom">Cad: {{ user[2].strftime("%d/%m/%Y") }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div id="tab-dispositivos" class="tab-content">
                <div style="padding: 10px 15px; font-size: 13px; color: var(--text-secondary); font-weight: bold;">📱 MÓDULOS E CHIPS DE HARDWARE</div>
                <div class="photo-grid">
                    {% for dispositivo in lista_dispositivos %}
                    <div class="grid-card" {% if dispositivo[4] == 'Bloqueado' %}style="background:#2c1414;"{% endif %}>
                        <div class="card-top">
                            <span>📍 {{ dispositivo[2] }}</span>
                            <span style="color:{% if dispositivo[4] == 'Ativo' %}#30d158{% else %}var(--insta-danger){% endif %};">● {{ dispositivo[4] }}</span>
                        </div>
                        <div class="card-center">
                            <span style="font-size: 13px; font-weight: bold; color:var(--insta-blue);">{{ dispositivo[1] }}</span>
                            <code style="font-size:8px; color:var(--text-secondary); margin:2px 0;">{{ dispositivo[3] }}</code>
                            
                            {% if session.get('modo_admin') %}
                                {% if dispositivo[4] == 'Ativo' %}
                                    <a href="/alterar_status_dispositivo/{{ dispositivo[0] }}/Bloqueado" class="btn-card-action btn-card-block">Bloquear</a>
                                {% else %}
                                    <a href="/alterar_status_dispositivo/{{ dispositivo[0] }}/Ativo" class="btn-card-action btn-card-unblock">Liberar</a>
                                {% endif %}
                            {% else %}
                                <span style="font-size:8px; color: #ff9f43; margin-top:4px;">Requer Admin</span>
                            {% endif %}
                        </div>
                        <div class="card-bottom">Sinal: {{ dispositivo[5].strftime("%H:%M:%S") }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <div id="tab-alertas" class="tab-content">
                <div style="padding: 10px 15px; font-size: 13px; color: var(--insta-danger); font-weight: bold;">⚠️ ALERTAS DISPARADOS (>26°C OU <18°C)</div>
                <div class="photo-grid">
                    {% if lista_alertas|length == 0 %}
                    <div style="grid-column: span 3; text-align: center; padding: 40px; color: var(--text-secondary); font-size:14px;">
                        ✅ Nenhum alerta crítico registrado!
                    </div>
                    {% endif %}
                    
                    {% for alerta in lista_alertas %}
                    <div class="grid-card" style="background: #2b1114; border: 1px solid var(--insta-danger);">
                        <div class="card-top">
                            <span style="color:var(--insta-danger); font-weight:bold;">⚠️ CRÍTICO</span>
                            <span>LOG</span>
                        </div>
                        <div class="card-center">
                            <div class="card-main-val val-alert">{{ alerta[1] }}°C</div>
                            <span style="font-size: 9px; color: var(--text-secondary);">{{ alerta[0] }}</span>
                        </div>
                        <div class="card-bottom" style="color:var(--text-secondary);">{{ alerta[2].strftime("%d/%m %H:%M:%S") }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>

        </div>

        <script>
            document.addEventListener("DOMContentLoaded", function() {
                // Recupera qual aba o usuário estava olhando antes do refresh automático
                const activeTab = localStorage.getItem('selectedInstaTab') || 'feed';
                const buttons = document.querySelectorAll('.tab-btn');
                
                buttons.forEach(btn => {
                    if(btn.getAttribute('onclick').includes(activeTab)) {
                        switchTab(activeTab, btn);
                    }
                });
            });

            function switchTab(tabName, buttonElement) {
                // Desativa todos os botões e esconde os blocos de grids
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                // Ativa o botão correto e exibe o grid selecionado
                buttonElement.classList.add('active');
                document.getElementById('tab-' + tabName).classList.add('active');
                
                // Salva no armazenamento do navegador
                localStorage.setItem('selectedInstaTab', tabName);
            }

            // Loop de atualização constante a cada 4s (Apenas roda se estiver no feed principal)
            setInterval(function() {
                const currentTab = localStorage.getItem('selectedInstaTab') || 'feed';
                if(currentTab === 'feed') {
                     window.location.reload();
                }
            }, 4000);
        </script>
    </body>
    </html>
    """
    return render_template_string(
        html_instagram, 
        usuario=session.get('usuario_logado'),
        horario_login=session.get('horario_login'),
        modo_admin=session.get('modo_admin'),
        sensor=sensor_display, 
        temperatura=temperatura_display, 
        temp_min=temp_minima,
        temp_max=temp_maxima,
        data_hora=data_hora_display, 
        status_wifi=status_wifi, 
        ip_esp=ip_esp,
        lista_leituras=lista_leituras,
        lista_usuarios=lista_usuarios,
        lista_dispositivos=lista_dispositivos,
        lista_alertas=lista_alertas
    )


# ======================================================
# CONTROLADORES DE STATUS (BLOQUEIOS)
# ======================================================
@app.route('/alterar_status_usuario/<int:user_id>/<string:novo_status>')
def alterar_status_usuario(user_id, novo_status):
    if not session.get('modo_admin'):
        return redirect(url_for('home'))
        
    conexao = None
    cursor = None
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        cursor.execute("UPDATE usuarios SET status = %s WHERE id = %s", (novo_status, user_id))
        conexao.commit()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
    return redirect(url_for('home'))


@app.route('/alterar_status_dispositivo/<int:disp_id>/<string:novo_status>')
def alterar_status_dispositivo(disp_id, novo_status):
    if not session.get('modo_admin'):
        return redirect(url_for('home'))
        
    conexao = None
    cursor = None
    try:
        conexao = mysql.connector.connect(**db_config)
        cursor = conexao.cursor()
        cursor.execute("UPDATE dispositivos SET status = %s WHERE id = %s", (novo_status, disp_id))
        conexao.commit()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if cursor: cursor.close()
        if conexao: conexao.close()
    return redirect(url_for('home'))


# ======================================================
# ROTAS DE VALIDAÇÃO DE TOKEN ADMIN
# ======================================================
@app.route('/verificar_token', methods=['GET', 'POST'])
def verificar_token():
    if not session.get('usuario_logado'):
        return redirect(url_for('login'))

    erro = None
    if request.method == 'POST':
        token_digitado = request.form.get('token_input')
        if token_digitado == TOKEN_SECRETO:
            session['modo_admin'] = True
            return redirect(url_for('home'))
        else:
            erro = "Token Incorreto!"

    html_token = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Token Supervisor</title>
        <style>
            body { background-color: #000000; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin:0;}
            .card { background: #121212; width: 320px; padding: 30px; border-radius: 12px; text-align: center; border: 1px solid #262626; }
            input { width: 90%; padding: 10px; margin-bottom: 15px; background: #000; color: white; border: 1px solid #262626; text-align: center; border-radius: 5px; }
            button { background: #0095f6; color: white; border: none; padding: 10px; width: 97%; font-weight: bold; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="card">
            <h3>🔑 Token de Supervisor</h3>
            <form method="POST">
                <input type="password" name="token_input" placeholder="Digite o Token Admin" required>
                {% if erro %}<p style="color:red;">{{ erro }}</p>{% endif %}
                <button type="submit">Liberar Modo Admin</button>
            </form>
            <br>
            <a href="/" style="color:#a8a8a8; text-decoration:none; font-size:13px;">Voltar ao Perfil</a>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_token, erro=erro)

@app.route('/trancar_admin')
def trancar_admin():
    session.pop('modo_admin', None)
    return redirect(url_for('home'))


# ======================================================
# LOGIN E AUTENTICAÇÃO (MANTIDO COMPATÍVEL COM MYSQL)
# ======================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = request.args.get('erro')
    sucesso = request.args.get('sucesso')

    if request.method == 'POST':
        usuario_digitado = request.form.get('usuario_input').strip()
        senha_digitada = request.form.get('senha_input')

        conexao = None
        cursor = None
        try:
            conexao = mysql.connector.connect(**db_config)
            cursor = conexao.cursor()
            cursor.execute("SELECT senha, status FROM usuarios WHERE usuario = %s", (usuario_digitado,))
            resultado = cursor.fetchone()

            if resultado:
                if resultado[1] == 'Bloqueado':
                    erro = "Esta conta de usuário foi bloqueada por um administrador!"
                elif resultado[0] == senha_digitada:
                    session['usuario_logado'] = usuario_digitado
                    session['horario_login'] = datetime.now().strftime("%H:%M:%S")
                    return redirect(url_for('home'))
                else:
                    erro = "Usuário ou senha inválidos!"
            else:
                erro = "Usuário ou senha inválidos!"
        except Exception as e:
            erro = f"Erro de conexão com o banco: {e}"
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()

    return render_template_string(html_tela_autenticacao, modo="login", erro=erro, sucesso=sucesso)


@app.route('/register', methods=['GET', 'POST'])
def register():
    erro = None
    if request.method == 'POST':
        usuario_digitado = request.form.get('usuario_input').strip()
        senha_digitada = request.form.get('senha_input')
        
        conexao = None
        cursor = None
        try:
            conexao = mysql.connector.connect(**db_config)
            cursor = conexao.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha, status) VALUES (%s, %s, 'Ativo')", (usuario_digitado, senha_digitada))
            conexao.commit()
            return redirect(url_for('login', sucesso="Conta criada com sucesso!"))
        except mysql.connector.IntegrityError:
            erro = "Usuário já existe no sistema!"
        except Exception as e:
            erro = f"Erro ao criar conta: {e}"
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()

    return render_template_string(
