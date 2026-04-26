"""
Requisições de exemplares da biblioteca.

Permite requisitar e devolver livros, e listar requisições ativas para o
administrador avaliar disponibilidade para novos requisitantes.
"""

import json
from datetime import date, timedelta
from pathlib import Path

import modulo_catalogo

_DADOS = Path(__file__).resolve().parent.parent / "data" / "requisicoes.json"

# Prazo de devolução contado a partir da data da requisição (novas requisições).
DIAS_PRAZO_EMPRESTIMO = 14


def _garantir_ficheiro():
    """Garante que a pasta e o ficheiro JSON de requisições existem.

    Se o ficheiro ainda não existir, cria-o com uma lista vazia (`[]`).
    """
    _DADOS.parent.mkdir(parents=True, exist_ok=True)
    if not _DADOS.exists():
        _DADOS.write_text("[]", encoding="utf-8")


def carregar_requisicoes():
    """Carrega todas as requisições a partir do ficheiro JSON.

    Estrutura típica de uma requisição (registos recentes)::
        {
          "id": int,
          "livro_id": int,
          "utilizador_id": int,
          "requisitante": str,
          "ativa": bool,
          "data_requisicao": "YYYY-MM-DD",
          "data_limite": "YYYY-MM-DD"
        }

    Nota: podem existir registos antigos sem `utilizador_id` e/ou sem datas.

    Returns:
        list[dict]: Lista de requisições (ativas e concluídas).
    """
    _garantir_ficheiro()
    return json.loads(_DADOS.read_text(encoding="utf-8"))


