Biblioteca (TP2)
=================

Projeto da UC **Ambientes de Desenvolvimento Colaborativo**, com a mesma organização
do repositório de referência (``src``, ``docs_sphinx``, ``requirements.txt``).

Execução
--------

Na raiz do projeto ``TP2``::

    python src/main.py

Funcionalidades
---------------

* **Administrador**: criar livros; consultar requisições ativas; registar utilizadores;
  consultar **fichas** de utilizadores (dados e resumo de requisições); ver e **ajustar o stock**
  (exemplares totais por livro, respeitando o que está em requisição).
* **Leitor**: consultar o catálogo; requisitar e devolver com o **id de utilizador** (tem de
  estar registado pelo administrador).

Os dados são guardados em JSON na pasta ``data/`` (criada automaticamente).
