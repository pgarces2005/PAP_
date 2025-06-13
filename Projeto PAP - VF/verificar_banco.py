import mysql.connector
from mysql.connector import Error

def verificar_e_criar_banco():
    try:
        # Primeiro tenta conectar sem especificar o banco de dados
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        if conn.is_connected():
            print("Conectado ao MySQL!")
            
            cursor = conn.cursor()
            
            # Criar o banco de dados se não existir
            cursor.execute("CREATE DATABASE IF NOT EXISTS pap")
            print("Banco de dados 'pap' verificado/criado!")
            
            # Usar o banco de dados
            cursor.execute("USE pap")
            
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
            print("Tabela mensagens_contato verificada/criada!")
            
            # Verificar se a tabela existe
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
        print(f"Erro ao conectar ao MySQL: {str(e)}")
        print("\nVerifique se:")
        print("1. O servidor MySQL está instalado e rodando")
        print("2. As credenciais (usuário 'root' sem senha) estão corretas")
        print("3. O servidor está aceitando conexões em localhost")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
            print("Conexão fechada.")

if __name__ == "__main__":
    verificar_e_criar_banco() 