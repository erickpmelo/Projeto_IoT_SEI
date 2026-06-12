-- =========================================================
-- 1. CRIAR DATABASE
-- =========================================================
CREATE DATABASE IF NOT EXISTS sei;
USE sei;
-- =========================================================
-- 2. TABELA USUARIOS
-- Colunas: usuario, senha (compatível com o app.py)
-- =========================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    usuario      VARCHAR(50)  NOT NULL UNIQUE,
    senha        VARCHAR(255) NOT NULL,
    status       VARCHAR(20)  DEFAULT 'Ativo',
    data_cadastro TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);
-- =========================================================
-- 3. TABELA DISPOSITIVOS
-- Colunas: nome, localizacao, mac_address, status, ultima_atualizacao
-- =========================================================
CREATE TABLE IF NOT EXISTS dispositivos (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    nome               VARCHAR(50)  NOT NULL UNIQUE,
    localizacao        VARCHAR(50)  DEFAULT 'Não Definido',
    mac_address        VARCHAR(30)  DEFAULT '00:00:00:00:00:00',
    status             VARCHAR(20)  DEFAULT 'Ativo',
    ultima_atualizacao TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- =========================================================
-- 4. TABELA LEITURAS
-- =========================================================
CREATE TABLE IF NOT EXISTS leituras (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    sensor      VARCHAR(100)   NOT NULL,
    temperatura DECIMAL(5,2),
    umidade     DECIMAL(5,2),
    data_hora   DATETIME       DEFAULT CURRENT_TIMESTAMP
);
-- =========================================================
-- 5. TABELA ALERTAS
-- =========================================================
CREATE TABLE IF NOT EXISTS alertas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    leitura_id  INT  NOT NULL,
    tipo_alerta VARCHAR(50),
    descricao   TEXT,
    data_hora   DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_leitura FOREIGN KEY (leitura_id) REFERENCES leituras(id)
);
-- =========================================================
-- 6. VERIFICAR
-- =========================================================
SELECT * FROM usuarios;
SELECT * FROM dispositivos;
SELECT * FROM leituras;
SELECT * FROM alertas;
