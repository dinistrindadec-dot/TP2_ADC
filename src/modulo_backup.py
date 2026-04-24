import shutil
from datetime import datetime
from pathlib import Path

_DADOS = Path(__file__).resolve().parent.parent / "data"
_FICHEIROS = ("livros.json", "requisicoes.json", "utilizadores.json")
_BACKUPS = _DADOS / "backups"


def criar_backup():

    _DADOS.mkdir(parents=True, exist_ok=True)
    _BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    pasta = _BACKUPS / f"backup_{stamp}"
    pasta.mkdir(parents=False, exist_ok=False)
    copiados = []
    for nome in _FICHEIROS:
        origem = _DADOS / nome
        if origem.is_file():
            shutil.copy2(origem, pasta / nome)
            copiados.append(nome)
    if not copiados:
        pasta.rmdir()
        return None, copiados
    return pasta, copiados
