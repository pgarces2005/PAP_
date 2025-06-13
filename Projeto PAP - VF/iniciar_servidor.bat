@echo off
echo Verificando ambiente Python...
python --version
if errorlevel 1 (
    echo Erro: Python nao encontrado!
    pause
    exit
)

echo.
echo Instalando/Atualizando dependencias...
pip install flask pymysql werkzeug passlib --quiet
if errorlevel 1 (
    echo Erro ao instalar dependencias!
    pause
    exit
)

echo.
echo Iniciando o servidor...
echo Por favor, aguarde...
echo.
python app.py
pause 