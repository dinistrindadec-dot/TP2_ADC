"""
Aplicação de gestão de biblioteca (catálogo e requisições)
---------------------------------------------------------

Programa principal com menus interativos para o administrador
(criar livros, ver requisições) e para leitores (consultar catálogo,
requisitar e devolver).

Os módulos ``modulo_catalogo`` e ``modulo_requisicoes`` concentram a lógica
de negócio e a persistência em ficheiros JSON.

:Autor: TP2 ADC
:Versão: 1.0
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import modulo_catalogo
import modulo_requisicoes


def menu_principal():
    """
    Menu inicial: escolha do perfil.

    :rtype: int
    """
    while True:
        print("\n--- Biblioteca ---")
        print("1. Administrador")
        print("2. Leitor")
        print("3. Sair")
        op = input("Opção: ").strip()
        if op in ("1", "2", "3"):
            return int(op)
        print("Opção inválida.")


def menu_admin():
    """
    Menu do administrador.

    :rtype: int
    """
    while True:
        print("\n--- Administrador ---")
        print("1. Criar livro (atualizar catálogo)")
        print("2. Ver livros requisitados (requisições ativas)")
        print("3. Consultar catálogo completo")
        print("4. Voltar")
        op = input("Opção: ").strip()
        if op in ("1", "2", "3", "4"):
            return int(op)
        print("Opção inválida.")


def menu_leitor():
    """
    Menu do leitor.

    :rtype: int
    """
    while True:
        print("\n--- Leitor ---")
        print("1. Consultar catálogo")
        print("2. Requisitar livro")
        print("3. Devolver livro")
        print("4. Voltar")
        op = input("Opção: ").strip()
        if op in ("1", "2", "3", "4"):
            return int(op)
        print("Opção inválida.")


def _pedir_inteiro_positivo(mensagem):
    while True:
        try:
            v = int(input(mensagem).strip())
            if v >= 1:
                return v
        except ValueError:
            pass
        print("Introduza um número inteiro >= 1.")


def fluxo_admin_criar_livro():
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()
    if not titulo or not autor:
        print("Título e autor são obrigatórios.")
        return
    exemplares = _pedir_inteiro_positivo("Número de exemplares: ")
    livro = modulo_catalogo.adicionar_livro(titulo, autor, exemplares)
    print(f"Livro criado com id {livro['id']}. Catálogo atualizado.")


def fluxo_admin_ver_requisitados():
    print("\nRequisições atuais (exemplares em requisição):")
    print(modulo_requisicoes.listar_requisitadas_admin())


def fluxo_admin_catalogo():
    print("\nCatálogo:")
    print(modulo_catalogo.listar_catalogo_formatado())


def fluxo_leitor_catalogo():
    fluxo_admin_catalogo()


def fluxo_leitor_requisitar():
    print("\nCatálogo:")
    print(modulo_catalogo.listar_catalogo_formatado())
    try:
        lid = int(input("Id do livro a requisitar: ").strip())
    except ValueError:
        print("Id inválido.")
        return
    nome = input("O seu nome: ").strip()
    if not nome:
        print("Nome é obrigatório.")
        return
    ok, msg, _ = modulo_requisicoes.requisitar(lid, nome)
    print(msg)


def fluxo_leitor_devolver():
    nome = input("O seu nome (como na requisição): ").strip()
    if not nome:
        return
    print("\nAs suas requisições ativas:")
    print(modulo_requisicoes.listar_por_requisitante(nome))
    try:
        rid = int(input("Número da requisição a devolver (#id): ").strip())
    except ValueError:
        print("Valor inválido.")
        return
    regs = modulo_requisicoes.carregar_requisicoes()
    reg = next((x for x in regs if x["id"] == rid), None)
    if reg is None or reg["requisitante"].strip().lower() != nome.strip().lower():
        print("Essa requisição não existe ou não está associada ao nome indicado.")
        return
    ok, msg = modulo_requisicoes.devolver(rid)
    print(msg)


def painel_admin():
    while True:
        op = menu_admin()
        if op == 1:
            fluxo_admin_criar_livro()
        elif op == 2:
            fluxo_admin_ver_requisitados()
        elif op == 3:
            fluxo_admin_catalogo()
        else:
            break


def painel_leitor():
    while True:
        op = menu_leitor()
        if op == 1:
            fluxo_leitor_catalogo()
        elif op == 2:
            fluxo_leitor_requisitar()
        elif op == 3:
            fluxo_leitor_devolver()
        else:
            break


def main():
    """
    Ponto de entrada: ciclo de menus até sair.

    :rtype: None
    """
    while True:
        op = menu_principal()
        if op == 1:
            painel_admin()
        elif op == 2:
            painel_leitor()
        else:
            print("Até breve.")
            break


if __name__ == "__main__":
    main()
