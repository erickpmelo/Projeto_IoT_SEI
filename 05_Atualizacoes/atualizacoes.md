# 🔁 Atualizações do Projeto

# v1.0
- Configuração inicial

# v1.1
- Investigação de pinos

# v1.2
- Ajustes na modelagem do sistema
- 
# v1.2
- Mostrar evidencias
---

# 🚨 Problemas e soluções
1. ESP8266 não conectava no computador (Erro HTTP -1)
O Arduino não conseguia mandar dados porque o computador mudou de IP sozinho e o Firewall do Windows estava bloqueando a conexão.

Como resolvemos:
Descobrimos o IP correto usando o comando ipconfig, colocamos esse IP no código do Arduino e desligamos o Firewall para liberar a conexão.



2. Erro no banco de dados (Erro 1045 / HTTP 500)
O sistema até recebia os dados, mas o MySQL não deixava salvar porque o usuário não tinha permissão ou a senha estava errada.

Como resolvemos:
Criamos um novo usuário no MySQL com senha correta e liberamos as permissões para ele conseguir acessar e salvar os dados.



3. Erro de linguagem entre banco (SQL Server x MySQL)
O código estava misturando comandos do SQL Server com MySQL, então dava erro.

Como resolvemos:
Trocamos a biblioteca para mysql.connector e ajustamos os comandos (ex: usamos LIMIT 1 no lugar de TOP 1).



4. Erro ao enviar temperatura (vírgula no número)
O Arduino mandava números assim: 25,5, mas o Python só entende 25.5.

Como resolvemos:
Fizemos o sistema trocar vírgula por ponto automaticamente antes de salvar no banco.


5. Painel aberto para qualquer pessoa
Qualquer pessoa na rede podia acessar os dados digitando o IP.

Como resolvemos:
Criamos uma senha de acesso (token) para bloquear a página e só liberar quem tiver a chave correta.



6. Sistema parava quando o Google Sheets falhava
Se a internet caísse, o sistema inteiro parava.

Como resolvemos:
Fizemos o sistema continuar funcionando no MySQL mesmo se o Google Sheets não funcionasse.



7. Falta de registro de ações (logs)
Não dava para saber quem acessou ou quando deu erro.

Como resolvemos:
Criamos um sistema de logs que salva tudo no banco: horários, erros e acessos.
