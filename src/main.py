"""
Aplicação de consola — Catálogo e requisições da biblioteca.

Menu principal inspirado na organização modular do projeto de referência
(`prof`): funções de menu, entrada do utilizador e chamadas aos módulos
`modulo_catalogo` e `modulo_requisicoes`.

:Autor: TP2 — Biblioteca
"""

import sys
from pathlib import Path

# Permite `python main.py` a partir de `src/` ou `python src/main.py` a partir da raiz TP2
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import modulo_catalogo
import modulo_requisicoes


def menu_principal():
    while True:
        print("\n--- Biblioteca ---")
        print("1. Consultar catálogo")
        print("2. Área de administrador")
        print("3. Sair")
        opcao = input("Opção: ").strip()
        if opcao in ("1", "2", "3"):
            return int(opcao)
        print("Opção inválida.")


def menu_admin():
    while True:
        print("\n--- Administrador ---")
        print("1. Criar livro (atualizar catálogo)")
        print("2. Ver livros requisitados (requisições ativas)")
        print("3. Voltar ao menu principal")
        opcao = input("Opção: ").strip()
        if opcao in ("1", "2", "3"):
            return int(opcao)
        print("Opção inválida.")


def consultar_catalogo():
    livros = modulo_catalogo.listar_livros()
    if not livros:
        print("O catálogo está vazio.")
        return
    print("\nCatálogo:")
    for livro in livros:
        disp = modulo_requisicoes.exemplares_disponiveis(livro)
        print(
            f"  [{livro['id']}] {livro['titulo']} — {livro['autor']} | "
            f"Exemplares: {livro['exemplares']} | Disponíveis: {disp}"
        )


def admin_criar_livro():
    titulo = input("Título: ").strip()
    if not titulo:
        print("Título obrigatório.")
        return
    autor = input("Autor: ").strip()
    if not autor:
        print("Autor obrigatório.")
        return
    raw = input("Número de exemplares: ").strip()
    try:
        exemplares = int(raw)
    except ValueError:
        print("Introduza um número inteiro válido.")
        return
    if exemplares < 0:
        print("O número de exemplares não pode ser negativo.")
        return
    livro = modulo_catalogo.criar_livro(titulo, autor, exemplares)
    print(f"Livro criado com id {livro['id']}. Catálogo atualizado.")


def admin_ver_requisicoes():
    linhas = modulo_requisicoes.listar_requisicoes_ativas_para_admin(
        modulo_catalogo.obter_livro
    )
    if not linhas:
        print("Não há requisições ativas.")
        return
    print("\nRequisições ativas (para avaliar se outros podem requisitar):")
    for linha in linhas:
        print(linha)


def main():
    while True:
        op = menu_principal()
        if op == 1:
            consultar_catalogo()
        elif op == 2:
            while True:
                oa = menu_admin()
                if oa == 1:
                    admin_criar_livro()
                elif oa == 2:
                    admin_ver_requisicoes()
                else:
                    break
        else:
            break


if __name__ == "__main__":
    main()
