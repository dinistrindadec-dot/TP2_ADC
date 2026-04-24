import json
from pathlib import Path

_DADOS = Path(__file__).resolve().parent.parent / "data" / "utilizadores.json"


def _garantir_ficheiro():
    _DADOS.parent.mkdir(parents=True, exist_ok=True)
    if not _DADOS.exists():
        _DADOS.write_text("[]", encoding="utf-8")


def carregar_utilizadores():

    _garantir_ficheiro()
    return json.loads(_DADOS.read_text(encoding="utf-8"))


def _guardar_utilizadores(regs):
    _DADOS.write_text(json.dumps(regs, ensure_ascii=False, indent=2), encoding="utf-8")


def _proximo_id(regs):
    if not regs:
        return 1
    return max(u["id"] for u in regs) + 1


def adicionar_utilizador(nome, email="", telefone=""):

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

    for u in carregar_utilizadores():
        if u["id"] == utilizador_id:
            return u
    return None


def listar_indice_formatado():

    regs = carregar_utilizadores()
    if not regs:
        return "(Ainda não existem utilizadores registados.)"
    linhas = [f"  [{u['id']}] {u['nome']}" for u in regs]
    return "\n".join(linhas)


def ficha_formatada(utilizador_id):

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
