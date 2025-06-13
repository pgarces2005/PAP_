from main import app
import sys
import os

def main():
    try:
        # Configurar variáveis de ambiente
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        
        print("Python version:", sys.version)
        print("Iniciando o servidor Flask...")
        print("Por favor, acesse: http://127.0.0.1:5000")
        
        # Executar o aplicativo
        app.run(host='127.0.0.1', port=5000, debug=True)
    except Exception as e:
        print(f"\nErro ao iniciar o servidor: {str(e)}")
        input("\nPressione Enter para sair...")

if __name__ == '__main__':
    main() 