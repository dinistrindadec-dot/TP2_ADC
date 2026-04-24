"""
Aplicação de gestão de biblioteca (catálogo e requisições)
---------------------------------------------------------

Programa principal com menus interativos para o administrador
(criar livros, ver requisições) e para leitores (consultar catálogo,
requisitar e devolver).

Os módulos ``modulo_catalogo``, ``modulo_requisicoes`` e ``modulo_utilizadores``
concentram a lógica de negócio e a persistência em ficheiros JSON.

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
import modulo_utilizadores


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
        print("4. Registar utilizador")
        print("5. Fichas de utilizadores")
        print("6. Stock dos livros (ver / alterar quantidade)")
        print("7. Voltar")
        op = input("Opção: ").strip()
        if op in ("1", "2", "3", "4", "5", "6", "7"):
            return int(op)
        print("Opção inválida.")


def menu_leitor():
    """
    Menu do leitor.

    :rtype: int
    """
    while True:
        print("\n--- Leitor ---")
        print("1. Consultar catálogo (disponível / emprestado)")
        print("2. Requisitar livro")
        print("3. Devolver livro")
        print("4. Prazos das minhas requisições (tempo até devolução)")
        print("5. Voltar")
        op = input("Opção: ").strip()
        if op in ("1", "2", "3", "4", "5"):
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


def _pedir_inteiro_minimo(mensagem, minimo):
    while True:
        try:
            v = int(input(mensagem).strip())
            if v >= minimo:
                return v
        except ValueError:
            pass
        print(f"Introduza um número inteiro >= {minimo}.")


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


def fluxo_admin_registar_utilizador():
    nome = input("Nome completo: ").strip()
    if not nome:
        print("O nome é obrigatório.")
        return
    email = input("E-mail (opcional): ").strip()
    telefone = input("Telefone (opcional): ").strip()
    try:
        u = modulo_utilizadores.adicionar_utilizador(nome, email, telefone)
        print(f"Utilizador registado com id {u['id']}.")
    except ValueError as e:
        print(str(e))


def fluxo_admin_fichas():
    print("\nUtilizadores:")
    print(modulo_utilizadores.listar_indice_formatado())
    try:
        uid = int(input("Id do utilizador para ver a ficha: ").strip())
    except ValueError:
        print("Id inválido.")
        return
    print()
    print(modulo_utilizadores.ficha_formatada(uid))


def fluxo_admin_stock():
    while True:
        print("\nStock por livro (total | em requisição | disponível):")
        print(modulo_requisicoes.listar_stock_por_livro_formatado())
        print("1. Alterar stock (número de exemplares) de um livro")
        print("2. Voltar")
        op = input("Opção: ").strip()
        if op == "2":
            break
        if op != "1":
            print("Opção inválida.")
            continue
        try:
            lid = int(input("Id do livro: ").strip())
        except ValueError:
            print("Id inválido.")
            continue
        if modulo_catalogo.obter_livro(lid) is None:
            print("Livro não encontrado.")
            continue
        em_uso = modulo_requisicoes.contar_requisicoes_ativas_por_livro(lid)
        minimo = max(1, em_uso)
        print(
            f"Novo total de exemplares (não pode ser inferior a {minimo}, "
            f"porque {em_uso} estão em requisição)."
        )
        novo = _pedir_inteiro_minimo("Novo stock total: ", minimo)
        ok, msg = modulo_catalogo.atualizar_exemplares(lid, novo)
        print(msg)


def fluxo_leitor_catalogo():
    print("\nCatálogo com disponibilidade para requisição:")
    print(modulo_requisicoes.catalogo_disponibilidade_formatado())


def fluxo_leitor_requisitar():
    print("\nUtilizadores registados:")
    print(modulo_utilizadores.listar_indice_formatado())
    try:
        uid = int(input("O seu id de utilizador: ").strip())
    except ValueError:
        print("Id inválido.")
        return
    if modulo_utilizadores.obter_utilizador(uid) is None:
        print("Utilizador não encontrado.")
        return
    print("\nDisponibilidade:")
    print(modulo_requisicoes.catalogo_disponibilidade_formatado())
    try:
        lid = int(input("Id do livro a requisitar: ").strip())
    except ValueError:
        print("Id inválido.")
        return
    ok, msg, _ = modulo_requisicoes.requisitar(lid, uid)
    print(msg)


def fluxo_leitor_devolver():
    print("\nUtilizadores registados:")
    print(modulo_utilizadores.listar_indice_formatado())
    try:
        uid = int(input("O seu id de utilizador: ").strip())
    except ValueError:
        print("Id inválido.")
        return
    if modulo_utilizadores.obter_utilizador(uid) is None:
        print("Utilizador não encontrado.")
        return
    print("\nAs suas requisições ativas:")
    print(modulo_requisicoes.listar_por_utilizador(uid))
    try:
        rid = int(input("Número da requisição a devolver (#id): ").strip())
    except ValueError:
        print("Valor inválido.")
        return
    regs = modulo_requisicoes.carregar_requisicoes()
    reg = next((x for x in regs if x["id"] == rid), None)
    if reg is None or not modulo_requisicoes.requisicao_pertence_a_utilizador(reg, uid):
        print("Essa requisição não existe ou não pertence a este utilizador.")
        return
    ok, msg = modulo_requisicoes.devolver(rid)
    print(msg)


def fluxo_leitor_prazos():
    print("\nUtilizadores registados:")
    print(modulo_utilizadores.listar_indice_formatado())
    try:
        uid = int(input("O seu id de utilizador: ").strip())
    except ValueError:
        print("Id inválido.")
        return
    if modulo_utilizadores.obter_utilizador(uid) is None:
        print("Utilizador não encontrado.")
        return
    print("\nAs suas requisições ativas e tempo até à devolução:")
    print(modulo_requisicoes.prazos_minhas_requisicoes_formatado(uid))


def painel_admin():
    while True:
        op = menu_admin()
        if op == 1:
            fluxo_admin_criar_livro()
        elif op == 2:
            fluxo_admin_ver_requisitados()
        elif op == 3:
            fluxo_admin_catalogo()
        elif op == 4:
            fluxo_admin_registar_utilizador()
        elif op == 5:
            fluxo_admin_fichas()
        elif op == 6:
            fluxo_admin_stock()
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
        elif op == 4:
            fluxo_leitor_prazos()
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
