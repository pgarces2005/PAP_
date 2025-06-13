@echo off
echo Configurando o banco de dados...
"C:\xampp\mysql\bin\mysql.exe" -u root < setup_database.sql
if %errorlevel% equ 0 (
    echo Banco de dados configurado com sucesso!
) else (
    echo Erro ao configurar o banco de dados.
    echo Certifique-se de que:
    echo 1. O XAMPP está instalado em C:\xampp
    echo 2. O MySQL está em execução no XAMPP Control Panel
    echo 3. A senha do root está vazia
) 