USE pap;

-- Atualizar o usuário para ser administrador
UPDATE usuarios 
SET is_admin = TRUE 
WHERE email = '2016fontespedro@gmail.com';

-- Mostrar o status do usuário
SELECT id, nome, email, is_admin 
FROM usuarios 
WHERE email = '2016fontespedro@gmail.com'; 