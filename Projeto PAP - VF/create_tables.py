import pymysql
import os

def get_db_connection():
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Conexão com o MySQL estabelecida com sucesso!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao MySQL: {str(e)}")
        return None

def create_database():
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cursor:
            # Criar banco de dados
            print("Criando banco de dados 'pap'...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS pap")
            cursor.execute("USE pap")
            
            # Criar tabela de usuários
            print("Criando tabela 'usuarios'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    senha_hash VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Criar tabela de categorias
            print("Criando tabela 'categorias'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(50) NOT NULL UNIQUE,
                    descricao TEXT
                )
            """)
            
            # Criar tabela de notícias
            print("Criando tabela 'noticias'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS noticias (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(200) NOT NULL,
                    conteudo TEXT NOT NULL,
                    imagem VARCHAR(255),
                    id_autor INT,
                    id_categoria INT,
                    data_publicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_autor) REFERENCES usuarios(id),
                    FOREIGN KEY (id_categoria) REFERENCES categorias(id)
                )
            """)
            
            # Criar tabela de comentários
            print("Criando tabela 'comentarios'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comentarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    conteudo TEXT NOT NULL,
                    id_utilizador INT,
                    id_noticia INT,
                    data_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_utilizador) REFERENCES usuarios(id),
                    FOREIGN KEY (id_noticia) REFERENCES noticias(id)
                )
            """)
            
            # Criar tabela de mensagens
            print("Criando tabela 'mensagens'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensagens (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    assunto VARCHAR(200) NOT NULL,
                    mensagem TEXT NOT NULL,
                    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    lida BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Criar usuário admin padrão
            print("Criando usuário admin padrão...")
            cursor.execute("""
                INSERT IGNORE INTO usuarios (nome, email, senha_hash, is_admin)
                VALUES ('Admin', 'admin@admin.com', 'pbkdf2:sha256:600000$dK9Ll9Tz$a4b2c6a3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0', TRUE)
            """)
            
            conn.commit()
            print("Banco de dados e tabelas criados com sucesso!")
            
    except Exception as e:
        print(f"Erro ao criar banco de dados: {str(e)}")
    finally:
        conn.close()
        print("Conexão fechada.")

if __name__ == '__main__':
    create_database() 