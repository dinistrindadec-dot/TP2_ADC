"""Cópias de segurança (backup) dos ficheiros de dados.

Este módulo cria uma cópia de segurança dos ficheiros JSON usados pela
aplicação (catálogo, requisições e utilizadores).

A estratégia é simples:
- Cria (se necessário) a pasta `data/`.
- Cria (se necessário) a pasta `data/backups/`.
- Para cada ficheiro esperado, se existir, copia-o para uma nova subpasta
  `backup_<timestamp>/`.
- Se nenhum ficheiro existir, remove a pasta de backup criada e devolve
  `(None, [])`.
"""
import shutil
from datetime import datetime
from pathlib import Path

# Pasta de dados do projeto (onde vivem os ficheiros JSON).
_DADOS = Path(__file__).resolve().parent.parent / "data"

# Lista de ficheiros que compõem o estado da aplicação.
_FICHEIROS = ("livros.json", "requisicoes.json", "utilizadores.json")

# Pasta onde são guardadas as cópias de segurança.
_BACKUPS = _DADOS / "backups"


def criar_backup():
    """Cria um backup dos ficheiros de dados existentes.

    Returns:
        tuple[Path | None, list[str]]:
            - Caminho para a pasta de backup criada (ou `None` se não foi
              copiado nenhum ficheiro).
            - Lista de nomes de ficheiros copiados.

    Raises:
        OSError: Se houver falhas de IO ao criar pastas ou copiar ficheiros.
    """
    # Garante que a estrutura de pastas existe.
    _DADOS.mkdir(parents=True, exist_ok=True)
    _BACKUPS.mkdir(parents=True, exist_ok=True)
    
    # Timestamp com microssegundos para evitar colisões entre backups.
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
         # Se nada foi copiado, o backup não é útil: remove a pasta criada.
        pasta.rmdir()
        return None, copiados
    return pasta, copiados
