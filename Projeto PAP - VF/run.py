try:
    from main import app
    
    if __name__ == '__main__':
        print("Iniciando servidor Flask...")
        app.run(debug=True)
except Exception as e:
    print(f"Erro ao iniciar o servidor: {str(e)}")
    input("Pressione Enter para sair...") 