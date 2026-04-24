"""
Gestão do catálogo de livros (persistência em JSON).

Este módulo expõe operações para o administrador manter o catálogo atualizado
e para qualquer perfil listar os livros disponíveis para consulta.
"""

import json
from pathlib import Path

_DADOS = Path(__file__).resolve().parent.parent / "data" / "livros.json"


def _garantir_ficheiro():
    _DADOS.parent.mkdir(parents=True, exist_ok=True)
    if not _DADOS.exists():
        _DADOS.write_text("[]", encoding="utf-8")


def carregar_livros():
    """
    Carrega todos os livros do ficheiro de dados.

    :return: Lista de dicionários com chaves id, titulo, autor, exemplares
    :rtype: list[dict]
    """
    _garantir_ficheiro()
    return json.loads(_DADOS.read_text(encoding="utf-8"))


def _guardar_livros(livros):
    _DADOS.write_text(json.dumps(livros, ensure_ascii=False, indent=2), encoding="utf-8")


def _proximo_id(livros):
    if not livros:
        return 1
    return max(l["id"] for l in livros) + 1


def adicionar_livro(titulo, autor, exemplares):
    """
    Regista um novo livro no catálogo.

    :param titulo: Título do livro
    :param autor: Nome do autor
    :param exemplares: Número de exemplares físicos (>= 1)
    :return: O dicionário do livro criado
    :rtype: dict
    """
    livros = carregar_livros()
    livro = {
        "id": _proximo_id(livros),
        "titulo": titulo.strip(),
        "autor": autor.strip(),
        "exemplares": int(exemplares),
    }
    livros.append(livro)
    _guardar_livros(livros)
    return livro


def obter_livro(livro_id):
    """
    Obtém um livro pelo identificador.

    :param livro_id: Identificador do livro
    :return: Dicionário do livro ou None se não existir
    :rtype: dict | None
    """
    for livro in carregar_livros():
        if livro["id"] == livro_id:
            return livro
    return None


def listar_catalogo_formatado():
    """
    Devolve linhas de texto com o catálogo completo para apresentação na consola.

    :return: Texto com um livro por linha (id, título, autor, exemplares)
    :rtype: str
    """
    livros = carregar_livros()
    if not livros:
        return "(Catálogo vazio — ainda não existem livros registados.)"
    linhas = []
    for livro in livros:
        linhas.append(
            f"  [{livro['id']}] {livro['titulo']} — {livro['autor']} "
            f"({livro['exemplares']} exemplar(es) no total)"
        )
    return "\n".join(linhas)


if __name__ == "__main__":
    print(listar_catalogo_formatado())
