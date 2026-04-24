"""
Gestão do catálogo de livros (ficheiro JSON).

:Autor: TP2 — Biblioteca
"""

import json
from pathlib import Path

_FICHEIRO = Path(__file__).resolve().parent.parent / "data" / "catalogo.json"


def _carregar_ficheiro():
    if not _FICHEIRO.exists():
        return []
    with open(_FICHEIRO, encoding="utf-8") as f:
        return json.load(f)


def _guardar_ficheiro(livros):
    _FICHEIRO.parent.mkdir(parents=True, exist_ok=True)
    with open(_FICHEIRO, "w", encoding="utf-8") as f:
        json.dump(livros, f, ensure_ascii=False, indent=2)


def listar_livros():
    """Devolve uma cópia da lista de livros no catálogo."""
    return list(_carregar_ficheiro())


def obter_livro(id_livro):
    """Devolve o dicionário do livro ou None."""
    for livro in _carregar_ficheiro():
        if livro.get("id") == id_livro:
            return dict(livro)
    return None


def criar_livro(titulo, autor, exemplares):
    """
    Adiciona um livro ao catálogo e grava no disco.

    :param titulo: Título do livro
    :param autor: Nome do autor
    :param exemplares: Número de exemplares (inteiro >= 0)
    :return: O dicionário do livro criado
    """
    livros = _carregar_ficheiro()
    novo_id = max((l.get("id", 0) for l in livros), default=0) + 1
    livro = {
        "id": novo_id,
        "titulo": titulo.strip(),
        "autor": autor.strip(),
        "exemplares": int(exemplares),
    }
    livros.append(livro)
    _guardar_ficheiro(livros)
    return livro
