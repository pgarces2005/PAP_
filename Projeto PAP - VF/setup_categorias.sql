-- Criar tabela de categorias se não existir
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descricao TEXT,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir categorias iniciais
INSERT IGNORE INTO categorias (nome, descricao) VALUES
('Atualizações', 'Últimas atualizações e patches do GTA'),
('DLCs', 'Conteúdos adicionais e expansões'),
('Notícias', 'Notícias gerais sobre o jogo'),
('Guias', 'Guias e tutoriais para jogadores'),
('Comunidade', 'Notícias e eventos da comunidade'),
('Rumores', 'Rumores e especulações sobre futuros lançamentos'); 