"""
Requisições de exemplares da biblioteca.

Permite requisitar e devolver livros, e listar requisições ativas para o
administrador avaliar disponibilidade para novos requisitantes.
"""

import json
from pathlib import Path

import modulo_catalogo

_DADOS = Path(__file__).resolve().parent.parent / "data" / "requisicoes.json"


def _garantir_ficheiro():
    _DADOS.parent.mkdir(parents=True, exist_ok=True)
    if not _DADOS.exists():
        _DADOS.write_text("[]", encoding="utf-8")


def carregar_requisicoes():
    """
    Carrega todas as requisições.

    :return: Lista de dicionários com id, livro_id, utilizador_id, requisitante, ativa
    :rtype: list[dict]
    """
    _garantir_ficheiro()
    return json.loads(_DADOS.read_text(encoding="utf-8"))


def _guardar_requisicoes(regs):
    _DADOS.write_text(json.dumps(regs, ensure_ascii=False, indent=2), encoding="utf-8")


def _proximo_id(regs):
    if not regs:
        return 1
    return max(r["id"] for r in regs) + 1


def contar_requisicoes_ativas_por_livro(livro_id):
    """
    Conta quantos exemplares de um livro estão atualmente requisitados.

    :param livro_id: Identificador do livro
    :rtype: int
    """
    return sum(
        1
        for r in carregar_requisicoes()
        if r["livro_id"] == livro_id and r["ativa"]
    )


def exemplares_disponiveis(livro_id):
    """
    Calcula quantos exemplares ainda podem ser requisitados.

    :param livro_id: Identificador do livro
    :return: Número de exemplares livres ou 0 se o livro não existir
    :rtype: int
    """
    livro = modulo_catalogo.obter_livro(livro_id)
    if livro is None:
        return 0
    em_uso = contar_requisicoes_ativas_por_livro(livro_id)
    return max(0, livro["exemplares"] - em_uso)


def requisitar(livro_id, utilizador_id):
    """
    Cria uma requisição ativa se houver exemplar disponível.

    :param livro_id: Identificador do livro
    :param utilizador_id: Identificador do utilizador registado
    :return: Tupla (sucesso: bool, mensagem: str, requisicao ou None)
    :rtype: tuple[bool, str, dict | None]
    """
    import modulo_utilizadores

    utilizador = modulo_utilizadores.obter_utilizador(utilizador_id)
    if utilizador is None:
        return False, "Utilizador não encontrado. Peça ao administrador o registo.", None

    livro = modulo_catalogo.obter_livro(livro_id)
    if livro is None:
        return False, "Livro não encontrado.", None
    if exemplares_disponiveis(livro_id) <= 0:
        return False, "Não há exemplares disponíveis para requisição.", None
    regs = carregar_requisicoes()
    reg = {
        "id": _proximo_id(regs),
        "livro_id": livro_id,
        "utilizador_id": utilizador_id,
        "requisitante": utilizador["nome"],
        "ativa": True,
    }
    regs.append(reg)
    _guardar_requisicoes(regs)
    return True, "Requisição registada com sucesso.", reg


def devolver(requisicao_id):
    """
    Encerra uma requisição (devolução de exemplar).

    :param requisicao_id: Identificador da requisição
    :return: Tupla (sucesso, mensagem)
    :rtype: tuple[bool, str]
    """
    regs = carregar_requisicoes()
    for r in regs:
        if r["id"] == requisicao_id:
            if not r["ativa"]:
                return False, "Esta requisição já estava concluída."
            r["ativa"] = False
            _guardar_requisicoes(regs)
            return True, "Devolução registada."
    return False, "Requisição não encontrada."


def listar_requisitadas_admin():
    """
    Lista requisições ativas com título do livro e disponibilidade restante.

    Destina-se ao administrador para perceber se outros podem requisitar.

    :return: Texto formatado para consola
    :rtype: str
    """
    ativas = [r for r in carregar_requisicoes() if r["ativa"]]
    if not ativas:
        return "(Não existem requisições ativas.)"
    linhas = []
    for r in ativas:
        livro = modulo_catalogo.obter_livro(r["livro_id"])
        titulo = livro["titulo"] if livro else f"(id {r['livro_id']} desconhecido)"
        disp = exemplares_disponiveis(r["livro_id"])
        linhas.append(
            f"  Requisição #{r['id']}: «{titulo}» — {r['requisitante']}\n"
            f"    Exemplares ainda disponíveis para outros: {disp}"
        )
    return "\n".join(linhas)


def requisicao_pertence_a_utilizador(reg, utilizador_id):
    """
    Verifica se a requisição pertence ao utilizador (por id ou legado por nome).
    """
    uid = reg.get("utilizador_id")
    if uid is not None:
        return uid == utilizador_id
    import modulo_utilizadores

    u = modulo_utilizadores.obter_utilizador(utilizador_id)
    if u is None:
        return False
    return reg.get("requisitante", "").strip().lower() == u["nome"].strip().lower()


def listar_por_utilizador(utilizador_id):
    """
    Lista requisições ativas de um utilizador (para escolher devolução).

    :rtype: str
    """
    ativas = [
        r
        for r in carregar_requisicoes()
        if r["ativa"] and requisicao_pertence_a_utilizador(r, utilizador_id)
    ]
    if not ativas:
        return "(Sem requisições ativas para este utilizador.)"
    linhas = []
    for r in ativas:
        livro = modulo_catalogo.obter_livro(r["livro_id"])
        titulo = livro["titulo"] if livro else "?"
        linhas.append(f"  [#{r['id']}] «{titulo}»")
    return "\n".join(linhas)


def resumo_requisicoes_utilizador(utilizador_id):
    """
    Texto com totais e histórico recente de requisições do utilizador.

    :rtype: str
    """
    regs = carregar_requisicoes()
    todas = [r for r in regs if requisicao_pertence_a_utilizador(r, utilizador_id)]
    ativas = [r for r in todas if r["ativa"]]
    concluidas = [r for r in todas if not r["ativa"]]

    linhas = [
        f"    Requisições ativas: {len(ativas)}",
        f"    Requisições concluídas (histórico): {len(concluidas)}",
    ]
    if ativas:
        linhas.append("    Em requisição:")
        for r in ativas:
            livro = modulo_catalogo.obter_livro(r["livro_id"])
            tit = livro["titulo"] if livro else "?"
            linhas.append(f"      — «{tit}» (#{r['id']})")
    return "\n".join(linhas)


def listar_stock_por_livro_formatado():

    livros = modulo_catalogo.carregar_livros()
    if not livros:
        return "(Sem livros no catálogo.)"
    linhas = []
    for livro in livros:
        lid = livro["id"]
        total = livro["exemplares"]
        em_req = contar_requisicoes_ativas_por_livro(lid)
        disp = max(0, total - em_req)
        linhas.append(
            f"  [{lid}] «{livro['titulo']}»\n"
            f"      Stock total: {total} | Em requisição: {em_req} | Disponível: {disp}"
        )
    return "\n".join(linhas)
