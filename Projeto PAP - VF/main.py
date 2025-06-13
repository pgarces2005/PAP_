import logging
import sys
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
import pymysql.cursors
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.hash import bcrypt
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask import render_template_string

# Configurar logging
logging.basicConfig(
    filename='debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Também enviar logs para o console
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

try:
    logging.info("Iniciando importações...")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    logging.info("Variáveis de ambiente carregadas")

    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config['UPLOAD_FOLDER'] = 'static/img'
    app.config['WTF_CSRF_SECRET_KEY'] = app.secret_key  # Usar a mesma chave secreta para CSRF
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # Desabilitar limite de tempo do token CSRF
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Desabilitar verificação SSL para desenvolvimento

    # Configurar proteção CSRF
    csrf = CSRFProtect(app)

    logging.info("CSRF configurado com sucesso")

    # Handler para erros CSRF
    @app.errorhandler(400)
    def handle_csrf_error(e):
        print(f"Erro CSRF detectado: {str(e)}")
        logging.error(f"Erro CSRF detectado: {str(e)}")
        print(f"Headers da requisição: {dict(request.headers)}")
        print(f"Form data: {dict(request.form)}")
        
        # Verificar se é uma requisição AJAX usando o cabeçalho X-Requested-With
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Erro de segurança. Por favor, recarregue a página.'}), 400
            
        flash('Erro de segurança. Por favor, tente novamente.', 'danger')
        return redirect(request.referrer or url_for('index'))

    # Configurações adicionais para sessão
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Sessão dura 7 dias
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Cookies não acessíveis via JavaScript
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Proteção contra CSRF

    logging.info("Flask app criada com sucesso")

    # Adicionar função para obter o ano atual
    @app.context_processor
    def utility_processor():
        def get_year():
            return datetime.now().year
        return dict(now=get_year)

    # Configurar conexão com o banco de dados
    def get_db_connection():
        try:
            print("\n=== Debug Conexão BD ===")
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='',
                database='pap',
                cursorclass=pymysql.cursors.DictCursor
            )
            print("Conexão estabelecida com sucesso!")
            print("===================\n")
            return connection
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {str(e)}")
            logging.error(f"Erro ao conectar ao banco de dados: {str(e)}")
            return None

    # Decorador para verificar se o usuário está logado
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor, faça login para acessar esta página', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    # Decorador para verificar se o usuário é admin
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor, faça login para acessar esta página', 'warning')
                return redirect(url_for('login'))
            
            if not session.get('is_admin'):
                flash('Acesso restrito ao administrador principal', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function

    # Decorador para carregar categorias
    def with_categories(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM categorias ORDER BY nome")
                    g.categorias = cursor.fetchall()
            except Exception as e:
                print(f"Erro ao carregar categorias: {str(e)}")
                g.categorias = []
            finally:
                if conn:
                    conn.close()
            return f(*args, **kwargs)
        return decorated_function

    # Função auxiliar para verificar extensões de arquivo permitidas
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Rotas principais
    @app.route('/')
    @with_categories
    def index():
        try:
            conn = get_db_connection()
            with conn:
                with conn.cursor() as cursor:
                    # Pegar as 3 notícias mais recentes
                    cursor.execute("""
                        SELECT n.*, u.nome as autor, c.nome as categoria 
                        FROM noticias n
                        JOIN usuarios u ON n.id_autor = u.id
                        JOIN categorias c ON n.id_categoria = c.id
                        ORDER BY n.data_publicacao DESC
                        LIMIT 3
                    """)
                    noticias = cursor.fetchall()
            
            return render_template('index.html', noticias=noticias, categorias=g.categorias)
        except Exception as e:
            print(f"Erro na página inicial: {str(e)}")
            flash('Erro ao carregar a página inicial', 'danger')
            return render_template('index.html', noticias=[], categorias=[])

    @app.route('/noticia/<int:id>')
    @with_categories
    def noticia(id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Pegar notícia específica
            cursor.execute("""
                SELECT n.*, u.nome as autor, c.nome as categoria
                FROM noticias n
                JOIN usuarios u ON n.id_autor = u.id
                JOIN categorias c ON n.id_categoria = c.id
                WHERE n.id = %s
            """, (id,))
            noticia = cursor.fetchone()
            
            if not noticia:
                flash('Notícia não encontrada', 'danger')
                return redirect(url_for('index'))
            
            # Pegar comentários com nome do autor
            cursor.execute("""
                SELECT c.*, u.nome as autor
                FROM comentarios c
                JOIN usuarios u ON c.id_utilizador = u.id
                WHERE c.id_noticia = %s
                ORDER BY c.data_comentario DESC
            """, (id,))
            comentarios = cursor.fetchall()
            
            # Formatar as datas dos comentários
            for comentario in comentarios:
                if comentario['data_comentario']:
                    try:
                        comentario['data_comentario'] = comentario['data_comentario'].strftime('%d-%m-%Y %H:%M')
                    except Exception as e:
                        print(f"Erro ao formatar data do comentário: {str(e)}")
                        comentario['data_comentario'] = datetime.now().strftime('%d-%m-%Y %H:%M')
            
            # Formatar a data da notícia
            if noticia['data_publicacao']:
                try:
                    noticia['data_publicacao'] = noticia['data_publicacao'].strftime('%d-%m-%Y %H:%M')
                except Exception as e:
                    print(f"Erro ao formatar data da notícia: {str(e)}")
                    noticia['data_publicacao'] = datetime.now().strftime('%d-%m-%Y %H:%M')
            
            return render_template('noticia.html', 
                                 noticia=noticia, 
                                 comentarios=comentarios, 
                                 categorias=g.categorias)
        
        except Exception as e:
            print(f"Erro ao visualizar notícia: {str(e)}")
            flash('Erro ao carregar notícia', 'danger')
            return redirect(url_for('index'))
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Sistema de autenticação
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        print("\n=== Debug Sessão ===")
        print(f"Rota atual: login")
        print(f"Método: {request.method}")
        print(f"Sessão: {session}")
        print("===================\n")

        if request.method == 'POST':
            print("\n=== Debug Login ===")
            print(f"Método: POST")
            print(f"Sessão atual: {session}")
            print(f"Headers: {dict(request.headers)}")
            print(f"Form: {dict(request.form)}")
            
            email = request.form.get('email')
            password = request.form.get('password')
            csrf_token = request.form.get('csrf_token')
            
            print(f"CSRF Token recebido: {csrf_token}")
            print(f"Email: {email}")
            print(f"Password length: {len(password) if password else 0}")
            
            if not email or not password:
                flash('Por favor, preencha todos os campos', 'danger')
                return redirect(url_for('login'))
            
            conn = get_db_connection()
            if not conn:
                flash('Erro de conexão com o banco de dados', 'danger')
                return redirect(url_for('login'))
            
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
                user = cursor.fetchone()
                
                if user and bcrypt.verify(password, user['senha_hash']):
                    session['user_id'] = user['id']
                    session['user_name'] = user['nome']
                    session['is_admin'] = user['is_admin']
                    session.permanent = True
                    
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Email ou senha incorretos', 'danger')
                    return redirect(url_for('login'))
                
            except Exception as e:
                print(f"Erro durante o login: {str(e)}")
                flash('Erro durante o login', 'danger')
                return redirect(url_for('login'))
            
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if conn:
                    conn.close()
        
        print("\n=== Debug Login ===")
        print(f"Método: GET")
        print(f"Sessão atual: {session}")
        
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    @with_categories
    def register():
        if 'user_id' in session:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            password = request.form.get('password')
            
            print("\n=== Debug Registro ===")
            print(f"Nome: {nome}")
            print(f"Email: {email}")
            print(f"Senha length: {len(password)}")
            
            if not all([nome, email, password]):
                flash('Por favor, preencha todos os campos', 'danger')
                return redirect(url_for('register'))
            
            conn = get_db_connection()
            try:
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                        if cursor.fetchone():
                            flash('Email já está em uso', 'danger')
                            return redirect(url_for('register'))
                        
                        # Define como admin apenas se for o email específico
                        is_admin = email.lower().strip() == '2016fontespedro@gmail.com'
                        
                        # Gerar hash da senha usando bcrypt
                        print("Gerando hash da senha...")
                        hashed_password = bcrypt.hash(password)
                        print(f"Hash gerado: {hashed_password}")
                        
                        # Verificar se o hash está funcionando
                        print("Verificando hash...")
                        if bcrypt.verify(password, hashed_password):
                            print("Hash verificado com sucesso!")
                        else:
                            print("ERRO: Hash não verificou!")
                            raise Exception("Erro na verificação do hash da senha")
                        
                        cursor.execute("""
                            INSERT INTO usuarios (nome, email, senha_hash, is_admin)
                            VALUES (%s, %s, %s, %s)
                        """, (nome, email.lower().strip(), hashed_password, is_admin))
                        
                        conn.commit()
                        print("Usuário registrado com sucesso!")
                        print("===================\n")
                        
                        flash('Conta criada com sucesso! Faça login.', 'success')
                        return redirect(url_for('login'))
            except Exception as e:
                print(f"Erro ao criar conta: {str(e)}")
                flash(f'Erro ao criar conta: {str(e)}', 'danger')
                return redirect(url_for('register'))
            finally:
                if conn:
                    conn.close()
        
        return render_template('register.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('user_name', None)
        flash('Você foi desconectado', 'info')
        return redirect(url_for('index'))

    @app.route('/admin')
    @admin_required
    def admin():
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Pegar estatísticas
            cursor.execute("SELECT COUNT(*) as total FROM noticias")
            total_noticias = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cursor.fetchone()['total']
            
            # Pegar todas as notícias para gerenciamento
            cursor.execute("""
                SELECT n.*, u.nome as autor 
                FROM noticias n
                JOIN usuarios u ON n.id_autor = u.id
                ORDER BY n.data_publicacao DESC
            """)
            noticias = cursor.fetchall()
            
            # Pegar categorias
            cursor.execute("SELECT * FROM categorias")
            categorias = cursor.fetchall()
            
            return render_template('admin.html', 
                                 total_noticias=total_noticias,
                                 total_usuarios=total_usuarios,
                                 noticias=noticias,
                                 categorias=categorias)
        
        except Exception as e:
            print(f"Erro ao acessar painel admin: {str(e)}")
            flash('Erro ao carregar painel de administração', 'danger')
            return redirect(url_for('index'))
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @app.route('/admin/noticia/novo', methods=['GET', 'POST'])
    @admin_required
    def admin_nova_noticia():
        conn = None
        if request.method == 'POST':
            try:
                titulo = request.form.get('titulo', '').strip()
                conteudo = request.form.get('conteudo', '').strip()
                id_categoria = request.form.get('categoria')
                imagem = request.files.get('imagem')
                
                # Validações
                if not titulo or not conteudo or not id_categoria:
                    flash('Por favor, preencha todos os campos obrigatórios', 'danger')
                    return redirect(url_for('admin_nova_noticia'))
                
                # Processar upload da imagem
                filename = None
                if imagem and allowed_file(imagem.filename):
                    filename = secure_filename(imagem.filename)
                    imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO noticias (titulo, conteudo, imagem, id_autor, id_categoria)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (titulo, conteudo, filename, session['user_id'], id_categoria))
                    conn.commit()
                
                flash('Notícia publicada com sucesso!', 'success')
                return redirect(url_for('admin'))
            
            except Exception as e:
                flash(f'Erro ao publicar notícia: {str(e)}', 'danger')
                return redirect(url_for('admin_nova_noticia'))
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
        
        try:
            # Buscar categorias para o formulário
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM categorias ORDER BY nome")
                categorias = cursor.fetchall()
            return render_template('nova_noticia.html', categorias=categorias)
        
        except Exception as e:
            flash(f'Erro ao carregar formulário: {str(e)}', 'danger')
            return redirect(url_for('admin'))
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    @app.route('/admin/noticia/editar/<int:id>', methods=['GET', 'POST'])
    @admin_required
    def admin_editar_noticia(id):
        conn = get_db_connection()
        
        if request.method == 'POST':
            titulo = request.form['titulo']
            conteudo = request.form['conteudo']
            id_categoria = request.form['categoria']
            imagem = request.files.get('imagem')
            
            try:
                with conn:
                    with conn.cursor() as cursor:
                        if imagem and allowed_file(imagem.filename):
                            filename = secure_filename(imagem.filename)
                            imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                            cursor.execute("""
                                UPDATE noticias 
                                SET titulo = %s, conteudo = %s, imagem = %s, id_categoria = %s 
                                WHERE id = %s
                            """, (titulo, conteudo, filename, id_categoria, id))
                        else:
                            cursor.execute("""
                                UPDATE noticias 
                                SET titulo = %s, conteudo = %s, id_categoria = %s 
                                WHERE id = %s
                            """, (titulo, conteudo, id_categoria, id))
                        
                        conn.commit()
                        flash('Notícia atualizada com sucesso!', 'success')
                        return redirect(url_for('admin'))
            except Exception as e:
                flash(f'Erro ao atualizar notícia: {str(e)}', 'danger')
        
        # Buscar dados da notícia e categorias
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT n.*, c.id as categoria_id 
                    FROM noticias n
                    JOIN categorias c ON n.id_categoria = c.id
                    WHERE n.id = %s
                """, (id,))
                noticia = cursor.fetchone()
                
                if not noticia:
                    flash('Notícia não encontrada', 'danger')
                    return redirect(url_for('admin'))
                
                cursor.execute("SELECT * FROM categorias")
                categorias = cursor.fetchall()
        
        return render_template('editar_noticia.html', noticia=noticia, categorias=categorias)

    @app.route('/admin/noticia/excluir/<int:id>', methods=['POST'])
    @admin_required
    def admin_excluir_noticia(id):
        conn = get_db_connection()
        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM noticias WHERE id = %s", (id,))
                    conn.commit()
                    flash('Notícia excluída com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao excluir notícia: {str(e)}', 'danger')
        
        return redirect(url_for('admin'))

    @app.route('/contact', methods=['GET', 'POST'])
    @with_categories
    def contact():
        print("\n=== Debug Sessão ===")
        print(f"Rota atual: contact")
        print(f"Método: {request.method}")
        print(f"Sessão: {session}")
        print("===================\n")

        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            assunto = request.form.get('assunto')
            mensagem = request.form.get('mensagem')
            
            # Validar os campos
            if not all([nome, email, assunto, mensagem]):
                flash('Por favor, preencha todos os campos', 'danger')
                return redirect(url_for('contact'))
            
            conn = get_db_connection()
            if not conn:
                flash('Erro ao processar sua mensagem. Por favor, tente novamente.', 'danger')
                return redirect(url_for('contact'))
            
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mensagens_contato (nome, email, assunto, mensagem)
                    VALUES (%s, %s, %s, %s)
                """, (nome, email, assunto, mensagem))
                conn.commit()
                
                flash('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
                return redirect(url_for('contact'))
                
            except Exception as e:
                print(f"Erro ao enviar mensagem: {str(e)}")
                flash('Erro ao enviar mensagem. Por favor, tente novamente.', 'danger')
                return redirect(url_for('contact'))
                
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if conn:
                    conn.close()
        
        return render_template('contact.html', categorias=g.categorias)

    @app.route('/admin/mensagens')
    @admin_required
    def admin_mensagens():
        conn = get_db_connection()
        if not conn:
            flash('Erro ao carregar mensagens', 'danger')
            return redirect(url_for('admin'))
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *, DATE_FORMAT(data_envio, '%d/%m/%Y %H:%i') as data_formatada 
                FROM mensagens_contato 
                ORDER BY data_envio DESC
            """)
            mensagens = cursor.fetchall()
            
            return render_template('admin/mensagens.html', mensagens=mensagens)
            
        except Exception as e:
            print(f"Erro ao carregar mensagens: {str(e)}")
            flash('Erro ao carregar mensagens', 'danger')
            return redirect(url_for('admin'))
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()

    @app.route('/admin/mensagem/<int:id>/marcar-lida', methods=['POST'])
    @admin_required
    def marcar_mensagem_lida(id):
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erro de conexão'}), 500
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE mensagens_contato 
                SET lida = NOT lida 
                WHERE id = %s
            """, (id,))
            conn.commit()
            
            # Buscar o novo estado
            cursor.execute("SELECT lida FROM mensagens_contato WHERE id = %s", (id,))
            result = cursor.fetchone()
            
            return jsonify({
                'success': True, 
                'lida': result['lida']
            })
            
        except Exception as e:
            print(f"Erro ao marcar mensagem: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()

    @app.route('/admin/mensagem/<int:id>/excluir', methods=['POST'])
    @admin_required
    def excluir_mensagem(id):
        conn = get_db_connection()
        if not conn:
            flash('Erro ao excluir mensagem', 'danger')
            return redirect(url_for('admin_mensagens'))
        
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM mensagens_contato WHERE id = %s", (id,))
            conn.commit()
            
            flash('Mensagem excluída com sucesso', 'success')
            return redirect(url_for('admin_mensagens'))
            
        except Exception as e:
            print(f"Erro ao excluir mensagem: {str(e)}")
            flash('Erro ao excluir mensagem', 'danger')
            return redirect(url_for('admin_mensagens'))
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()

    @app.route('/opcoes', methods=['GET', 'POST'])
    def opcoes():
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar as configurações', 'warning')
            return redirect(url_for('login'))
        
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Obter dados do utilizador
                cursor.execute("SELECT * FROM usuarios WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                
                if request.method == 'POST':
                    try:
                        # Verificar token CSRF
                        csrf.protect()
                        
                        # Obter dados do formulário
                        novo_nome = request.form.get('nome')
                        novo_email = request.form.get('email')
                        senha_atual = request.form.get('senha_atual')
                        nova_senha = request.form.get('nova_senha')
                        confirmar_senha = request.form.get('confirmar_senha')
                        
                        # Validar dados
                        if not novo_nome or not novo_email:
                            flash('Nome e email são obrigatórios', 'danger')
                            return render_template('opcoes.html', user=user)
                        
                        # Verificar se o email já está em uso
                        if novo_email != user['email']:
                            cursor.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s", 
                                         (novo_email, session['user_id']))
                            if cursor.fetchone():
                                flash('Este email já está em uso por outra conta', 'danger')
                                return render_template('opcoes.html', user=user)
                        
                        # Atualizar nome e email
                        cursor.execute("""
                            UPDATE usuarios 
                            SET nome = %s, email = %s 
                            WHERE id = %s
                        """, (novo_nome, novo_email, session['user_id']))
                        
                        # Atualizar senha se fornecida
                        if senha_atual and nova_senha:
                            try:
                                # Verificar senha atual
                                if not bcrypt.verify(senha_atual, user['senha_hash']):
                                    flash('Senha atual incorreta', 'danger')
                                    return render_template('opcoes.html', user=user)
                                    
                                if nova_senha != confirmar_senha:
                                    flash('As senhas não coincidem', 'danger')
                                    return render_template('opcoes.html', user=user)
                                    
                                if len(nova_senha) < 6:
                                    flash('A nova senha deve ter pelo menos 6 caracteres', 'danger')
                                    return render_template('opcoes.html', user=user)
                                    
                                # Gerar novo hash
                                senha_hash = bcrypt.hash(nova_senha)
                                
                                cursor.execute("""
                                    UPDATE usuarios 
                                    SET senha_hash = %s 
                                    WHERE id = %s
                                """, (senha_hash, session['user_id']))
                            except Exception as e:
                                print(f"Erro ao processar senha: {str(e)}")
                                logging.error(f"Erro ao processar senha: {str(e)}")
                                flash('Erro ao processar a senha', 'danger')
                                return render_template('opcoes.html', user=user)
                        
                        conn.commit()
                        session['user_name'] = novo_nome
                        session['email'] = novo_email
                        flash('Usuário atualizado com sucesso!', 'success')
                        return redirect(url_for('opcoes'))
                        
                    except CSRFError:
                        flash('Erro de segurança. Por favor, tente novamente.', 'danger')
                        return redirect(url_for('opcoes'))
                
                return render_template('opcoes.html', user=user)
                
        except Exception as e:
            print(f"Erro ao atualizar dados: {str(e)}")
            logging.error(f"Erro ao atualizar dados: {str(e)}")
            flash('Erro ao atualizar dados', 'danger')
            return redirect(url_for('opcoes'))
        
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    @app.route('/routes')
    def list_routes():
        import urllib.parse
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            line = urllib.parse.unquote(f"{rule.endpoint:50s} {methods:20s} {rule}")
            output.append(line)
        return '<br>'.join(sorted(output))

    # API para comentários
    @app.route('/comentar', methods=['POST'])
    def comentar():
        if 'user_id' not in session:
            flash('Por favor, faça login para comentar', 'warning')
            return redirect(url_for('login'))
        
        try:
            noticia_id = request.form.get('noticia_id')
            comentario = request.form.get('comentario')
            
            if not noticia_id or not comentario:
                flash('Por favor, preencha o comentário', 'warning')
                return redirect(request.referrer or url_for('index'))
            
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    # Verificar se a notícia existe
                    cursor.execute("SELECT id FROM noticias WHERE id = %s", (noticia_id,))
                    if not cursor.fetchone():
                        flash('Notícia não encontrada', 'danger')
                        return redirect(url_for('index'))
                    
                    # Inserir o comentário
                    cursor.execute("""
                        INSERT INTO comentarios (id_utilizador, id_noticia, conteudo)
                        VALUES (%s, %s, %s)
                    """, (session['user_id'], noticia_id, comentario))
                    conn.commit()
                    
                    flash('Comentário adicionado com sucesso!', 'success')
                    return redirect(url_for('noticia', id=noticia_id))
            
            except Exception as e:
                if conn:
                    conn.rollback()
                print(f"Erro ao adicionar comentário: {str(e)}")
                flash('Erro ao adicionar comentário', 'danger')
                return redirect(request.referrer or url_for('index'))
            finally:
                if conn:
                    conn.close()
        
        except Exception as e:
            print(f"Erro ao processar comentário: {str(e)}")
            flash('Erro ao processar comentário', 'danger')
            return redirect(request.referrer or url_for('index'))

    @app.route('/comentario/<int:comment_id>/excluir', methods=['POST'])
    def excluir_comentario(comment_id):
        if 'user_id' not in session:
            flash('Por favor, faça login para excluir comentários', 'warning')
            return redirect(url_for('login'))
        
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # Verificar se o comentário existe e pertence ao usuário
                cursor.execute("""
                    SELECT c.*, n.id as noticia_id 
                    FROM comentarios c
                    JOIN noticias n ON c.id_noticia = n.id
                    WHERE c.id = %s
                """, (comment_id,))
                
                comentario = cursor.fetchone()
                
                if not comentario:
                    flash('Comentário não encontrado', 'danger')
                    return redirect(url_for('index'))
                
                # Verificar se o usuário tem permissão para excluir
                if comentario['id_utilizador'] != session['user_id'] and not session.get('is_admin'):
                    flash('Você não tem permissão para excluir este comentário', 'danger')
                    return redirect(url_for('noticia', id=comentario['noticia_id']))
                
                # Excluir o comentário
                cursor.execute("DELETE FROM comentarios WHERE id = %s", (comment_id,))
                conn.commit()
                
                flash('Comentário excluído com sucesso', 'success')
                return redirect(url_for('noticia', id=comentario['noticia_id']))
        
        except Exception as e:
            print(f"Erro ao excluir comentário: {str(e)}")
            flash('Erro ao excluir comentário', 'danger')
            return redirect(url_for('index'))
        
        finally:
            if conn:
                conn.close()

    @app.route('/sobre')
    @with_categories
    def sobre():
        return render_template('sobre.html', categorias=g.categorias)

    @app.route('/admin/categorias', methods=['GET', 'POST'])
    @admin_required
    @with_categories
    def gerenciar_categorias():
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if request.method == 'POST':
                acao = request.form.get('acao')
                print(f"Ação solicitada: {acao}")
                
                if acao == 'adicionar':
                    nome = request.form.get('nome')
                    descricao = request.form.get('descricao', '')
                    
                    print(f"Tentando adicionar categoria: {nome}")
                    print(f"Descrição: {descricao}")
                    
                    if not nome:
                        flash('Nome da categoria é obrigatório', 'danger')
                        return redirect(url_for('gerenciar_categorias'))
                    
                    # Verificar se já existe
                    cursor.execute("SELECT id FROM categorias WHERE nome = %s", (nome,))
                    categoria_existente = cursor.fetchone()
                    
                    if categoria_existente:
                        flash('Esta categoria já existe', 'danger')
                        return redirect(url_for('gerenciar_categorias'))
                    else:
                        # Inserir nova categoria
                        cursor.execute("""
                            INSERT INTO categorias (nome, descricao) 
                            VALUES (%s, %s)
                        """, (nome, descricao))
                        conn.commit()
                        flash('Categoria adicionada com sucesso!', 'success')
                        print(f"Categoria '{nome}' adicionada com sucesso!")
                
                elif acao == 'editar':
                    id_categoria = request.form.get('id')
                    novo_nome = request.form.get('nome')
                    nova_descricao = request.form.get('descricao', '')
                    
                    print(f"Tentando editar categoria ID {id_categoria}")
                    print(f"Novo nome: {novo_nome}")
                    print(f"Nova descrição: {nova_descricao}")
                    
                    if id_categoria and novo_nome:
                        # Verificar se o novo nome já existe em outra categoria
                        cursor.execute("SELECT id FROM categorias WHERE nome = %s AND id != %s", (novo_nome, id_categoria))
                        categoria_existente = cursor.fetchone()
                        
                        if categoria_existente:
                            flash('Já existe uma categoria com este nome', 'danger')
                            return redirect(url_for('gerenciar_categorias'))
                        
                        cursor.execute("""
                            UPDATE categorias 
                            SET nome = %s, descricao = %s 
                            WHERE id = %s
                        """, (novo_nome, nova_descricao, id_categoria))
                        conn.commit()
                        flash('Categoria atualizada com sucesso!', 'success')
                
                elif acao == 'excluir':
                    id_categoria = request.form.get('id')
                    print(f"Tentando excluir categoria ID {id_categoria}")
                    
                    if id_categoria:
                        cursor.execute("SELECT COUNT(*) as total FROM noticias WHERE id_categoria = %s", (id_categoria,))
                        total_noticias = cursor.fetchone()['total']
                        
                        if total_noticias > 0:
                            flash('Não é possível excluir esta categoria pois existem notícias vinculadas a ela', 'danger')
                        else:
                            cursor.execute("DELETE FROM categorias WHERE id = %s", (id_categoria,))
                            conn.commit()
                            flash('Categoria excluída com sucesso!', 'success')
                
                return redirect(url_for('gerenciar_categorias'))
            
            # Buscar todas as categorias
            cursor.execute("""
                SELECT c.*, COUNT(n.id) as total_noticias 
                FROM categorias c 
                LEFT JOIN noticias n ON c.id = n.id_categoria 
                GROUP BY c.id
                ORDER BY c.nome
            """)
            categorias = cursor.fetchall()
            
            return render_template('admin/categorias.html', categorias=categorias)

        except Exception as e:
            print(f"Erro geral no gerenciamento de categorias: {str(e)}")
            if conn:
                conn.rollback()
            flash('Erro ao gerenciar categorias. Por favor, tente novamente.', 'danger')
            return redirect(url_for('gerenciar_categorias'))
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @app.route('/categoria/<int:id>')
    @with_categories
    def ver_categoria(id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Buscar informações da categoria
            cursor.execute("SELECT * FROM categorias WHERE id = %s", (id,))
            categoria = cursor.fetchone()
            
            if not categoria:
                flash('Categoria não encontrada', 'danger')
                return redirect(url_for('index'))
            
            # Buscar notícias da categoria
            cursor.execute("""
                SELECT n.*, u.nome as autor 
                FROM noticias n
                JOIN usuarios u ON n.id_autor = u.id
                WHERE n.id_categoria = %s
                ORDER BY n.data_publicacao DESC
            """, (id,))
            noticias = cursor.fetchall()
            
            return render_template('categoria.html', 
                                 categoria=categoria, 
                                 noticias=noticias, 
                                 categorias=g.categorias)
        
        except Exception as e:
            print(f"Erro ao visualizar categoria: {str(e)}")
            flash('Erro ao carregar categoria', 'danger')
            return redirect(url_for('index'))
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Rotas de gerenciamento de utilizadores
    @app.route('/admin/usuarios')
    @admin_required
    def listar_usuarios():
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, nome, email, is_admin,
                           COALESCE(DATE_FORMAT(data_criacao, '%d/%m/%Y %H:%i'), '-') as data_criacao_formatada
                    FROM usuarios 
                    ORDER BY nome
                """)
                usuarios = cursor.fetchall()
            
            return render_template('admin/usuarios.html', usuarios=usuarios)
        
        except Exception as e:
            print(f"Erro ao listar utilizadores: {str(e)}")
            logging.error(f"Erro ao listar utilizadores: {str(e)}")
            flash('Erro ao carregar lista de utilizadores', 'danger')
            return redirect(url_for('admin'))
        
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    @app.route('/admin/usuario/<int:id>', methods=['GET', 'POST'])
    @admin_required
    def editar_usuario(id):
        conn = None
        try:
            conn = get_db_connection()
            
            # Não permitir editar o próprio admin principal
            if id == session['user_id'] and session['email'] == '2016fontespedro@gmail.com':
                flash('Não é possível editar a conta de administrador principal', 'danger')
                return redirect(url_for('listar_usuarios'))
            
            if request.method == 'POST':
                nome = request.form.get('nome')
                email = request.form.get('email')
                is_admin = request.form.get('is_admin') == 'on'
                
                with conn.cursor() as cursor:
                    # Verificar se o email já existe (exceto para o próprio usuário)
                    cursor.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s", (email, id))
                    if cursor.fetchone():
                        flash('Este email já está em uso por outro usuário', 'danger')
                        return redirect(url_for('editar_usuario', id=id))
                    
                    cursor.execute("""
                        UPDATE usuarios 
                        SET nome = %s, email = %s, is_admin = %s
                        WHERE id = %s
                    """, (nome, email, is_admin, id))
                    conn.commit()
                    flash('Usuário atualizado com sucesso!', 'success')
                    return redirect(url_for('listar_usuarios'))
            
            # Buscar dados do utilizador para o formulário
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
                usuario = cursor.fetchone()
                if not usuario:
                    flash('Usuário não encontrado', 'danger')
                    return redirect(url_for('listar_usuarios'))
            
            return render_template('admin/editar_usuario.html', usuario=usuario)
        
        except Exception as e:
            print(f"Erro ao editar usuário: {str(e)}")
            logging.error(f"Erro ao editar usuário: {str(e)}")
            flash('Erro ao editar usuário', 'danger')
            return redirect(url_for('listar_usuarios'))
        
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    @app.route('/admin/usuario/<int:id>/excluir', methods=['POST'])
    @admin_required
    def excluir_usuario(id):
        # Não permitir excluir o próprio admin principal
        if id == session['user_id']:
            flash('Não é possível excluir a própria conta de administrador principal', 'danger')
            return redirect(url_for('listar_usuarios'))
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Verificar se está tentando excluir o admin principal
                cursor.execute("SELECT email FROM usuarios WHERE id = %s", (id,))
                usuario = cursor.fetchone()
                if usuario and usuario['email'] == '2016fontespedro@gmail.com':
                    flash('Não é possível excluir a conta de administrador principal', 'danger')
                    return redirect(url_for('listar_usuarios'))
                    
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
                conn.commit()
                flash('Usuário excluído com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao excluir usuário: {str(e)}', 'danger')
        return redirect(url_for('listar_usuarios'))

    # Rota temporária para debug do banco de dados
    @app.route('/debug_db')
    def debug_db():
        try:
            output = []
            output.append("=== Verificação do Banco de Dados ===")
            
            conn = get_db_connection()
            if not conn:
                return "Erro ao conectar ao banco de dados", 500
            
            with conn.cursor() as cursor:
                # Verificar estrutura da tabela
                output.append("\n1. Estrutura da tabela usuarios:")
                cursor.execute("DESCRIBE usuarios")
                for row in cursor.fetchall():
                    output.append(str(row))
                
                # Verificar primeiro usuário
                output.append("\n2. Dados do primeiro usuário:")
                cursor.execute("SELECT * FROM usuarios LIMIT 1")
                user = cursor.fetchone()
                if user:
                    for key, value in user.items():
                        output.append(f"{key}: {type(value)} = {value}")
                else:
                    output.append("Nenhum usuário encontrado")
                
                # Verificar campos vazios
                output.append("\n3. Verificando campos vazios:")
                cursor.execute("SELECT * FROM usuarios WHERE email IS NULL OR senha_hash IS NULL OR nome IS NULL")
                empty_fields = cursor.fetchall()
                if empty_fields:
                    output.append("Utilizadores com campos vazios encontrados:")
                    for user in empty_fields:
                        output.append(str(user))
                else:
                    output.append("Nenhum utilizador com campos vazios encontrado")
                
            return "<br>".join(output)
        except Exception as e:
            return f"ERRO: {str(e)}", 500

    # Verificar estado da sessão antes de cada requisição
    @app.before_request
    def before_request():
        try:
            print("\n=== Debug Sessão ===")
            print(f"Rota atual: {request.endpoint}")
            print(f"Método: {request.method}")
            print(f"Sessão: {dict(session)}")
            print("===================\n")
        except Exception as e:
            print(f"Erro ao verificar sessão: {str(e)}")
            logging.error(f"Erro ao verificar sessão: {str(e)}")

    # Handler para erros 500
    @app.errorhandler(500)
    def internal_error(error):
        print(f"Erro 500: {str(error)}")
        logging.error(f"Erro 500: {str(error)}")
        return render_template('error.html', error=error), 500

    # Rota de debug para verificar hash da senha
    @app.route('/debug_hash/<email>')
    def debug_hash(email):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT senha_hash FROM usuarios WHERE email = %s", (email,))
                user = cursor.fetchone()
                if user:
                    return f"Hash armazenado: {user['senha_hash']}"
                return "Usuário não encontrado"
        except Exception as e:
            return f"Erro: {str(e)}"
        finally:
            if conn:
                conn.close()

    # Configuração do email
    def enviar_email(destinatario, assunto, corpo):
        # Configurações do servidor de email
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SMTP_USERNAME = "seu_email@gmail.com"  # Substitua pelo seu email
        SMTP_PASSWORD = "sua_senha_app"        # Substitua pela sua senha de app

        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'html'))

        try:
            # Conectar e enviar email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False

    @app.route('/esqueci-senha', methods=['GET', 'POST'])
    def esqueci_senha():
        if request.method == 'POST':
            email = request.form.get('email')
            
            if not email:
                flash('Por favor, insira seu email', 'danger')
                return redirect(url_for('esqueci_senha'))
            
            conn = get_db_connection()
            try:
                with conn:
                    with conn.cursor() as cursor:
                        # Verificar se o email existe
                        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                        user = cursor.fetchone()
                        
                        if not user:
                            flash('Email não encontrado', 'danger')
                            return redirect(url_for('esqueci_senha'))
                        
                        # Gerar token único
                        token = secrets.token_urlsafe(32)
                        expiracao = datetime.now() + timedelta(hours=1)
                        
                        # Salvar token no banco
                        cursor.execute("""
                            INSERT INTO recuperacao_senha (id_utilizador, token, expiracao)
                            VALUES (%s, %s, %s)
                        """, (user['id'], token, expiracao))
                        conn.commit()
                        
                        # Enviar email
                        link_recuperacao = url_for('redefinir_senha', token=token, _external=True)
                        corpo_email = f"""
                        <h2>Recuperação de Senha - Entertainment News</h2>
                        <p>Você solicitou a recuperação de senha. Clique no link abaixo para redefinir sua senha:</p>
                        <p><a href="{link_recuperacao}">Redefinir Senha</a></p>
                        <p>Este link é válido por 1 hora.</p>
                        <p>Se você não solicitou esta recuperação, ignore este email.</p>
                        """
                        
                        if enviar_email(email, "Recuperação de Senha - Entertainment News", corpo_email):
                            flash('Enviamos um email com instruções para recuperar sua senha', 'success')
                        else:
                            flash('Erro ao enviar email. Por favor, tente novamente mais tarde', 'danger')
                        
                        return redirect(url_for('login'))
                        
            except Exception as e:
                flash('Erro ao processar solicitação. Por favor, tente novamente', 'danger')
                return redirect(url_for('esqueci_senha'))
            
            finally:
                if conn:
                    conn.close()
        
        return render_template('esqueci_senha.html')

    @app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
    def redefinir_senha(token):
        if request.method == 'POST':
            nova_senha = request.form.get('password')
            confirmar_senha = request.form.get('confirm_password')
            
            if not nova_senha or not confirmar_senha:
                flash('Por favor, preencha todos os campos', 'danger')
                return redirect(url_for('redefinir_senha', token=token))
            
            if nova_senha != confirmar_senha:
                flash('As senhas não coincidem', 'danger')
                return redirect(url_for('redefinir_senha', token=token))
            
            if len(nova_senha) < 6:
                flash('A senha deve ter pelo menos 6 caracteres', 'danger')
                return redirect(url_for('redefinir_senha', token=token))
            
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Verificar token
                cursor.execute("""
                    SELECT id_utilizador
                    FROM recuperacao_senha
                    WHERE token = %s AND expiracao > NOW() AND usado = 0
                """, (token,))
                recuperacao = cursor.fetchone()

                if not recuperacao:
                    flash('Link de recuperação inválido ou expirado', 'danger')
                    return redirect(url_for('login'))

                # Atualizar senha
                senha_hash = bcrypt.hash(nova_senha)
                cursor.execute("""
                    UPDATE usuarios
                    SET senha_hash = %s
                    WHERE id = %s
                """, (senha_hash, recuperacao['id_utilizador']))

                # Marcar token como usado
                cursor.execute("""
                    UPDATE recuperacao_senha
                    SET usado = 1
                    WHERE token = %s
                """, (token,))

                conn.commit()
                flash('Senha atualizada com sucesso! Faça login com sua nova senha', 'success')
                return redirect(url_for('login'))

            except Exception as e:
                if conn:
                    conn.rollback()
                print(f"Erro ao redefinir senha: {str(e)}")
                flash('Erro ao redefinir senha. Por favor, tente novamente', 'danger')
                return redirect(url_for('redefinir_senha', token=token))
            
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        return render_template('redefinir_senha.html', token=token)

    if __name__ == '__main__':
        logging.info("Iniciando servidor Flask...")
        app.run(debug=True)

except Exception as e:
    logging.error(f"ERRO CRÍTICO: {str(e)}")
    logging.error(f"Tipo do erro: {type(e)}")
    import traceback
    logging.error("Stack trace:", exc_info=True)