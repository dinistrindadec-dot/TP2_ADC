"""
Gestão de requisições de livros (ficheiro JSON).

:Autor: TP2 — Biblioteca
"""

import json
from pathlib import Path

_FICHEIRO = Path(__file__).resolve().parent.parent / "data" / "requisicoes.json"


def _carregar_ficheiro():
    if not _FICHEIRO.exists():
        return []
    with open(_FICHEIRO, encoding="utf-8") as f:
        return json.load(f)


def _guardar_ficheiro(requisicoes):
    _FICHEIRO.parent.mkdir(parents=True, exist_ok=True)
    with open(_FICHEIRO, "w", encoding="utf-8") as f:
        json.dump(requisicoes, f, ensure_ascii=False, indent=2)


def listar_requisicoes():
    """Devolve todas as requisições (ativas e inativas)."""
    return list(_carregar_ficheiro())


def requisicoes_ativas_por_livro(id_livro):
    """Conta requisições ativas para um dado livro."""
    n = 0
    for r in _carregar_ficheiro():
        if r.get("id_livro") == id_livro and r.get("ativa", False):
            n += 1
    return n


def exemplares_disponiveis(livro):
    """
    Calcula quantos exemplares ainda podem ser requisitados.

    :param livro: dict com chaves id e exemplares
    """
    total = int(livro.get("exemplares", 0))
    emprestados = requisicoes_ativas_por_livro(livro["id"])
    return max(0, total - emprestados)


def listar_requisicoes_ativas_para_admin(obter_livro):
    """
    Constrói linhas descritivas das requisições ativas para o administrador.

    :param obter_livro: função(id_livro) -> dict ou None (ex.: modulo_catalogo.obter_livro)
    :return: lista de strings para impressão
    """
    linhas = []
    for r in _carregar_ficheiro():
        if not r.get("ativa", False):
            continue
        lid = r.get("id_livro")
        livro = obter_livro(lid) if lid is not None else None
        titulo = livro["titulo"] if livro else f"(livro id={lid} desconhecido)"
        disp = exemplares_disponiveis(livro) if livro else "?"
        linhas.append(
            f"  Requisição #{r.get('id')} | \"{titulo}\" | "
            f"Requisitante: {r.get('requisitante', '?')} | "
            f"Disponíveis para novos pedidos: {disp}"
        )
    return linhas
