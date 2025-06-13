-- Remover admin existente
DELETE FROM utilizadores WHERE email = '2016fontespedro@gmail.com';

-- Criar novo admin
-- Senha: admin123
INSERT INTO utilizadores (nome, email, senha_hash, is_admin) VALUES
('Administrador', '2016fontespedro@gmail.com', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLJvHHyTtNDJjbK', TRUE); 