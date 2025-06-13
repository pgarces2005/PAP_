import pymysql

def verificar_tabela():
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
        
        # Verificar se a tabela existe
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.tables 
            WHERE table_schema = 'pap' 
            AND table_name = 'mensagens_contato'
        """)
        
        result = cursor.fetchone()
        if result['count'] > 0:
            print("A tabela mensagens_contato existe!")
            
            # Mostrar a estrutura da tabela
            cursor.execute("DESCRIBE mensagens_contato")
            columns = cursor.fetchall()
            print("\nEstrutura da tabela:")
            for col in columns:
                print(f"- {col['Field']}: {col['Type']}")
        else:
            print("A tabela mensagens_contato NÃO existe!")
            print("\nTentando criar a tabela...")
            
            cursor.execute("""
                CREATE TABLE mensagens_contato (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    assunto VARCHAR(200) NOT NULL,
                    mensagem TEXT NOT NULL,
                    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
                    lida BOOLEAN DEFAULT FALSE
                )
            """)
            conn.commit()
            print("Tabela criada com sucesso!")
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    verificar_tabela() 