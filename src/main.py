"""
Aplicação de gestão de biblioteca (catálogo e requisições)
---------------------------------------------------------

Programa principal com menus interativos para o administrador
(criar livros, ver requisições) e para leitores (consultar catálogo,
requisitar e devolver).

Os módulos ``modulo_catalogo``, ``modulo_requisicoes``, ``modulo_utilizadores``
e ``modulo_backup`` concentram a lógica de negócio e a persistência em ficheiros JSON.

:Autor: TP2 ADC
:Versão: 1.0
"""

import sys
from pathlib import Path

# Garante que `src/` está no `sys.path` quando o programa é executado
# diretamente, permitindo `import modulo_*` sem instalar o projeto como pacote.
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import modulo_backup
import modulo_catalogo
import modulo_requisicoes
import modulo_utilizadores


def menu_principal():
    """
    Menu inicial: escolha do perfil.

    O ciclo repete até receber uma opção válida.

    Returns:
        int: 1 (administrador), 2 (leitor) ou 3 (sair).
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

    Returns:
    int: Opção selecionada (1..8).
    """
    while True:
        print("\n--- Administrador ---")
        print("1. Criar livro (atualizar catálogo)")
        print("2. Ver livros requisitados (requisições ativas)")
        print("3. Consultar catálogo completo")
        print("4. Registar utilizador")
        print("5. Fichas de utilizadores")
        print("6. Stock dos livros (ver / alterar quantidade)")
        print("7. Criar backup dos dados (cópia de segurança)")
        print("8. Voltar")
        op = input("Opção: ").strip()
        if op in ("1", "2", "3", "4", "5", "6", "7", "8"):
            return int(op)
        print("Opção inválida.")


def menu_leitor():
    """
    Menu do leitor.

    Returns:
        int: Opção selecionada (1..7).
    """
    while True:
        print("\n--- Leitor ---")
        print("1. Consultar catálogo (disponível / emprestado)")
        print("2. Requisitar livro")
        print("3. Devolver livro")
        print("4. Prazos das minhas requisições (tempo até devolução)")
        print("5. Pesquisar livros (por autor ou por tema)")
        print("6. Atualizar e-mail ou telemóvel (contactos)")
        print("7. Voltar")
        op = input("Opção: ").strip()
        if op in ("1", "2", "3", "4", "5", "6", "7"):
            return int(op)
        print("Opção inválida.")


def _pedir_inteiro_positivo(mensagem):
    """Pede um inteiro ao utilizador e valida que é >= 1.

    Args:
        mensagem (str): Texto a apresentar no `input()`.

    Returns:
        int: Inteiro validado (>= 1).
    """
    while True:
        try:
            v = int(input(mensagem).strip())
            if v >= 1:
                return v
        except ValueError:
            pass
        print("Introduza um número inteiro >= 1.")


def _pedir_inteiro_minimo(mensagem, minimo):
    """Pede um inteiro ao utilizador e valida que é >= `minimo`.

    Args:
        mensagem (str): Texto a apresentar no `input()`.
        minimo (int): Valor mínimo aceite.

    Returns:
        int: Inteiro validado (>= `minimo`).
    """
    while True:
        try:
            v = int(input(mensagem).strip())
            if v >= minimo:
                return v
        except ValueError:
            pass
        print(f"Introduza um número inteiro >= {minimo}.")


def fluxo_admin_criar_livro():
    """Fluxo do administrador: registo de um novo livro no catálogo.

    Solicita título/autor (obrigatórios), número de exemplares (>= 1) e um tema
    opcional para permitir pesquisa.

    Returns:
        None
    """
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()
    if not titulo or not autor:
        print("Título e autor são obrigatórios.")
        return
    exemplares = _pedir_inteiro_positivo("Número de exemplares: ")
    tema = input("Tema / género (opcional, para pesquisa): ").strip()
    livro = modulo_catalogo.adicionar_livro(titulo, autor, exemplares, tema)
    print(f"Livro criado com id {livro['id']}. Catálogo atualizado.")


def fluxo_admin_ver_requisitados():
    """Fluxo do administrador: listagem de requisições ativas.

    Returns:
        None
    """
    print("\nRequisições atuais (exemplares em requisição):")
    print(modulo_requisicoes.listar_requisitadas_admin())


def fluxo_admin_catalogo():
    """Fluxo do administrador: listagem do catálogo completo.

    Returns:
        None
    """
    print("\nCatálogo:")
    print(modulo_catalogo.listar_catalogo_formatado())