def _guardar_requisicoes(regs):
    """Persiste a lista completa de requisições no ficheiro JSON.

    Args:
        regs (list[dict]): Lista de requisições a gravar.
    """
    _DADOS.write_text(
        json.dumps(regs, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _proximo_id(regs):
    """Calcula o próximo identificador sequencial para uma requisição.

    Args:
        regs (list[dict]): Lista de requisições.

    Returns:
        int: Próximo identificador.
    """
    if not regs:
        return 1
    return max(r["id"] for r in regs) + 1


def contar_requisicoes_ativas_por_livro(livro_id):
    """Conta quantas requisições ativas existem para um determinado livro.

    Cada registo ativo corresponde a um exemplar emprestado.

    Args:
        livro_id (int): Identificador do livro.

    Returns:
        int: Número de exemplares atualmente em requisição.
    """
    return sum(
        1
        for r in carregar_requisicoes()
        if r["livro_id"] == livro_id and r["ativa"]
    )


def texto_tempo_restante_devolucao(data_limite_iso):
    """Converte uma data limite (ISO) num texto amigável sobre o prazo.

    Este helper existe para manter a lógica de apresentação consistente em
    vários ecrãs/fluxos (listagens por utilizador e painel do administrador).

    Args:
        data_limite_iso (str | None): Data em formato ISO (`YYYY-MM-DD`) ou
            `None`.

    Returns:
        str: Mensagem humana (dias restantes, último dia, ou atraso).
    """
    if not data_limite_iso:
        return "Prazo não definido nesta requisição (registo antigo)."
    try:
        limite = date.fromisoformat(data_limite_iso)
    except ValueError:
        return "Data limite inválida no registo."
    hoje = date.today()
    delta = (limite - hoje).days
    limite_pt = limite.strftime("%d/%m/%Y")
    if delta > 1:
        return f"Faltam {delta} dias até ao limite de devolução ({limite_pt})."
    if delta == 1:
        return f"Falta 1 dia até ao limite de devolução ({limite_pt})."
    if delta == 0:
        return f"Hoje é o último dia do prazo ({limite_pt})."
    return f"Em atraso há {abs(delta)} dia(s). Limite era {limite_pt}."


def _linha_livro_com_disponibilidade(livro):
    """Gera uma linha (multi-linha) para mostrar um livro e a sua disponibilidade.

    Args:
        livro (dict): Livro (como devolvido por
            `modulo_catalogo.carregar_livros`).

    Returns:
        str: Texto formatado com título/autor/tema e um resumo do estado.
    """
    lid = livro["id"]
    disp = exemplares_disponiveis(lid)
    total = livro["exemplares"]
    if disp > 0:
        estado = f"Disponível — {disp} exemplar(es) livre(s) (de {total})"
    elif total == 0:
        estado = "Sem exemplares no stock"
    else:
        estado = f"Emprestado — os {total} exemplar(es) estão requisitados"
    tema = livro.get("tema", "").strip()
    extra_tema = f" | Tema: {tema}" if tema else ""
    return (
        f"  [{lid}] «{livro['titulo']}» — {livro['autor']}{extra_tema}\n"
        f"      {estado}"
    )


def catalogo_disponibilidade_formatado():
    """Devolve o catálogo completo com disponibilidade calculada.

    Returns:
        str: Texto pronto a imprimir na consola.
    """
    livros = modulo_catalogo.carregar_livros()
    if not livros:
        return "(Catálogo vazio — ainda não existem livros registados.)"
    return "\n".join(_linha_livro_com_disponibilidade(livro) for livro in livros)


def formatar_livros_com_disponibilidade(livros):
    """Formata uma lista de livros (subconjunto do catálogo) com disponibilidade.

    Args:
        livros (list[dict]): Livros a formatar (como devolvidos por pesquisas).

    Returns:
        str: Texto pronto a imprimir.
    """
    if not livros:
        return "(Nenhum livro corresponde à pesquisa.)"
    return "\n".join(_linha_livro_com_disponibilidade(livro) for livro in livros)


def exemplares_disponiveis(livro_id):
    """Calcula quantos exemplares de um livro ainda podem ser requisitados.

    A disponibilidade é calculada como:
    `exemplares_total - requisições_ativas` (limitado a 0).

    Args:
        livro_id (int): Identificador do livro.

    Returns:
        int: Número de exemplares disponíveis (0 se o livro não existir).
    """
    livro = modulo_catalogo.obter_livro(livro_id)
    if livro is None:
        return 0
    em_uso = contar_requisicoes_ativas_por_livro(livro_id)
    return max(0, livro["exemplares"] - em_uso)


def requisitar(livro_id, utilizador_id):
    """Cria uma nova requisição ativa, se houver exemplar disponível.

    Este método valida:
    - existência do utilizador
    - existência do livro
    - disponibilidade (pelo menos 1 exemplar livre)

    Em caso de sucesso, grava a requisição com datas (hoje e data limite).

    Args:
        livro_id (int): Identificador do livro.
        utilizador_id (int): Identificador do utilizador.

    Returns:
        tuple[bool, str, dict | None]:
            - sucesso (bool)
            - mensagem (str) para apresentação
            - registo da requisição (dict) ou `None` em caso de erro
    """
    # Import local para evitar dependência circular em tempo de import.
    import modulo_utilizadores

    utilizador = modulo_utilizadores.obter_utilizador(utilizador_id)
    if utilizador is None:
        return (
            False,
            "Utilizador não encontrado. Peça ao administrador o registo.",
            None,
        )

    livro = modulo_catalogo.obter_livro(livro_id)
    if livro is None:
        return False, "Livro não encontrado.", None
    if exemplares_disponiveis(livro_id) <= 0:
        return False, "Não há exemplares disponíveis para requisição.", None
    regs = carregar_requisicoes()
    hoje = date.today()
    limite = hoje + timedelta(days=DIAS_PRAZO_EMPRESTIMO)
    reg = {
        "id": _proximo_id(regs),
        "livro_id": livro_id,
        "utilizador_id": utilizador_id,
        "requisitante": utilizador["nome"],
        "ativa": True,
        "data_requisicao": hoje.isoformat(),
        "data_limite": limite.isoformat(),
    }
    regs.append(reg)
    _guardar_requisicoes(regs)
    msg = (
        "Requisição registada com sucesso. "
        f"Devolução até {limite.strftime('%d/%m/%Y')} "
        f"({DIAS_PRAZO_EMPRESTIMO} dias)."
    )
    return True, msg, reg


def devolver(requisicao_id):
    """Encerra uma requisição ativa (regista a devolução do exemplar).

    Args:
        requisicao_id (int): Identificador da requisição.

    Returns:
        tuple[bool, str]: Resultado da operação e mensagem.
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
    """Lista requisições ativas para o administrador.

    Inclui:
    - identificador da requisição
    - título do livro
    - nome do requisitante
    - exemplares ainda disponíveis para terceiros
    - data limite (se existir e for válida)

    Returns:
        str: Texto formatado para consola.
    """
    ativas = [r for r in carregar_requisicoes() if r["ativa"]]
    if not ativas:
        return "(Não existem requisições ativas.)"
    linhas = []
    for r in ativas:
        livro = modulo_catalogo.obter_livro(r["livro_id"])
        titulo = livro["titulo"] if livro else f"(id {r['livro_id']} desconhecido)"
        disp = exemplares_disponiveis(r["livro_id"])
        prazo = r.get("data_limite")
        linha_prazo = ""
        if prazo:
            try:
                linha_prazo = (
                    f"\n    Devolução até: "
                    f"{date.fromisoformat(prazo).strftime('%d/%m/%Y')}"
                )
            except ValueError:
                pass
        linhas.append(
            f"  Requisição #{r['id']}: «{titulo}» — {r['requisitante']}\n"
            f"    Exemplares ainda disponíveis para outros: {disp}{linha_prazo}"
        )
    return "\n".join(linhas)


def requisicao_pertence_a_utilizador(reg, utilizador_id):
    """Valida se uma requisição pertence a um utilizador.

    A regra preferencial é por `utilizador_id`. Para compatibilidade com
    registos antigos (legados), se `utilizador_id` não existir no registo,
    valida por nome (`requisitante`).

    Args:
        reg (dict): Registo de requisição.
        utilizador_id (int): Identificador do utilizador.

    Returns:
        bool: `True` se a requisição pertencer ao utilizador.
    """
    # Alguns registos antigos podem não ter `utilizador_id`, apenas nome.
    uid = reg.get("utilizador_id")
    if uid is not None:
        return uid == utilizador_id
    import modulo_utilizadores

    u = modulo_utilizadores.obter_utilizador(utilizador_id)
    if u is None:
        return False
    return reg.get("requisitante", "").strip().lower() == u["nome"].strip().lower()


def prazos_minhas_requisicoes_formatado(utilizador_id):
    """Lista requisições ativas do utilizador e descreve o prazo de devolução.

    Args:
        utilizador_id (int): Identificador do utilizador.

    Returns:
        str: Texto formatado para consola.
    """
    ativas = [
        r
        for r in carregar_requisicoes()
        if r["ativa"] and requisicao_pertence_a_utilizador(r, utilizador_id)
    ]
    if not ativas:
        return "(Sem requisições ativas.)"
    linhas = []
    for r in ativas:
        livro = modulo_catalogo.obter_livro(r["livro_id"])
        titulo = livro["titulo"] if livro else "?"
        linhas.append(f"  [#{r['id']}] «{titulo}»")
        linhas.append(
            f"      {texto_tempo_restante_devolucao(r.get('data_limite'))}"
        )
    return "\n".join(linhas)


def listar_por_utilizador(utilizador_id):
    """Lista requisições ativas de um utilizador (para escolher devolução).

    Args:
        utilizador_id (int): Identificador do utilizador.

    Returns:
        str: Texto formatado para consola.
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
        linhas.append(f"      {texto_tempo_restante_devolucao(r.get('data_limite'))}")
    return "\n".join(linhas)


def resumo_requisicoes_utilizador(utilizador_id):
    """Gera um resumo textual das requisições de um utilizador.

    Inclui contagens de requisições ativas e concluídas e, se existirem
    requisições ativas, lista-as com o respetivo prazo.

    Args:
        utilizador_id (int): Identificador do utilizador.

    Returns:
        str: Texto formatado para a consola.
    """
    # O resumo é consumido pelo módulo de utilizadores (ficha de utilizador).
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
            linhas.append(
                f"        {texto_tempo_restante_devolucao(r.get('data_limite'))}"
            )
    return "\n".join(linhas)


def listar_stock_por_livro_formatado():
    """Formata um relatório de stock por livro.

    Para cada livro apresenta:
    - stock total no catálogo
    - quantos exemplares estão em requisição (requisições ativas)
    - quantos exemplares estão disponíveis

    Returns:
        str: Texto pronto a imprimir na consola.
    """
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
