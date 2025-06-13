-- Remover usuário existente
DELETE FROM utilizadores WHERE email = '2016fontespedro@gmail.com';

-- Criar novo admin com senha simples
INSERT INTO utilizadores (nome, email, senha_hash, is_admin) VALUES
('Administrador', '2016fontespedro@gmail.com', 'admin123', TRUE); 