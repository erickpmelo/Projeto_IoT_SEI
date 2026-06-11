-- =========================================================
-- 1. CRIAR DATABASE (SÓ CRIA SE NÃO EXISTIR)
-- =========================================================
CREATE DATABASE IF NOT EXISTS sei;
USE sei;

-- =========================================================
-- 2. TABELA USUARIOS
-- =========================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- 3. TABELA DISPOSITIVOS
-- =========================================================
CREATE TABLE IF NOT EXISTS dispositivos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    ip_dispositivo VARCHAR(100),
    status_dispositivo VARCHAR(50) DEFAULT 'ONLINE',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- INSERIR DISPOSITIVO PADRÃO (Protegido para não duplicar)
INSERT INTO dispositivos (nome, ip_dispositivo, status_dispositivo)
SELECT 'ESP8266 DHT11', '10.106.202.32', 'ONLINE'
WHERE NOT EXISTS (SELECT 1 FROM dispositivos WHERE nome = 'ESP8266 DHT11');


-- =========================================================
-- 4. TABELA LEITURAS (AQUI ESTÁ A MÁGICA: FORMATO ANTIGO/ESTÁVEL)
-- =========================================================
CREATE TABLE IF NOT EXISTS leituras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor VARCHAR(100) NOT NULL,       -- Mantém a coluna de texto direta
    temperatura DECIMAL(5,2),           -- Decimal para não perder os quebrado de temperatura
    umidade DECIMAL(5,2),               -- Decimal para precisão da umidade
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 5. TABELA ALERTAS (ADAPTADA PARA CONECTAR NA LEITURA ANTIGA)
-- =========================================================
CREATE TABLE IF NOT EXISTS alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    leitura_id INT NOT NULL,            -- Conecta direto no ID da leitura acima
    tipo_alerta VARCHAR(50),
    descricao TEXT,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_leitura FOREIGN KEY (leitura_id) REFERENCES leituras(id)
);

-- =========================================================
-- 6. VERIFICAR SE TUDO FOI CRIADO CERTINHO
-- =========================================================
SELECT * FROM usuarios;
SELECT * FROM dispositivos;
SELECT * FROM leituras;
SELECT * FROM alertas;
