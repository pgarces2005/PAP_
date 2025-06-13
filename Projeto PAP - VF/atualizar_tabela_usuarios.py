import pymysql

def atualizar_tabela():
    try:
        # Conectar ao banco de dados
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='pap',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        # Verificar se a coluna is_admin existe
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'pap' 
            AND TABLE_NAME = 'usuarios' 
            AND COLUMN_NAME = 'is_admin'
        """)
        
        if not cursor.fetchone():
            print("Adicionando coluna is_admin...")
            cursor.execute("""
                ALTER TABLE usuarios 
                ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT FALSE
            """)
            
            # Definir o usuário com email 2016fontespedro@gmail.com como admin
            cursor.execute("""
                UPDATE usuarios 
                SET is_admin = TRUE 
                WHERE email = '2016fontespedro@gmail.com'
            """)
            
            conn.commit()
            print("Coluna is_admin adicionada e admin configurado com sucesso!")
        else:
            print("Coluna is_admin já existe!")
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    atualizar_tabela() 