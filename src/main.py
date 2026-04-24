import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import modulo_catalogo
import modulo_requisicoes


def menu_principal():

    while True:
        print("\n--- Biblioteca ---")
        print("1. Consultar catálogo")
        print("2. Requisitar um livro")
        print("3. Área de administrador")
        print("4. Sair")
        opcao = input("Opção: ").strip()
        if opcao in ("1", "2", "3", "4"):
            return int(opcao)
        print("Opção inválida.\n")


def menu_admin():

    while True:
        print("\n--- Administrador ---")
        print("1. Adicionar livro ao catálogo")
        print("2. Ver livros requisitados (requisições ativas)")
        print("3. Registar devolução de um exemplar")
        print("4. Voltar ao menu principal")
        opcao = input("Opção: ").strip()
        if opcao in ("1", "2", "3", "4"):
            return int(opcao)
        print("Opção inválida.\n")


def _autenticar_admin():

    chave = input("Palavra-passe de administrador: ").strip()
    if chave != "admin":
        print("Acesso negado.")
        return False
    return True


def _pedir_inteiro_positivo(mensagem):
    while True:
        try:
            n = int(input(mensagem).strip())
            if n > 0:
                return n
        except ValueError:
            pass
        print("Introduza um número inteiro positivo.")


def main():
    while True:
        op = menu_principal()

        if op == 1:
            print("\nCatálogo:")
            print(modulo_catalogo.formatar_catalogo_para_consulta())

        elif op == 2:
            print("\nCatálogo:")
            print(modulo_catalogo.formatar_catalogo_para_consulta())
            try:
                lid = int(input("Id do livro a requisitar: ").strip())
            except ValueError:
                print("Id inválido.")
                continue
            nome = input("O seu nome: ").strip()
            if not nome:
                print("O nome é obrigatório.")
                continue
            print(modulo_requisicoes.requisitar_livro(lid, nome))

        elif op == 3:
            if not _autenticar_admin():
                continue
            while True:
                oa = menu_admin()
                if oa == 1:
                    titulo = input("Título: ").strip()
                    autor = input("Autor: ").strip()
                    if not titulo or not autor:
                        print("Título e autor são obrigatórios.")
                        continue
                    ex = _pedir_inteiro_positivo("Número de exemplares: ")
                    livro = modulo_catalogo.criar_livro(titulo, autor, ex)
                    print(
                        f"Livro criado: id {livro['id']}, «{livro['titulo']}», "
                        f"{livro['exemplares']} exemplar(es). Catálogo atualizado."
                    )
                elif oa == 2:
                    print("\nRequisições ativas:")
                    print(modulo_requisicoes.listar_requisicoes_ativas())
                elif oa == 3:
                    try:
                        rid = int(input("Id da requisição a encerrar (devolução): ").strip())
                    except ValueError:
                        print("Id inválido.")
                        continue
                    print(modulo_requisicoes.devolver_livro(rid))
                else:
                    break

        else:
            break


if __name__ == "__main__":
    main()