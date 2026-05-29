-- =========================================================
-- 1. CRIAR DATABASE (SÓ CRIA SE NÃO EXISTIR)
-- =========================================================
IF NOT EXISTS (
    SELECT name FROM sys.databases WHERE name = 'SEI'
)
BEGIN
    CREATE DATABASE SEI;
END
GO

USE SEI;
GO

-- =========================================================
-- 2. TABELA USUARIOS
-- =========================================================
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U'
)
BEGIN
    CREATE TABLE usuarios (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(MAX) NOT NULL,
        criado_em DATETIME DEFAULT GETDATE()
    );
END
GO

-- =========================================================
-- 3. TABELA DISPOSITIVOS
-- =========================================================
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='dispositivos' AND xtype='U'
)
BEGIN
    CREATE TABLE dispositivos (
        id INT IDENTITY(1,1) PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        ip_dispositivo VARCHAR(100),
        status_dispositivo VARCHAR(50) DEFAULT 'ONLINE',
        criado_em DATETIME DEFAULT GETDATE()
    );
END
GO

-- INSERIR DISPOSITIVO PADRÃO 
IF NOT EXISTS (SELECT 1 FROM dispositivos WHERE nome = 'ESP8266 DHT11')
BEGIN
    INSERT INTO dispositivos (nome, ip_dispositivo, status_dispositivo)
    VALUES ('ESP8266 DHT11', '10.106.202.32', 'ONLINE');
END
GO


-- =========================================================
-- 4. TABELA LEITURAS 
-- =========================================================
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='leituras' AND xtype='U'
)
BEGIN
    CREATE TABLE leituras (
        id INT IDENTITY(1,1) PRIMARY KEY,
        sensor VARCHAR(100) NOT NULL,     
        temperatura DECIMAL(5,2),          
        umidade DECIMAL(5,2),               
        data_hora DATETIME DEFAULT GETDATE()
    );
END
GO


-- =========================================================
-- 5. TABELA ALERTAS 
-- =========================================================
IF NOT EXISTS (
    SELECT * FROM sysobjects WHERE name='alertas' AND xtype='U'
)
BEGIN
    CREATE TABLE alertas (
        id INT IDENTITY(1,1) PRIMARY KEY,
        leitura_id INT NOT NULL,           
        tipo_alerta VARCHAR(50),
        descricao VARCHAR(MAX),
        data_hora DATETIME DEFAULT GETDATE(),
        CONSTRAINT fk_leitura FOREIGN KEY (leitura_id) REFERENCES leituras(id)
    );
END
GO

-- =========================================================
-- 6. VERIFICAR SE TUDO FOI CRIADO CERTINHO
-- =========================================================
SELECT * FROM usuarios;
GO
SELECT * FROM dispositivos;
GO
SELECT * FROM leituras;
GO
SELECT * FROM alertas;
GO
