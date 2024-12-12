# src/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from helpers import get_db_connection

auth_bp = Blueprint('auth', __name__)

#rota de login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        
        if usuario == "adjantar@01" and senha == "adjantar@01":  # alterar as credencias caso necessario
            session['logged_in'] = True  # marca a sessão como logada
            next_page = request.args.get('next')  # redireciona para a página original após login
            return redirect(next_page or url_for('index'))
        else:
            return 'Usuário ou senha incorretos', 403
    return render_template('login.html')

# excluir um registro
@auth_bp.route('/excluir/<id>', methods=['POST'])
def excluir(id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))  # redireciona para o login

    try:
        # conectar ao banco de dados e excluir o registro
        conn = get_db_connection()
        conn.execute('DELETE FROM registros WHERE id = ?', (id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao excluir registro: {e}")
    finally:
        conn.close()

    # caminhos das pastas de arquivos
    qr_code_path = os.path.join('static', 'qrcodes', f'{id}.png')
    user_image_path = os.path.join('static', 'users', id)

    # excluir qrcode se existir
    if os.path.exists(qr_code_path):
        os.remove(qr_code_path)

    # verifica as extensões possíveis para as imagens do usuário
    image_extensions = ['.jpg', '.jpeg', '.png']

    # exclui a foto do usuário com qualquer uma das extensões
    for ext in image_extensions:
        user_image_full_path = f'{user_image_path}{ext}'
        if os.path.exists(user_image_full_path):
            os.remove(user_image_full_path)

    return redirect(url_for('index'))

# rota para visualizar os detalhes de um registro
@auth_bp.route('/view/<id>', methods=['GET', 'POST'])
def view(id):
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))  # ...

    conn = get_db_connection()
    registro = conn.execute('SELECT * FROM registros WHERE id = ?', (id,)).fetchone()
    conn.close()

    if registro is None:
        return render_template('error.html', mensagem="ID não encontrado.", id=id), 404

    if request.method == 'POST':
        senha = request.form.get('senha')
        if senha == "saveall":
            situacao = request.form.get('situacao')  #obtendo a situacao
            anotacoes = request.form.get('anotacoes', '').strip()

            if not situacao:
                flash('A situação não pode estar vazia!', 'danger')
                return redirect(url_for('auth.view', id=id))

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
            return redirect(url_for('auth.view', id=id))

    return render_template('view.html', id=id, dados=registro)

# rota para sair e desconectar
@auth_bp.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove a chave de sessão, deslogando o usuário
    return redirect(url_for('auth.login'))
