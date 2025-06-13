-- Criar tabela de utilizadores se não existir
CREATE TABLE IF NOT EXISTS utilizadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de categorias se não existir
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de notícias se não existir
CREATE TABLE IF NOT EXISTS noticias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    conteudo TEXT NOT NULL,
    imagem VARCHAR(255),
    id_autor INT NOT NULL,
    id_categoria INT NOT NULL,
    data_publicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_autor) REFERENCES utilizadores(id),
    FOREIGN KEY (id_categoria) REFERENCES categorias(id)
);

-- Criar tabela de comentários se não existir
CREATE TABLE IF NOT EXISTS comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conteudo TEXT NOT NULL,
    id_utilizador INT NOT NULL,
    id_noticia INT NOT NULL,
    data_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilizador) REFERENCES utilizadores(id),
    FOREIGN KEY (id_noticia) REFERENCES noticias(id)
);

-- Criar tabela de recuperação de senha se não existir
CREATE TABLE IF NOT EXISTS recuperacao_senha (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_utilizador INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    expiracao DATETIME NOT NULL,
    usado TINYINT(1) DEFAULT 0,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_utilizador) REFERENCES utilizadores(id)
);

-- Inserir categorias iniciais se não existirem
INSERT IGNORE INTO categorias (nome, descricao) VALUES
('Atualizações', 'Últimas atualizações e patches do GTA'),
('DLCs', 'Conteúdos adicionais e expansões'),
('Notícias', 'Notícias gerais sobre o jogo'),
('Guias', 'Guias e tutoriais para jogadores'),
('Comunidade', 'Notícias e eventos da comunidade'),
('Rumores', 'Rumores e especulações sobre futuros lançamentos');

-- Inserir usuário admin se não existir
INSERT IGNORE INTO utilizadores (nome, email, senha_hash, is_admin) VALUES
('Administrador', '2016fontespedro@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLJvHHyTtNDJjbK', TRUE); 