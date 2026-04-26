"""Gestão de utilizadores (persistência em JSON).

Este módulo concentra operações CRUD simples para utilizadores da aplicação.
A persistência é feita num ficheiro JSON dentro da pasta `data/` do projeto.

Estrutura esperada por registo de utilizador::

    {
      "id": int,
      "nome": str,
      "email": str,
      "telefone": str
    }

As funções deste módulo são chamadas pelo `main.py` e por outros módulos
(ex.: `modulo_requisicoes`) para validar identidades e apresentar fichas.
"""
import json
from pathlib import Path

# Caminho para o ficheiro de dados de utilizadores.
_DADOS = Path(__file__).resolve().parent.parent / "data" / "utilizadores.json"


def _garantir_ficheiro():
    """Garante que a pasta e o ficheiro JSON de utilizadores existem.

    Esta função é um detalhe interno de persistência. Se o ficheiro ainda não
    existir, cria-o com uma lista vazia (`[]`).
    """
    _DADOS.parent.mkdir(parents=True, exist_ok=True)
    if not _DADOS.exists():
        _DADOS.write_text("[]", encoding="utf-8")


def carregar_utilizadores():
    """Carrega todos os utilizadores a partir do ficheiro JSON.

    Returns:
        list[dict]: Lista de utilizadores (cada um representado por um
        dicionário com as chaves `id`, `nome`, `email`, `telefone`).
    """
    _garantir_ficheiro()
    return json.loads(_DADOS.read_text(encoding="utf-8"))


def _guardar_utilizadores(regs):
    """Guarda a lista completa de utilizadores no ficheiro JSON.

    Args:
        regs (list[dict]): Lista de utilizadores a persistir.
    """
    _DADOS.write_text(json.dumps(regs, ensure_ascii=False, indent=2), encoding="utf-8")


def _proximo_id(regs):
    """Calcula o próximo identificador sequencial para um utilizador.

    Args:
        regs (list[dict]): Lista atual de utilizadores.

    Returns:
        int: O próximo `id` (1 se a lista estiver vazia).
    """
    if not regs:
        return 1
    return max(u["id"] for u in regs) + 1


def adicionar_utilizador(nome, email="", telefone=""):
    """Regista um novo utilizador.

    Valida o nome (obrigatório), normaliza os campos (trim) e persiste o
    registo no ficheiro JSON.

    Args:
        nome (str): Nome completo do utilizador. Campo obrigatório.
        email (str): Endereço de e-mail (opcional).
        telefone (str): Contacto telefónico (opcional).

    Returns:
        dict: Dicionário do utilizador criado (inclui `id`).

    Raises:
        ValueError: Se `nome` estiver vazio após `strip()`.
    """
    nome = nome.strip()
    if not nome:
        raise ValueError("O nome é obrigatório.")
    regs = carregar_utilizadores()
    u = {
        "id": _proximo_id(regs),
        "nome": nome,
        "email": (email or "").strip(),
        "telefone": (telefone or "").strip(),
    }
    regs.append(u)
    _guardar_utilizadores(regs)
    return u


def obter_utilizador(utilizador_id):
    """Obtém um utilizador pelo seu identificador.

    Args:
        utilizador_id (int): Identificador do utilizador.

    Returns:
        dict | None: O dicionário do utilizador se existir; caso contrário
        `None`.
    """
    for u in carregar_utilizadores():
        if u["id"] == utilizador_id:
            return u
    return None


def atualizar_contactos(utilizador_id, email, telefone):
    """Atualiza e persiste os contactos (e-mail e telefone) de um utilizador.

    Os valores são normalizados com `strip()`. O chamador pode passar string
    vazia para remover um contacto.

    Args:
        utilizador_id (int): Identificador do utilizador.
        email (str): Novo e-mail (ou vazio para remover).
        telefone (str): Novo telefone (ou vazio para remover).

    Returns:
        tuple[bool, str]:
            - `True` e mensagem de sucesso se o utilizador existir.
            - `False` e mensagem de erro se não existir.
    """
    email = (email or "").strip()
    telefone = (telefone or "").strip()
    regs = carregar_utilizadores()
    for u in regs:
        if u["id"] == utilizador_id:
            u["email"] = email
            u["telefone"] = telefone
            _guardar_utilizadores(regs)
            return True, "E-mail e telemóvel atualizados com sucesso."
    return False, "Utilizador não encontrado."


def listar_indice_formatado():
    """Lista simples (id + nome) para mostrar na consola.

    Returns:
        str: Texto formatado com um utilizador por linha.
    """
    regs = carregar_utilizadores()
    if not regs:
        return "(Ainda não existem utilizadores registados.)"
    linhas = [f"  [{u['id']}] {u['nome']}" for u in regs]
    return "\n".join(linhas)


def ficha_formatada(utilizador_id):
    """Gera uma 'ficha' de utilizador com contactos e resumo de requisições.

    Esta função agrega informação de `modulo_requisicoes` para apresentar um
    resumo de requisições ativas e histórico.

    Args:
        utilizador_id (int): Identificador do utilizador.

    Returns:
        str: Texto pronto a imprimir na consola.
    """
    u = obter_utilizador(utilizador_id)
    if u is None:
        return "Utilizador não encontrado."

    import modulo_requisicoes

    resumo = modulo_requisicoes.resumo_requisicoes_utilizador(utilizador_id)

    linhas = [
        f"  Id: {u['id']}",
        f"  Nome: {u['nome']}",
        f"  E-mail: {u['email'] or '—'}",
        f"  Telefone: {u['telefone'] or '—'}",
        "",
        "  Requisições:",
        resumo,
    ]
    return "\n".join(linhas)
