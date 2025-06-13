-- Adicionar coluna imagem à tabela noticias
ALTER TABLE noticias ADD COLUMN imagem VARCHAR(255) AFTER conteudo; 