import sqlite3
import random, string, os
from flask import Blueprint, request, session, redirect, url_for, render_template
from helpers import UPLOAD_FOLDER, allowed_file, get_db_connection, gerar_qr_code

# define a blueprint
register_bp = Blueprint('register', __name__)

#gera o ID aleatório
def gerar_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@register_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    #usuario tá logado?
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        #gera o id e registra os dados
        id_gerado = gerar_id()
        responsavel = request.form['responsavel']
        convidados = request.form['convidados']
        anotacoes = request.form.get('anotacoes', '').strip()  #recupera o campo, padrão vazio se nn preenchido
        situacao = 'Em espera'

        # processar o upload do arquivo de imagem
        imagem_filename = None
        if 'imagem' in request.files:
            imagem = request.files['imagem']
            if imagem and allowed_file(imagem.filename):
                #criando a pasta dos arquivos de imagm se nn existir
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                    print("Pasta 'users' criada com sucesso.")
                else:
                    print("A pasta 'users' já existe.")


                #define extensão do arquivo usando a original
                extensao = imagem.filename.rsplit('.', 1)[1].lower()

                #nome do arquivo = id gerado
                imagem_filename = f"{id_gerado}.{extensao}"
                imagem_path = os.path.join(UPLOAD_FOLDER, imagem_filename)

                #salva
                imagem.save(imagem_path)
                print(f"Imagem salva como {imagem_filename}")  #verifica se a imagem foi salva

        #insere os dados no banco de dados
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO registros (id, responsavel, convidados, anotacoes, situacao) VALUES (?, ?, ?, ?, ?)',
                         (id_gerado, responsavel, convidados, anotacoes, situacao))
            conn.commit()

            #gera o qrcode para esse novo IQ e salva
            gerar_qr_code(id_gerado)
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Erro ao inserir dados: {e}")
        finally:
            conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('registrar.html')


