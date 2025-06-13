import pymysql

def check_database():
    try:
        print("\n=== Verificação do Banco de Dados ===")
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='pap',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with conn.cursor() as cursor:
            # Verificar estrutura da tabela
            print("\n1. Estrutura da tabela usuarios:")
            cursor.execute("DESCRIBE usuarios")
            for row in cursor.fetchall():
                print(row)
            
            # Verificar primeiro usuário
            print("\n2. Dados do primeiro usuário:")
            cursor.execute("SELECT * FROM usuarios LIMIT 1")
            user = cursor.fetchone()
            if user:
                for key, value in user.items():
                    print(f"{key}: {type(value)} = {value}")
            else:
                print("Nenhum usuário encontrado")
            
            # Verificar campos vazios
            print("\n3. Verificando campos vazios:")
            cursor.execute("SELECT * FROM usuarios WHERE email IS NULL OR senha_hash IS NULL OR nome IS NULL")
            empty_fields = cursor.fetchall()
            if empty_fields:
                print("Usuários com campos vazios encontrados:")
                for user in empty_fields:
                    print(user)
            else:
                print("Nenhum usuário com campos vazios encontrado")
                
    except Exception as e:
        print(f"\nERRO: {str(e)}")
    finally:
        print("\n=== Fim da Verificação ===")

if __name__ == "__main__":
    check_database() 