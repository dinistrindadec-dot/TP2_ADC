"""
Gestão do catálogo de livros (persistência em JSON).

Este módulo expõe operações para o administrador manter o catálogo atualizado
e para qualquer perfil listar os livros disponíveis para consulta.
"""

import json
from pathlib import Path

# Caminho para o ficheiro JSON do catálogo.
_DADOS = Path(__file__).resolve().parent.parent / "data" / "livros.json"


def _garantir_ficheiro():
    """Garante que a pasta e o ficheiro JSON do catálogo existem.

    Se o ficheiro ainda não existir, é criado com uma lista vazia (`[]`).
    """
    _DADOS.parent.mkdir(parents=True, exist_ok=True)
    if not _DADOS.exists():
        _DADOS.write_text("[]", encoding="utf-8")


def carregar_livros():
    """
    Carrega todos os livros do ficheiro de dados.

    Returns:
        list[dict]: Lista de livros, onde cada livro contém:
            - `id` (int)
            - `titulo` (str)
            - `autor` (str)
            - `exemplares` (int)
            - `tema` (str, opcional)
    """
    _garantir_ficheiro()
    return json.loads(_DADOS.read_text(encoding="utf-8"))


def _guardar_livros(livros):
    """Persiste a lista completa de livros no ficheiro JSON.

    Args:
        livros (list[dict]): Lista de livros a gravar.
    """
    _DADOS.write_text(json.dumps(livros, ensure_ascii=False, indent=2), encoding="utf-8")


def _proximo_id(livros):
    """Calcula o próximo identificador sequencial para um livro.

    Args:
        livros (list[dict]): Lista atual de livros.

    Returns:
        int: O próximo `id` (1 se a lista estiver vazia).
    """
    if not livros:
        return 1
    return max(l["id"] for l in livros) + 1


def adicionar_livro(titulo, autor, exemplares, tema=""):
    """
    Regista um novo livro no catálogo.

    Args:
        titulo (str): Título do livro.
        autor (str): Nome do autor.
        exemplares (int): Número de exemplares físicos (>= 1).
        tema (str): Tema ou género (opcional), usado na pesquisa.

    Returns:
        dict: O dicionário do livro criado e persistido.
    """
    livros = carregar_livros()
    livro = {
        "id": _proximo_id(livros),
        "titulo": titulo.strip(),
        "autor": autor.strip(),
        "exemplares": int(exemplares),
        "tema": (tema or "").strip(),
    }
    livros.append(livro)
    _guardar_livros(livros)
    return livro


def pesquisar_por_autor(termo):
    """Pesquisa livros por autor (correspondência parcial, case-insensitive).

    Args:
        termo (str): Texto (parcial) a procurar no campo `autor`.

    Returns:
        list[dict]: Lista de livros cujo autor contém o `termo`.
    """
    termo = termo.strip().lower()
    if not termo:
        return []
    return [
        livro
        for livro in carregar_livros()
        if termo in livro.get("autor", "").lower()
    ]


def pesquisar_por_tema(termo):
    """Pesquisa livros por tema/género (correspondência parcial).

    Args:
        termo (str): Texto (parcial) a procurar no campo `tema`.

    Returns:
        list[dict]: Lista de livros cujo tema contém o `termo`.
    """
    termo = termo.strip().lower()
    if not termo:
        return []
    return [
        livro
        for livro in carregar_livros()
        if termo in livro.get("tema", "").lower()
    ]


def obter_livro(livro_id):
    """
    Obtém um livro pelo identificador.

    Args:
        livro_id (int): Identificador do livro.

    Returns:
        dict | None: Dicionário do livro, ou `None` se não existir.
    """
    for livro in carregar_livros():
        if livro["id"] == livro_id:
            return livro
    return None


def atualizar_exemplares(livro_id, novo_total):

    novo_total = int(novo_total)
    if novo_total < 1:
        return False, "O stock total tem de ser pelo menos 1."
    livros = carregar_livros()
    for livro in livros:
        if livro["id"] == livro_id:
            livro["exemplares"] = novo_total
            _guardar_livros(livros)
            return True, "Stock atualizado."
    return False, "Livro não encontrado."


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
        tema = livro.get("tema", "").strip()
        extra = f" | Tema: {tema}" if tema else ""
        linhas.append(
            f"  [{livro['id']}] {livro['titulo']} — {livro['autor']}{extra} "
            f"({livro['exemplares']} exemplar(es) no total)"
        )
    return "\n".join(linhas)


if __name__ == "__main__":
    print(listar_catalogo_formatado())
