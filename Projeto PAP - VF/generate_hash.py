import pymysql
from passlib.hash import bcrypt

# Configuração do banco de dados
def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='pap',
        cursorclass=pymysql.cursors.DictCursor
    )

# Senha que queremos usar
password = "admin123"

# Gerar novo hash
hash = bcrypt.hash(password)

print(f"Senha: {password}")
print(f"Hash gerado: {hash}")

# Atualizar no banco de dados
conn = get_db_connection()
try:
    with conn:
        with conn.cursor() as cursor:
            # Primeiro, verificar se o usuário existe
            cursor.execute("SELECT id FROM utilizadores WHERE email = %s", ('2016fontespedro@gmail.com',))
            user = cursor.fetchone()
            
            if user:
                # Atualizar senha se usuário existe
                cursor.execute("""
                    UPDATE utilizadores 
                    SET senha_hash = %s 
                    WHERE email = %s
                """, (hash, '2016fontespedro@gmail.com'))
            else:
                # Criar novo usuário se não existe
                cursor.execute("""
                    INSERT INTO utilizadores (nome, email, senha_hash, is_admin)
                    VALUES (%s, %s, %s, %s)
                """, ('Administrador', '2016fontespedro@gmail.com', hash, True))
            
            conn.commit()
            print("Banco de dados atualizado com sucesso!")
except Exception as e:
    print(f"Erro: {str(e)}")
finally:
    conn.close() 