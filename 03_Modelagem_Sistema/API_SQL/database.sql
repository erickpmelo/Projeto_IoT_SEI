-- =========================================================
-- CRIAR DATABASE
-- =========================================================
IF NOT EXISTS (
    SELECT name
    FROM sys.databases
    WHERE name = 'SEI'
)
BEGIN
    CREATE DATABASE SEI;
END
GO

USE SEI;
GO

-- =========================================================
-- TABELA USUARIOS
-- =========================================================
IF NOT EXISTS (
    SELECT *
    FROM sysobjects
    WHERE name='usuarios'
    AND xtype='U'
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
-- TABELA DISPOSITIVOS
-- =========================================================
IF NOT EXISTS (
    SELECT *
    FROM sysobjects
    WHERE name='dispositivos'
    AND xtype='U'
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

-- =========================================================
-- INSERIR DISPOSITIVO PADRÃO
-- =========================================================
INSERT INTO dispositivos (
    nome,
    ip_dispositivo,
    status_dispositivo
)
VALUES (
    'ESP8266 DHT11',
    '10.106.202.32',
    'ONLINE'
);
GO

-- =========================================================
-- TABELA LEITURAS
-- =========================================================
IF NOT EXISTS (
    SELECT *
    FROM sysobjects
    WHERE name='leituras'
    AND xtype='U'
)
BEGIN

CREATE TABLE leituras (

    id INT IDENTITY(1,1) PRIMARY KEY,

    dispositivo_id INT NOT NULL,

    temperatura DECIMAL(5,2),

    umidade DECIMAL(5,2),

    rotacao INT,

    estado VARCHAR(50),

    data_hora DATETIME DEFAULT GETDATE(),

    CONSTRAINT fk_dispositivo
    FOREIGN KEY (dispositivo_id)
    REFERENCES dispositivos(id)

);

END
GO

-- =========================================================
-- TABELA ALERTAS
-- =========================================================
IF NOT EXISTS (
    SELECT *
    FROM sysobjects
    WHERE name='alertas'
    AND xtype='U'
)
BEGIN

CREATE TABLE alertas (

    id INT IDENTITY(1,1) PRIMARY KEY,

    leitura_id INT NOT NULL,

    tipo_alerta VARCHAR(50),

    descricao VARCHAR(MAX),

    data_hora DATETIME DEFAULT GETDATE(),

    CONSTRAINT fk_leitura
    FOREIGN KEY (leitura_id)
    REFERENCES leituras(id)

);

END
GO

-- =========================================================
-- VERIFICAR TABELAS
-- =========================================================
SELECT * FROM usuarios;
GO

SELECT * FROM dispositivos;
GO

SELECT * FROM leituras;
GO

SELECT * FROM alertas;
GO
