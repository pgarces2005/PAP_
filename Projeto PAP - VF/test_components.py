import sys
import os

def test_imports():
    print("\n=== Testando importações ===")
    try:
        import flask
        print("✓ Flask importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar Flask: {str(e)}")
        
    try:
        import pymysql
        print("✓ PyMySQL importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar PyMySQL: {str(e)}")
        
    try:
        from passlib.hash import bcrypt
        print("✓ Bcrypt importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar Bcrypt: {str(e)}")
        
    try:
        from flask_wtf.csrf import CSRFProtect
        print("✓ CSRFProtect importado com sucesso")
    except Exception as e:
        print(f"✗ Erro ao importar CSRFProtect: {str(e)}")

def test_database():
    print("\n=== Testando conexão com banco de dados ===")
    try:
        import pymysql
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='pap',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✓ Conexão estabelecida com sucesso")
        
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("✓ Tabelas encontradas:", [list(t.values())[0] for t in tables])
            
            cursor.execute("DESCRIBE usuarios")
            columns = cursor.fetchall()
            print("\nEstrutura da tabela usuarios:")
            for col in columns:
                print(f"- {col['Field']}: {col['Type']} ({col['Null']} null)")
            
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            count = cursor.fetchone()['total']
            print(f"\n✓ Total de usuários: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM usuarios LIMIT 1")
                user = cursor.fetchone()
                print("\nPrimeiro usuário (campos mascarados):")
                for key, value in user.items():
                    if key in ['senha_hash', 'email']:
                        print(f"- {key}: {'*' * len(str(value))}")
                    else:
                        print(f"- {key}: {value}")
        
    except Exception as e:
        print(f"✗ Erro: {str(e)}")

def test_flask():
    print("\n=== Testando inicialização do Flask ===")
    try:
        from flask import Flask
        app = Flask(__name__)
        app.secret_key = os.urandom(24)
        print("✓ Flask app criada com sucesso")
        
        from flask_wtf.csrf import CSRFProtect
        csrf = CSRFProtect(app)
        print("✓ CSRF configurado com sucesso")
        
        print("\nConfigurações da app:")
        print(f"- Debug: {app.debug}")
        print(f"- Testing: {app.testing}")
        print(f"- Secret Key definida: {'Sim' if app.secret_key else 'Não'}")
        
    except Exception as e:
        print(f"✗ Erro: {str(e)}")

if __name__ == "__main__":
    print("Iniciando testes de componentes...")
    test_imports()
    test_database()
    test_flask()
    print("\nTestes concluídos!") 