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

* **Administrador**: criar livros (atualiza o catálogo persistente) e consultar
  requisições ativas (para saber quantos exemplares ainda podem ser requisitados).
* **Leitor**: consultar o catálogo, requisitar exemplares disponíveis e registar devoluções.

Os dados são guardados em JSON na pasta ``data/`` (criada automaticamente).
