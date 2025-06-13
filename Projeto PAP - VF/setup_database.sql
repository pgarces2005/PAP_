-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS pap;
USE pap;

-- Remover tabelas na ordem correta (por causa das chaves estrangeiras)
DROP TABLE IF EXISTS comentarios;
DROP TABLE IF EXISTS noticias;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS mensagens;

-- Criar tabela de usuários
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger para garantir que apenas o email específico possa ser admin
DELIMITER //
CREATE TRIGGER check_admin_email
BEFORE INSERT ON usuarios
FOR EACH ROW
BEGIN
    IF NEW.is_admin = TRUE AND NEW.email != '2016fontespedro@gmail.com' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Apenas o email 2016fontespedro@gmail.com pode ser definido como administrador';
    END IF;
END //

CREATE TRIGGER check_admin_email_update
BEFORE UPDATE ON usuarios
FOR EACH ROW
BEGIN
    IF NEW.is_admin = TRUE AND NEW.email != '2016fontespedro@gmail.com' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Apenas o email 2016fontespedro@gmail.com pode ser definido como administrador';
    END IF;
END //
DELIMITER ;

-- Criar tabela de categorias
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao TEXT
);

-- Criar tabela de notícias
CREATE TABLE noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    conteudo TEXT NOT NULL,
    imagem VARCHAR(255),
    id_autor INT,
    id_categoria INT,
    data_publicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_autor) REFERENCES usuarios(id),
    FOREIGN KEY (id_categoria) REFERENCES categorias(id)
);

-- Criar tabela de comentários
CREATE TABLE comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conteudo TEXT NOT NULL,
    id_utilizador INT,
    id_noticia INT,
    data_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilizador) REFERENCES usuarios(id),
    FOREIGN KEY (id_noticia) REFERENCES noticias(id)
);

-- Criar tabela de mensagens
CREATE TABLE mensagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    assunto VARCHAR(200) NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lida BOOLEAN DEFAULT FALSE
);

-- Inserir usuário admin padrão
INSERT INTO usuarios (nome, email, senha_hash, is_admin) 
VALUES ('Admin', 'admin@admin.com', 'pbkdf2:sha256:600000$dK9Ll9Tz$a4b2c6a3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0', TRUE); 