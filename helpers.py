import sqlite3
import os
import zipfile
import qrcode

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'users')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('registros.db')
    conn.row_factory = sqlite3.Row
    return conn

def gerar_qr_code(id_usuario):
    qr_code_dir = os.path.join('static', 'qrcodes')
    if not os.path.exists(qr_code_dir):
        os.makedirs(qr_code_dir)
    url_qrcode = f"adtab-jantar.onrender.com/view/{id_usuario}"
    qr = qrcode.make(url_qrcode)
    qr_path = os.path.join(qr_code_dir, f'{id_usuario}.png')
    qr.save(qr_path)

#criar a tabela de registros, se ela não existir
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

def atualizar_tabela():
    conn = get_db_connection()
    # adiciona a coluna "anotacoes" caso ela ainda não exista (FIZ ISSO SÓ POR GARANTIA POR TER TIDO ALGUNS PROBLEMAS ANTES)
    try:
        conn.execute('ALTER TABLE registros ADD COLUMN anotacoes TEXT DEFAULT ""')
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            print(f"Erro ao atualizar tabela: {e}")
    finally:
        conn.close()

# função para compactar arquivos em um ZIP
def zip_backup():
    zip_path = os.path.join('static', 'backup.zip')
    
    # cria o arquivo ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # adiciona a pasta e seu conteudo
        qrcodes_dir = os.path.join('static', 'qrcodes')
        if os.path.exists(qrcodes_dir):
            # adiciona a pasta qrcodes ao zip, inclusive a estrtura do direrotio
            for root, dirs, files in os.walk(qrcodes_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=qrcodes_dir)  # manteve a estrutura de pastas
                    zipf.write(file_path, arcname=os.path.join('qrcodes', arcname))  # adiciona no zip com caminho correto

        # o mesmo para users e seu conteudo
        users_dir = os.path.join('static', 'users')
        if os.path.exists(users_dir):
            # . . . MESMA COISA
            for root, dirs, files in os.walk(users_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, start=users_dir) 
                    zipf.write(file_path, arcname=os.path.join('users', arcname))  # ...
        
        # adicionar o arquivo .db, mais facil por ser só ele e não ter que fazer nada relacionado às pastas
        db_file = 'registros.db'
        if os.path.exists(db_file):
            zipf.write(db_file, os.path.basename(db_file))

    return zip_path
