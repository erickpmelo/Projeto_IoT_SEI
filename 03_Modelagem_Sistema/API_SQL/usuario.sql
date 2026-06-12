-- Altera a senha do usuário root atual para Senai@122
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Senai@122';

-- Garante que o banco aplique a nova senha agora mesmo
FLUSH PRIVILEGES;