def fluxo_admin_registar_utilizador():
    """Fluxo do administrador: registo de um novo utilizador.

    O nome é obrigatório. E-mail e telefone são opcionais.

    Returns:
        None
    """
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
    """Fluxo do administrador: consulta da ficha de um utilizador.

    Mostra o índice de utilizadores e pede o `id` para apresentar a ficha
    detalhada (incluindo resumo de requisições).

    Returns:
        None
    """
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
    """Fluxo do administrador: gestão de stock (nº exemplares por livro).

    Este fluxo consulta o stock atual e permite alterar o número total de
    exemplares de um livro. Antes de alterar, valida que o novo stock não fica
    abaixo do número de exemplares atualmente requisitados.

    Returns:
        None
    """
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
        
        # `em_uso` define o mínimo permitido: não podemos ter menos stock do que
        # exemplares já emprestados.
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
    """Fluxo do leitor: consulta do catálogo com disponibilidade.

    Returns:
        None
    """
    print("\nCatálogo com disponibilidade para requisição:")
    print(modulo_requisicoes.catalogo_disponibilidade_formatado())


def fluxo_leitor_requisitar():
    """Fluxo do leitor: criação de uma requisição de livro.

    O leitor escolhe o seu `id` de utilizador e depois seleciona o livro a
    requisitar. A criação e validações são delegadas a `modulo_requisicoes`.

    Returns:
        None
    """
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
    """Fluxo do leitor: devolução de um livro (encerra uma requisição).

    Mostra as requisições ativas do utilizador e pede o `#id` da requisição
    para efetuar a devolução.

    Returns:
        None
    """
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
    """Fluxo do leitor: consulta dos prazos das requisições ativas.

    Returns:
        None
    """
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


def fluxo_leitor_pesquisar():
    """Fluxo do leitor: pesquisa de livros por autor ou tema.

    A pesquisa é feita no catálogo e, em seguida, os resultados são formatados
    com disponibilidade (usando as requisições ativas).

    Returns:
        None
    """
    print("\nPesquisa (texto parcial, ignora maiúsculas):")
    print("1. Por autor")
    print("2. Por tema")
    op = input("Opção: ").strip()
    termo = input("Texto a procurar: ").strip()
    if not termo:
        print("Indique um termo de pesquisa.")
        return
    if op == "1":
        livros = modulo_catalogo.pesquisar_por_autor(termo)
    elif op == "2":
        livros = modulo_catalogo.pesquisar_por_tema(termo)
    else:
        print("Opção inválida.")
        return
    print("\nResultados:")
    print(modulo_requisicoes.formatar_livros_com_disponibilidade(livros))


def _pedir_novo_contacto(rotulo, valor_atual):
    """Pede ao utilizador um novo valor para um campo de contacto.

    Regras:
    - Enter mantém o valor atual.
    - `-` apaga o valor.
    - Qualquer outro texto substitui o valor.

    Args:
        rotulo (str): Nome a apresentar (ex.: "E-mail").
        valor_atual (str): Valor atual do campo.

    Returns:
        str: Novo valor (pode ser vazio para representar remoção).
    """
    atual_txt = valor_atual if valor_atual else "—"
    print(f"{rotulo} atual: {atual_txt}")
    print("(Enter para manter, '-' para apagar, ou escreva o novo valor)")
    linha = input(f"Novo {rotulo.lower()}: ").strip()
    if linha == "":
        return valor_atual
    if linha == "-":
        return ""
    return linha


def fluxo_leitor_contactos():
    """Fluxo do leitor: atualização de contactos (e-mail e telemóvel).

    Returns:
        None
    """
    print("\nUtilizadores registados:")
    print(modulo_utilizadores.listar_indice_formatado())
    try:
        uid = int(input("O seu id de utilizador: ").strip())
    except ValueError:
        print("Id inválido.")
        return
    u = modulo_utilizadores.obter_utilizador(uid)
    if u is None:
        print("Utilizador não encontrado.")
        return
    email = _pedir_novo_contacto("E-mail", u.get("email", ""))
    telefone = _pedir_novo_contacto("Telemóvel", u.get("telefone", ""))
    if email == u.get("email", "") and telefone == u.get("telefone", ""):
        print("Nenhuma alteração.")
        return
    ok, msg = modulo_utilizadores.atualizar_contactos(uid, email, telefone)
    print(msg)


def fluxo_admin_backup():
    """Fluxo do administrador: criação de backup dos ficheiros de dados.

    Returns:
        None
    """
    try:
        pasta, ficheiros = modulo_backup.criar_backup()
    except OSError as e:
        print(f"Não foi possível criar o backup: {e}")
        return
    if not ficheiros:
        print(
            "Não foi copiado nenhum ficheiro (ainda não existem dados em "
            "livros.json, requisicoes.json ou utilizadores.json)."
        )
        return
    print(f"Backup criado com sucesso em:\n  {pasta}")
    print(f"Ficheiros copiados: {', '.join(ficheiros)}")


def painel_admin():
    """Loop principal do painel do administrador.

    Executa o menu e despacha para o fluxo correspondente, até o utilizador
    escolher "Voltar".

    Returns:
        None
    """
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
        elif op == 7:
            fluxo_admin_backup()
        else:
            break


def painel_leitor():
    """Loop principal do painel do leitor.

    Executa o menu e despacha para o fluxo correspondente, até o utilizador
    escolher "Voltar".

    Returns:
        None
    """
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
        elif op == 5:
            fluxo_leitor_pesquisar()
        elif op == 6:
            fluxo_leitor_contactos()
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
