from flask import Flask
from flask_talisman import Talisman  #adicionar cabeçalhos de segurança usando o talisman

from helpers import criar_tabela, atualizar_tabela

#importar as funções do routes
from src.routes import *

app = Flask(__name__, static_url_path='/static', static_folder='static')

#registrando cada blueprint usando flask
from src.auth import auth_bp
from src.register import register_bp
app.register_blueprint(auth_bp)
app.register_blueprint(register_bp)

#========================SESSÃO
app.secret_key = '02faf3e2914'  #chave secreta para uso futuro no app TODO (REMOVER DE PROJETOS GRANDES)

#configura o talisman pra os cabecarios de segurança csp (e futuramente usando nas tags)
Talisman(app, content_security_policy={
    'default-src': '\'self\'',
    'img-src': '\'self\' data:',
    'script-src': '\'self\' https://cdn.jsdelivr.net',
    'style-src': '\'self\' https://cdn.jsdelivr.net',
})

Talisman(app, frame_options="DENY")

#registrando as rotas
backup_route(app)
index_route(app)
user_image_route(app)
page_not_found_route(app)
force_https_route(app)
notforme_route(app)

if __name__ == '__main__':
    criar_tabela()  #cria a tabela se certificando
    atualizar_tabela() #usei pra alterar umas coisas mas enfim
    app.run(host='0.0.0.0', port=5000, debug=True)  #debug true nn é pra produção, mas posso enviar assim
