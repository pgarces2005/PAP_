import mysql.connector
from mysql.connector import Error

def criar_tabela_mensagens():
    try:
        # Conectar ao banco de dados
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='pap'
        )
        
        if conn.is_connected():
            print("Conectado ao MySQL!")
            
            cursor = conn.cursor()
            
            # Criar tabela de mensagens
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensagens_contato (
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
            print("Tabela mensagens_contato criada com sucesso!")
            
            # Verificar se a tabela foi criada
            cursor.execute("SHOW TABLES LIKE 'mensagens_contato'")
            if cursor.fetchone():
                print("Verificação: A tabela existe!")
                
                # Mostrar a estrutura da tabela
                cursor.execute("DESCRIBE mensagens_contato")
                columns = cursor.fetchall()
                print("\nEstrutura da tabela:")
                for col in columns:
                    print(f"- {col[0]}: {col[1]}")
            else:
                print("Erro: A tabela não foi criada!")
        
    except Error as e:
        print(f"Erro: {str(e)}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn.is_connected():
            conn.close()
            print("Conexão fechada.")

if __name__ == "__main__":
    criar_tabela_mensagens() 