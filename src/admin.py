#!/usr/bin/env python3
"""
CLI administrativo do banco da caixinha
=======================================

Use via ``make admin`` (dentro do container) ou:
    python -m src.admin
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

try:  # python -m src.admin
    from . import config
    from .utils import db
except ImportError:  # python admin.py (com src/ no sys.path)
    import config  # type: ignore
    from utils import db  # type: ignore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _mes_fmt(mes: str) -> str:
    try:
        return datetime.strptime(mes, "%Y-%m").strftime("%m/%Y")
    except (TypeError, ValueError):
        return mes


def _tg(valor: Any) -> str:
    return str(valor) if valor is not None else "—"


def _ra(valor: Any) -> str:
    return str(valor) if valor else "—"


def _texto(valor: Any, padrao: str = "—") -> str:
    return str(valor) if valor else padrao


def _pausa() -> None:
    try:
        input("\nPressione Enter para continuar...")
    except (KeyboardInterrupt, EOFError):
        pass


def _selecionar_membro(
    membros: List[sqlite3.Row], titulo: str = "Escolha o membro"
) -> Optional[sqlite3.Row]:
    """Lista membros numerados e devolve o escolhido (ou None)."""
    if not membros:
        print("❌ Nenhum membro encontrado.")
        return None

    print()
    for i, membro in enumerate(membros, 1):
        tipo = "EX" if int(membro["ex_bolsista"]) else "ATIVO"
        print(
            f"{i:2d}. [{tipo:5s}] id={membro['id']:<3d} "
            f"{membro['nome'][:38]:38s} RA {_ra(membro['ra']):8s} "
            f"TG {_tg(membro['telegram_id'])}"
        )

    escolha = input(f"\n{titulo} (número ou id, Enter cancela): ").strip()
    if not escolha:
        print("Operação cancelada.")
        return None

    if escolha.isdigit():
        numero = int(escolha)
        if 1 <= numero <= len(membros):
            return membros[numero - 1]
        for membro in membros:
            if int(membro["id"]) == numero:
                return membro

    print("❌ Opção inválida.")
    return None


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------


def mostrar_menu() -> None:
    print("\n🗃️  Gerenciador do Banco da Caixinha")
    print("=" * 46)
    print("1. Ver todos os membros")
    print("2. Ver bolsistas ativos")
    print("3. Ver ex-bolsistas (histórico)")
    print("4. Adicionar novo membro")
    print("5. Ver dívidas de um membro")
    print("6. Ver status/resumo do mês atual")
    print("7. Criar cobrança para o mês atual")
    print("8. Adicionar dívida manual")
    print("9. Aprovar/rejeitar pagamentos em auditoria")
    print("10. Vincular Telegram ID a membro legado")
    print("11. Backup do banco de dados")
    print("0. Sair")
    print("=" * 46)
    print(f"💰 Cota mensal: {_brl(config.VALOR_CONTRIBUICAO)}")


# ---------------------------------------------------------------------------
# Ações
# ---------------------------------------------------------------------------


def ver_membros(ex_bolsista: Optional[bool] = None) -> None:
    membros = db.listar_membros_detalhado(ex_bolsista=ex_bolsista)
    rotulo = (
        "todos os membros"
        if ex_bolsista is None
        else ("ex-bolsistas" if ex_bolsista else "bolsistas ativos")
    )

    if not membros:
        print(f"❌ Nenhum registro em {rotulo}.")
        return

    print(f"\n👥 {rotulo.capitalize()} ({len(membros)}):")
    print("-" * 110)
    print(
        f"{'ID':>4} | {'TIPO':6} | {'NOME':38} | {'RA':8} | "
        f"{'STATUS':28} | TELEGRAM"
    )
    print("-" * 110)
    for m in membros:
        tipo = "EX" if int(m["ex_bolsista"]) else "ATIVO"
        print(
            f"{int(m['id']):4d} | {tipo:6} | {m['nome'][:38]:38} | "
            f"{_ra(m['ra']):8} | {_texto(m['status_vinculo'])[:28]:28} | "
            f"{_tg(m['telegram_id'])}"
        )
    print("-" * 110)

    sem_tg = sum(1 for m in membros if m["telegram_id"] is None)
    print(f"Sem Telegram vinculado: {sem_tg}/{len(membros)}")


def adicionar_membro() -> None:
    print("\n➕ Adicionar novo membro")
    nome = input("Nome do membro: ").strip()
    if not nome:
        print("❌ Nome não pode estar vazio.")
        return

    ra = input("RA (opcional): ").strip() or None
    telegram_txt = input("ID do Telegram (opcional, Enter pula): ").strip()
    telegram_id: Optional[int] = None
    if telegram_txt:
        try:
            telegram_id = int(telegram_txt)
        except ValueError:
            print("❌ ID do Telegram deve ser um número.")
            return

    ex_txt = input("É ex-bolsista? (s/N): ").strip().lower()
    ex_bolsista = ex_txt == "s"

    if db.adicionar_membro(
        nome=nome,
        telegram_id=telegram_id,
        ra=ra,
        ex_bolsista=ex_bolsista,
    ):
        print(f"✅ Membro {nome} adicionado com sucesso!")
    else:
        print("❌ Erro: Telegram ID ou RA já cadastrado.")


def ver_dividas_membro() -> None:
    membro = _selecionar_membro(
        db.listar_membros_detalhado(), "Membro para ver dívidas"
    )
    if membro is None:
        return

    dividas = db.buscar_dividas_por_membro_id(int(membro["id"]))
    em_auditoria = [
        (mes, valor)
        for mes, valor in db.buscar_dividas_por_membro_id(
            int(membro["id"]), incluir_em_auditoria=True
        )
        if (mes, valor) not in dividas
    ]

    print(f"\n💰 Pendências de {membro['nome']} (RA {_ra(membro['ra'])}):")
    print("-" * 50)

    if not dividas and not em_auditoria:
        print("✅ Sem pendências! Está em dia.")
        return

    if dividas:
        total = sum(valor for _, valor in dividas)
        print("⏳ Em aberto:")
        for mes, valor in dividas:
            print(f"  • {_mes_fmt(mes)}: {_brl(valor)}")
        print(f"  Total: {_brl(total)}")

    if em_auditoria:
        print("\n🔎 Aguardando auditoria:")
        for mes, valor in em_auditoria:
            print(f"  • {_mes_fmt(mes)}: {_brl(valor)}")


def ver_status_mes() -> None:
    mes = db.buscar_mes_atual()
    resumo = db.obter_resumo_mes(mes)
    status_mes = db.buscar_status_mes(mes)
    aguardando = db.listar_pagamentos_aguardando_auditoria()

    print(f"\n📊 Status - {_mes_fmt(mes)}")
    print("=" * 58)

    ativos = resumo["ativos"]
    ex = resumo["ex_bolsistas"]

    print(f"👥 Bolsistas ativos: {int(ativos['membros'])}")
    print(f"  ✅ Pagos: {int(ativos['pagos'])} ({_brl(ativos['valor_pago'])})")
    print(f"  ⏳ Pendentes: {int(ativos['pendentes'])}")
    print(f"  🔎 Em auditoria: {int(ativos['em_auditoria'])}")
    print(f"🎓 Ex-bolsistas: {int(ex['membros'])}")
    print(f"  ✅ Cotas pagas no mês: {int(ex['pagos'])} ({_brl(ex['valor_pago'])})")
    print(f"  ⏳ Pendentes no mês: {int(ex['pendentes'])}")

    if status_mes:
        print("\n" + "-" * 58)
        for row in status_mes:
            tipo = "EX" if int(row["ex_bolsista"]) else "AT"
            print(
                f"[{tipo}] {row['nome'][:42]:42} "
                f"{row['status_pagamento']:>22} {_brl(float(row['valor_pago']))}"
            )

    if aguardando:
        print("\n🕵️ Aguardando auditoria (todos os meses):")
        for row in aguardando:
            print(
                f"  • #{row['id']} {row['nome'][:35]:35} "
                f"{_mes_fmt(row['mes'])} {_brl(float(row['valor_pago']))}"
            )
    else:
        print("\n🕵️ Nenhum pagamento aguardando auditoria.")


def criar_cobranca_mes() -> None:
    mes = db.buscar_mes_atual()
    confirmacao = input(
        f"\nCriar cobranças de {_mes_fmt(mes)} apenas para ativos? (s/N): "
    ).strip().lower()
    if confirmacao != "s":
        print("❌ Operação cancelada.")
        return

    try:
        criadas = db.criar_cobranca_mensal(mes)
        print(f"✅ Criadas {criadas} cobranças para {_mes_fmt(mes)}.")
        print("   Ex-bolsistas não recebem novas cobranças (regra de negócio).")
    except ValueError as exc:
        print(f"❌ {exc}")


def adicionar_divida_manual() -> None:
    print("\n💰 Adicionar dívida manual")
    membro = _selecionar_membro(
        db.listar_membros_detalhado(), "Membro para adicionar dívida"
    )
    if membro is None:
        return

    mes = input("Mês da dívida (YYYY-MM, ex: 2024-12): ").strip()
    try:
        datetime.strptime(mes, "%Y-%m")
    except ValueError:
        print("❌ Formato de mês inválido. Use YYYY-MM")
        return

    try:
        valor = float(input("Valor da dívida (R$, ex: 5.0): ").strip())
        if valor <= 0:
            print("❌ Valor deve ser positivo.")
            return
    except ValueError:
        print("❌ Valor inválido.")
        return

    print("\n📋 Confirmar dados:")
    print(f"👤 Membro: {membro['nome']}")
    print(f"📅 Mês: {_mes_fmt(mes)}")
    print(f"💰 Valor: {_brl(valor)}")

    if input("\nConfirmar adição? (s/N): ").strip().lower() != "s":
        print("❌ Operação cancelada.")
        return

    if db.adicionar_divida_manual_membro(int(membro["id"]), mes, valor):
        print(f"✅ Dívida adicionada para {membro['nome']}!")
    else:
        print(f"❌ Já existe uma cobrança para {membro['nome']} em {_mes_fmt(mes)}.")


def aprovar_auditoria() -> None:
    print("\n🕵️ Pagamentos aguardando auditoria")
    pendentes = db.listar_pagamentos_aguardando_auditoria()

    if not pendentes:
        print("✅ Nenhuma solicitação pendente.")
        return

    for i, row in enumerate(pendentes, 1):
        tipo = "EX" if int(row["ex_bolsista"]) else "AT"
        print(
            f"{i:2d}. [{tipo}] #{row['id']} {row['nome'][:35]:35} "
            f"{_mes_fmt(row['mes'])} {_brl(float(row['valor_pago']))} "
            f"(solicitado em {_texto(row['data_pagamento'])})"
        )

    escolha = input("\nNúmero da solicitação (Enter cancela): ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(pendentes)):
        print("Operação cancelada.")
        return

    row = pendentes[int(escolha) - 1]
    print(f"\n👤 {row['nome']} | RA {_ra(row['ra'])}")
    print(f"📅 {_mes_fmt(row['mes'])} | 💰 {_brl(float(row['valor_pago']))}")
    print(f"📝 {_texto(row['observacoes'])}")

    acao = input("\n[A]provar, [R]ejeitar ou Enter cancelar: ").strip().lower()
    if acao not in {"a", "r"}:
        print("Operação cancelada.")
        return

    if acao == "a":
        observacao = input("Observação da aprovação (opcional): ").strip()
        ok = db.aprovar_pagamento(int(row["id"]), aprovado=True,
                                  observacao=observacao or None)
        print("✅ Pagamento aprovado e marcado como pago." if ok
              else "❌ Não foi possível aprovar.")
    else:
        motivo = input("Motivo da rejeição (opcional): ").strip()
        ok = db.aprovar_pagamento(
            int(row["id"]),
            aprovado=False,
            observacao=motivo or "Rejeitado no painel administrativo",
        )
        print("✅ Solicitação rejeitada e devolvida para pendente." if ok
              else "❌ Não foi possível rejeitar.")


def vincular_telegram_manual() -> None:
    print("\n🔗 Vincular Telegram a membro legado")
    sem_telegram = db.listar_membros_detalhado(apenas_sem_telegram=True)

    if not sem_telegram:
        print("✅ Todos os membros já têm Telegram vinculado (ou não há membros).")
        return

    membro = _selecionar_membro(sem_telegram, "Membro legado")
    if membro is None:
        return

    texto = input("ID numérico do Telegram: ").strip()
    try:
        telegram_id = int(texto)
    except ValueError:
        print("❌ ID do Telegram deve ser um número.")
        return

    print(f"\n👤 {membro['nome']} (RA {_ra(membro['ra'])})")
    print(f"🔗 Telegram: {telegram_id}")

    dono = db.buscar_membro_por_telegram_id(telegram_id)
    if dono is not None and int(dono["id"]) != int(membro["id"]):
        print(
            f"\n⚠️  Esse Telegram já pertence a {dono['nome']} "
            f"(id={dono['id']}, RA {_ra(dono['ra'])})."
        )
        print("   O vínculo vai MESCLAR os lançamentos e remover o cadastro antigo.")
        if input("Confirmar mesclagem? (s/N): ").strip().lower() != "s":
            print("❌ Operação cancelada.")
            return

    if input("Confirmar vínculo? (s/N): ").strip().lower() != "s":
        print("❌ Operação cancelada.")
        return

    if db.vincular_telegram_id(int(membro["id"]), telegram_id):
        print("✅ Vínculo realizado! Se havia um cadastro placeholder para esse "
              "Telegram, ele foi mesclado neste membro.")
    else:
        print("❌ Não foi possível vincular.")


def fazer_backup() -> None:
    origem = os.path.abspath(config.DB_PATH)
    if not os.path.exists(origem):
        print("❌ Banco de dados não encontrado.")
        return

    # Pasta "backup/" relativa ao diretório de execução do projeto.
    # No Docker isso resolve para /app/backup (volume montado).
    diretorio = os.path.abspath(os.path.join(os.getcwd(), "backup"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(diretorio, f"caixinha_backup_{timestamp}.db")
    try:
        os.makedirs(diretorio, exist_ok=True)
        # backup() inclui o WAL de forma consistente, mesmo com web/bot ativos.
        with sqlite3.connect(config.DB_PATH) as origem_conn:
            with sqlite3.connect(destino) as destino_conn:
                origem_conn.backup(destino_conn)
        print(f"✅ Backup criado: {destino}")
    except (OSError, sqlite3.Error) as exc:
        print(f"❌ Erro ao criar backup: {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    try:
        db.init_db()
    except sqlite3.Error as exc:
        print(f"❌ Erro ao inicializar o banco: {exc}")
        return

    acoes: Dict[str, Any] = {
        "1": lambda: ver_membros(None),
        "2": lambda: ver_membros(False),
        "3": lambda: ver_membros(True),
        "4": adicionar_membro,
        "5": ver_dividas_membro,
        "6": ver_status_mes,
        "7": criar_cobranca_mes,
        "8": adicionar_divida_manual,
        "9": aprovar_auditoria,
        "10": vincular_telegram_manual,
        "11": fazer_backup,
    }

    while True:
        mostrar_menu()
        try:
            opcao = input("\nEscolha uma opção (0-11): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Saindo...")
            break

        if opcao == "0":
            print("👋 Até mais!")
            break

        acao = acoes.get(opcao)
        if acao is None:
            print("❌ Opção inválida. Escolha entre 0 e 11.")
        else:
            try:
                acao()
            except sqlite3.Error as exc:
                print(f"❌ Erro de banco de dados: {exc}")
            except (KeyboardInterrupt, EOFError):
                print("\n⚠️  Operação cancelada.")

        _pausa()


if __name__ == "__main__":
    main()
