-- Primeiro, remover o admin antigo se existir
DELETE FROM utilizadores WHERE email = 'admin@gtanews.com';

-- Inserir novo admin com o email especificado
-- A senha inicial será: admin123
INSERT INTO utilizadores (nome, email, senha_hash, is_admin) VALUES
('Administrador', '2016fontespedro@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLJvHHyTtNDJjbK', TRUE);

-- Se a conta já existir, apenas torná-la admin
UPDATE utilizadores 
SET is_admin = TRUE 
WHERE email = '2016fontespedro@gmail.com'; 