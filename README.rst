Biblioteca (TP2)
=================

Projeto da UC **Ambientes de Desenvolvimento Colaborativo**, com a mesma organização
do repositório de referência (``src``, ``docs_sphinx``, ``requirements.txt``).

Execução
--------

Na raiz do projeto ``TP2``::

    python src/main.py

Estrutura de Módulos
--------------------

* **modulo_catalogo.py**: Gestão da persistência de livros. Permite adicionar livros, atualizar quantidades de stock e pesquisar obras por tema ou autor.
* **modulo_requisicoes.py**: Lida com os empréstimos e devoluções. Calcula a disponibilidade de exemplares em tempo real e gere prazos de devolução (prazo predefinido de 14 dias).
* **modulo_utilizadores.py**: Gere o registo de utilizadores (nome, e-mail, telemóvel) e a compilação das suas fichas com histórico de requisições.
* **modulo_backup.py**: Responsável por criar cópias de segurança automáticas com carimbo de data/hora (timestamp) de todos os dados do sistema.
* **main.py**: Ponto de entrada da aplicação, contendo os menus interativos que separam as ações de Administrador e de Leitor.

Funcionalidades
---------------

**Administrador**
* **Criar livros**: Adicionar obras ao catálogo especificando título, autor, número de exemplares e um tema opcional.
* **Ver requisições ativas**: Consultar os exemplares atualmente emprestados, os respetivos requisitantes e a disponibilidade restante.
* **Consultar o catálogo completo**: Listagem formatada de todos os livros registados na biblioteca.
* **Registar utilizadores**: Criar perfis de utilizadores para que possam efetuar requisições.
* **Fichas de utilizadores**: Ver todos os dados de contacto de um utilizador específico, as suas requisições ativas e o histórico (requisições concluídas).
* **Gerir stock**: Visualizar e ajustar a quantidade física total de exemplares de um livro (impossibilitando baixar o limite para um valor inferior aos exemplares já requisitados).
* **Backup**: Gerar imediatamente uma cópia de segurança dos ficheiros de dados na pasta ``data/backups/``.

**Leitor**
* **Consultar catálogo**: Ver os livros, incluindo o estado exato de disponibilidade (ex: "X exemplar(es) livre(s)" ou "Sem exemplares no stock").
* **Requisitar livro**: Fazer o empréstimo de uma obra informando o seu ID de utilizador. O prazo de devolução é gerado automaticamente.
* **Devolver livro**: Encerrar uma requisição ativa que pertença ao seu perfil.
* **Prazos das requisições**: Consultar o tempo restante até à devolução dos seus livros, com indicação clara dos dias em falta ou em atraso.
* **Pesquisar livros**: Encontrar livros rapidamente procurando por autor ou tema (a pesquisa ignora maiúsculas e minúsculas).
* **Atualizar contactos**: Modificar o e-mail ou telemóvel associado à sua conta sem necessidade de intervenção do administrador.

Armazenamento de Dados
----------------------

Os dados são guardados nativamente em formato JSON (``livros.json``, ``requisicoes.json``, ``utilizadores.json``) na diretoria ``data/``, que é criada de forma automática na primeira execução do programa. Os backups preventivos ficam alojados em ``data/backups/``.