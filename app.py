from flask import Flask, flash, render_template, request, redirect, url_for, session
import random
import string
import sqlite3
import qrcode
from flask import send_file
import os
from flask import send_from_directory
from flask_talisman import Talisman  # Para adicionar cabeçalhos de segurança
import zipfile
import shutil


app = Flask(__name__, static_url_path='/static', static_folder='static')


# Configuração para sessão
app.secret_key = '02faf3e2914'  # Use uma chave secreta real e segura para produção

# Configurar o Talisman para adicionar cabeçalhos de segurança
Talisman(app, content_security_policy={
    'default-src': '\'self\'',
    'img-src': '\'self\' data:',
    'script-src': '\'self\' https://cdn.jsdelivr.net',
    'style-src': '\'self\' https://cdn.jsdelivr.net',
})

Talisman(app, frame_options="DENY")


# Função para gerar o ID aleatório
def gerar_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    conn = sqlite3.connect('registros.db')  # Conectando ao banco de dados
    conn.row_factory = sqlite3.Row  # Para retornar resultados como dicionários
    return conn

# Criar a tabela de registros, se ela não existir
def criar_tabela():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id TEXT PRIMARY KEY,
            responsavel TEXT NOT NULL,
            convidados TEXT NOT NULL,
            situacao TEXT NOT NULL,
            anotacoes TEXT
        );
    ''')
    conn.commit()
    conn.close()

# Função para gerar e salvar o QR Code
def gerar_qr_code(id_usuario):
    # Define o caminho completo para a pasta qrcodes dentro de static
    qr_code_dir = os.path.join('static', 'qrcodes')
    
    # Cria a pasta qrcodes se não existir
    if not os.path.exists(qr_code_dir):
        os.makedirs(qr_code_dir)
    
    # Gerar a URL completa com o ID
    url_qrcode = f"adtab-jantar.onrender.com/view/{id_usuario}"
    
    # Gerar o QR Code a partir da URL
    qr = qrcode.make(url_qrcode)
    
    # Define o caminho completo para o arquivo de imagem do QR Code
    qr_path = os.path.join(qr_code_dir, f'{id_usuario}.png')
    
    # Salvar o QR Code na pasta qrcodes
    qr.save(qr_path)

@app.route('/notforme')
def notforme():
    return render_template('notforme.html')

# Função para compactar arquivos em um ZIP
def zip_backup():
    zip_path = os.path.join('static', 'backup.zip')
    
    # Cria o arquivo ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adiciona a pasta qrcodes e seu conteúdo
        qrcodes_dir = os.path.join('static', 'qrcodes')
        if os.path.exists(qrcodes_dir):
            # Adiciona a pasta qrcodes ao zip, incluindo a estrutura de diretórios
            for root, dirs, files in os.walk(qrcodes_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=qrcodes_dir)  # Mantém a estrutura de pastas
                    zipf.write(file_path, arcname=os.path.join('qrcodes', arcname))  # Adiciona no zip com o caminho correto

        # Adiciona a pasta users e seu conteúdo
        users_dir = os.path.join('static', 'users')
        if os.path.exists(users_dir):
            # Adiciona a pasta users ao zip, incluindo a estrutura de diretórios
            for root, dirs, files in os.walk(users_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=users_dir)  # Mantém a estrutura de pastas
                    zipf.write(file_path, arcname=os.path.join('users', arcname))  # Adiciona no zip com o caminho correto
        
        # Adiciona o arquivo .db
        db_file = 'registros.db'
        if os.path.exists(db_file):
            zipf.write(db_file, os.path.basename(db_file))

    return zip_path


# Rota para a página de backup
@app.route('/backup', methods=['GET', 'POST'])
def backup():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Gera o backup.zip com todos os arquivos
        zip_path = zip_backup()
        
        # Retorna o arquivo compactado como download
        return send_file(zip_path, as_attachment=True)

    return render_template('backup.html')

# Página principal
@app.route('/')
def index():
    # Verificar se o usuário está autenticado
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Ordenar os registros pelo nome do responsável de forma alfabética
    registros = conn.execute('SELECT * FROM registros ORDER BY responsavel ASC').fetchall()
    conn.close()

    # Organize os dados como um dicionário para o template
    return render_template('index.html', registros=registros)


def atualizar_tabela():
    conn = get_db_connection()
    # Adiciona a coluna "anotacoes" caso ela ainda não exista
    try:
        conn.execute('ALTER TABLE registros ADD COLUMN anotacoes TEXT DEFAULT ""')
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            print(f"Erro ao atualizar tabela: {e}")
    finally:
        conn.close()


@app.route('/static/users/<id>')
def user_image(id):
    # Caminho onde as imagens estão armazenadas
    image_dir = 'static/users'
    
    # Extensões possíveis das imagens
    extensions = ['.jpg', '.jpeg', '.png']
    
    # Verifica qual arquivo existe
    for ext in extensions:
        image_path = os.path.join(image_dir, f"{id}{ext}")
        if os.path.exists(image_path):
            return send_from_directory(image_dir, f"{id}{ext}")
    
    # Caso nenhuma imagem seja encontrada, retorna uma imagem padrão
    return send_from_directory(image_dir, 'default.jpg')


# Caminho absoluto para a pasta onde as imagens serão armazenadas
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'users')

# Defina as extensões permitidas para o upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Função para verificar se o arquivo tem uma extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    # Verificar se o usuário está autenticado
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Gerar ID e registrar dados
        id_gerado = gerar_id()
        responsavel = request.form['responsavel']
        convidados = request.form['convidados']
        anotacoes = request.form.get('anotacoes', '').strip()  # Recuperar o campo de anotações, padrão vazio se não preenchido
        situacao = 'Em espera'

        # Processar o upload de imagem (se houver)
        imagem_filename = None
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem and allowed_file(imagem.filename):
                # Crie a pasta 'static/users' caso não exista
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                    print("Pasta 'users' criada com sucesso.")
                else:
                    print("A pasta 'users' já existe.")


                # Defina a extensão do arquivo (usando a extensão original)
                extensao = imagem.filename.rsplit('.', 1)[1].lower()

                # Defina o nome do arquivo com base no ID gerado
                imagem_filename = f"{id_gerado}.{extensao}"
                imagem_path = os.path.join(UPLOAD_FOLDER, imagem_filename)

                # Salvar a imagem
                imagem.save(imagem_path)
                print(f"Imagem salva como {imagem_filename}")  # Verifique se a imagem foi salva corretamente

        # Inserir os dados no banco de dados, sem incluir o nome da imagem
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO registros (id, responsavel, convidados, anotacoes, situacao) VALUES (?, ?, ?, ?, ?)',
                         (id_gerado, responsavel, convidados, anotacoes, situacao))
            conn.commit()

            # Gerar o QR Code para o novo ID e salvar na pasta qrcodes
            gerar_qr_code(id_gerado)
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Erro ao inserir dados: {e}")
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('registrar.html')



@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', mensagem="Página não encontrada."), 404

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        
        if usuario == "adjantar@01" and senha == "adjantar@01":  # Altere as credenciais conforme necessário
            session['logged_in'] = True  # Marca a sessão como logada
            next_page = request.args.get('next')  # Redireciona para a página original após login
            return redirect(next_page or url_for('index'))
        else:
            return 'Usuário ou senha incorretos', 403
    return render_template('login.html')

# Rota para excluir um registro
@app.route('/excluir/<id>', methods=['POST'])
def excluir(id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM registros WHERE id = ?', (id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao excluir registro: {e}")
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/view/<id>', methods=['GET', 'POST'])
def view(id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('notforme'))  # Redireciona para a página notforme.html

    conn = get_db_connection()
    registro = conn.execute('SELECT * FROM registros WHERE id = ?', (id,)).fetchone()
    conn.close()

    if registro is None:
        return render_template('error.html', mensagem="ID não encontrado.", id=id), 404

    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == "saveall":
            situacao = request.form.get('situacao')  # Usando get para evitar KeyError
            anotacoes = request.form.get('anotacoes', '').strip()

            if not situacao:
                flash('A situação não pode estar vazia!', 'danger')
                return redirect(url_for('view', id=id))

            try:
                conn = get_db_connection()
                conn.execute(
                    'UPDATE registros SET situacao = ?, anotacoes = ? WHERE id = ?',
                    (situacao, anotacoes, id)
                )
                conn.commit()
                flash('Dados atualizados com sucesso!', 'success')
            except sqlite3.Error as e:
                print(f"Erro ao atualizar registro: {e}")
                flash('Erro ao atualizar os dados, tente novamente mais tarde.', 'danger')
            finally:
                conn.close()

            return redirect(url_for('index'))
        else:
            flash('Senha incorreta', 'danger')
            return redirect(url_for('view', id=id))

    return render_template('view.html', id=id, dados=registro)


# Rota para logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove a chave de sessão, deslogando o usuário
    return redirect(url_for('login'))

@app.before_request
def force_https():
    if not request.is_secure and not app.debug and 'DYNO' in os.environ:  # Verifica se está em produção (exemplo: Heroku)
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


if __name__ == '__main__':
    criar_tabela()  # Certifica-se de que a tabela existe antes de iniciar o app
    atualizar_tabela()
    app.run(host='0.0.0.0', port=5000, debug=True)  # Sem o debug=True
