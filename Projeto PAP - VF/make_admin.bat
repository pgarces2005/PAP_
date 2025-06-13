@echo off
echo Configurando usuário como administrador...
"C:\xampp\mysql\bin\mysql.exe" -u root < make_admin.sql
if %errorlevel% equ 0 (
    echo Usuário configurado como administrador com sucesso!
) else (
    echo Erro ao configurar usuário como administrador.
    echo Certifique-se de que:
    echo 1. O XAMPP está instalado em C:\xampp
    echo 2. O MySQL está em execução no XAMPP Control Panel
    echo 3. A senha do root está vazia
) 