from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Olá! O Flask está funcionando!'

if __name__ == '__main__':
    print("Iniciando servidor de teste...")
    print("Acesse http://127.0.0.1:8080 no seu navegador")
    try:
        app.run(host='127.0.0.1', port=8080, debug=True)
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {str(e)}")
        input("Pressione Enter para sair...") 