import pymysql
from passlib.hash import bcrypt

def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='pap',
        cursorclass=pymysql.cursors.DictCursor
    )

# Dados de teste
email = '2016fontespedro@gmail.com'
password = 'admin123'

# Testar conexão com o banco
conn = get_db_connection()
try:
    with conn:
        with conn.cursor() as cursor:
            # Verificar se o usuário existe
            cursor.execute("SELECT * FROM utilizadores WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                print("Usuário encontrado no banco de dados:")
                print(f"ID: {user['id']}")
                print(f"Nome: {user['nome']}")
                print(f"Email: {user['email']}")
                print(f"É admin? {'Sim' if user['is_admin'] else 'Não'}")
                print(f"Hash atual: {user['senha_hash']}")
                
                # Testar a senha
                try:
                    if bcrypt.verify(password, user['senha_hash']):
                        print("\nSenha está correta!")
                    else:
                        print("\nSenha está incorreta!")
                except Exception as e:
                    print(f"\nErro ao verificar senha: {str(e)}")
                
                # Gerar novo hash para comparação
                new_hash = bcrypt.hash(password)
                print(f"\nNovo hash gerado para teste: {new_hash}")
                
                # Atualizar a senha no banco
                cursor.execute("""
                    UPDATE utilizadores 
                    SET senha_hash = %s 
                    WHERE email = %s
                """, (new_hash, email))
                conn.commit()
                print("\nSenha atualizada no banco de dados!")
                
            else:
                print("Usuário não encontrado no banco de dados!")
except Exception as e:
    print(f"Erro: {str(e)}")
finally:
    conn.close() 