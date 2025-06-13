-- Atualizar a senha do administrador
-- Nova senha será: admin123
UPDATE utilizadores 
SET senha_hash = '$2b$12$9XJ3iZzIX3ldKXGzUj7xR.TQg4QHcXOjZQz0ytkMji9nkrOkTKnMO'
WHERE email = '2016fontespedro@gmail.com';

-- Garantir que a conta é admin
UPDATE utilizadores 
SET is_admin = TRUE 
WHERE email = '2016fontespedro@gmail.com'; 