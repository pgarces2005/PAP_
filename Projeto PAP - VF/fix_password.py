import bcrypt
import pymysql
import logging
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

logger.info("Iniciando script...")

try:
    # Conectar ao banco de dados
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='pap'
    )
    logger.info("Conectado ao banco de dados")

    # Preparar a senha
    password = "admin123"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    logger.info(f"Hash gerado: {hashed}")

    # Atualizar no banco
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE usuarios SET senha_hash = %s WHERE email = %s",
            (hashed.decode('utf-8'), '2016fontespedro@gmail.com')
        )
        conn.commit()
        logger.info("Senha atualizada com sucesso")

except Exception as e:
    logger.error(f"Erro: {e}")
finally:
    if 'conn' in locals():
        conn.close()
        logger.info("Conexão fechada") 