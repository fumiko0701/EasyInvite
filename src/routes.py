from flask import render_template, redirect, url_for, session, request, send_file, send_from_directory
import os
from helpers import zip_backup, get_db_connection

def notforme_route(app):
    @app.route('/notforme')
    def notforme():
        return render_template('notforme.html') #pagina que é exibida quando usuarios não autenticados entram numa pagina de view id
    
# Página de backup
def backup_route(app):
    @app.route('/backup', methods=['GET', 'POST'])
    def backup():
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('auth.login'))  # redireciona para login se nn tiver logado

        if request.method == 'POST':
            #gera o backup zip com todos os arquivos
            zip_path = zip_backup()
            
            #retorna o compactado como download hehe
            return send_file(zip_path, as_attachment=True)

        return render_template('backup.html')

#pagina principal
def index_route(app):
    @app.route('/')
    def index():
        #verificar se usuario tá autenticado
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('auth.login'))  #vai pro login

        conn = get_db_connection()
        #ordena os registros pelo nome do responsavel, em ordem alfabetica
        registros = conn.execute('SELECT * FROM registros ORDER BY responsavel ASC').fetchall()
        conn.close()

        #organiza os dados como um dicionario e envia para o frontend
        return render_template('index.html', registros=registros)

#imagens de usuários
def user_image_route(app):
    @app.route('/static/users/<id>')
    def user_image(id):
        #onde está armazenada
        image_dir = 'static/users'
        extensions = ['.jpg', '.jpeg', '.png']
        
        #verifica se existe
        for ext in extensions:
            image_path = os.path.join(image_dir, f"{id}{ext}")
            if os.path.exists(image_path):
                return send_from_directory(image_dir, f"{id}{ext}")
        
        # se nn existir, retorna padrão #USADO NA VIEW ID QUANDO NN TEM IMAGEM
        return send_from_directory(image_dir, 'default.png')

# erro 404 de ID ou rotas
def page_not_found_route(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', mensagem="Página não encontrada."), 404

# vai para HTTPS
def force_https_route(app):
    @app.before_request
    def force_https():
        # verifica se não é segura
        if not request.is_secure and 'X-Forwarded-Proto' in request.headers and request.headers['X-Forwarded-Proto'] == 'http':
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)
