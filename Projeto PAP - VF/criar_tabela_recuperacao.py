import mysql.connector

def criar_tabela_recuperacao():
    try:
        # Conectar ao banco de dados
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            database="pap"
        )
        
        cursor = conn.cursor()
        
        # Criar tabela de recuperação de senha
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recuperacao_senha (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_utilizador INT NOT NULL,
                token VARCHAR(255) NOT NULL,
                expiracao DATETIME NOT NULL,
                usado BOOLEAN DEFAULT 0,
                FOREIGN KEY (id_utilizador) REFERENCES usuarios(id)
            )
        """)
        
        conn.commit()
        print("Tabela recuperacao_senha criada com sucesso!")
        
    except mysql.connector.Error as err:
        print(f"Erro ao criar tabela: {err}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    criar_tabela_recuperacao() 