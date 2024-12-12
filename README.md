# 🌐 EasyInvite - Site de registro e controle de convidados

Bem-vindo ao repositório oficial do projeto! Este é um projeto desenvolvido para facilitar o registro de relações de convidados de um evento e melhorar a forma de controle da recepção do evento

## ✨ Sobre o Projeto

O site foi criado para exibir informações referente aos usuarios registrados, como:
- ID, Nome do responsável, Convidados, Anotações e Situação (além da imagem de cada usuario e o QRCode de convite do mesmo)

Além disso, o site oferece:
- **Sistema de login**:
  - Backup das informações da web (mais usado no modo de produção)
  - Facilidade e possibilidade de gerir anotações e situação de convidados do evento.
- **Layout responsivo**: Totalmente adaptável para dispositivos desktop e móveis.

## 🔧 Tecnologias Utilizadas

- **HTML5** e **CSS3** para estrutura e estilização.
- **JavaScript** para interações dinâmicas.
- **Python3** para elaboração e estrutura do backend, rotas, funções e outros serviços.
- **Dashboard Render** como plataforma de hospedagem, que roda o serviço backend.

## 🎨 Layout e Design

### Página Inicial (index.html)
- Exibe uma **tabela** com as informações dos convidados registrados atualmente no arquivo db.
- **Campo de pesquisa** que é usado para filtrar convidados pelo ID.
- **Link no ID** para navegação entre as paginas /view de cada usuario.
- Totalmente centralizado e responsivo.

### Não é para mim (notforme.html "site.com/notforme")
- Exibe uma mensagem de aviso ao usuario não autenticado de que talvez essa págia não seja para ele (caso não faça parte da equipe de recepção do evento)

## 🔍 Como Utilizar

1. Acesse o site pelo link gerado no seu terminal.
2. Acesse o link, você será redirecionado para /login, insira as credenciais que estão na pasta src dentro de auth.py.
3. Utilize o botão de registrar da index.html (rota inicial "/"):
   - **Registrar** para abrir a rota /registrar e inserir um novo usuario no registro, inserindo nome*, convidados, anotações, e imagem.

## 🔄 Atualizações

- As informações dos usuarios registrados e o conteudo do banco de dados podem facilmente ser editados por fora, mesmo dentro de produção, recomendo integrar google firebase ao mesmo, mas caso mantenha SQLITE3 apenas use /backup para baixar o .db e então envie as atualizações locais para a produção junto do .db que já está na produção

## © Créditos

Desenvolvido por:
- **Marcos Emanuel Celestino Tavares**
- GitHub: [fumiko0701](https://github.com/fumiko0701)

Se você encontrou algum problema ou deseja contribuir, fique à vontade para abrir uma *issue* ou enviar um *pull request*.

---

📢 Recebendo dicas e avaliações
