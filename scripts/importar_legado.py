#!/usr/bin/env python3
"""
Importação do histórico legado da caixinha da ITCP
==================================================

Lê:
    * cotizacoes_itcp_ativos_e_ex_bolsistas.csv  (49 pessoas)
    * carga_lancamentos_mensais_grana_noiz.csv   (lançamentos mensais)

Grava em ``membros`` e ``pagamentos`` de forma **idempotente**:
    * membros são localizados por RA (ou nome normalizado, quando não há RA);
    * lançamentos usam UPSERT pela chave única (membro_id, mes).

Uso:
    python -m scripts.importar_legado
    python -m scripts.importar_legado --membros caminho/a.csv \
        --lancamentos caminho/b.csv --db data/caixinha.db
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Permite executar tanto "python -m scripts.importar_legado" quanto
# "python scripts/importar_legado.py" a partir da raiz do projeto.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from src import config
    from src.utils import db
except ImportError:  # execução com src/ no sys.path
    import config  # type: ignore
    from utils import db  # type: ignore


# ---------------------------------------------------------------------------
# Localização dos arquivos
# ---------------------------------------------------------------------------

NOMES_MEMBROS = (
    "cotizacoes_itcp_ativos_e_ex_bolsistas.csv",
    "cotizacoes_itcp_ativos_e_ex_bolsistas_corrigido.csv",
)
NOMES_LANCAMENTOS = (
    "carga_lancamentos_mensais_grana_noiz.csv",
    "carga_lancamentos_mensais_grana_noiz_corrigido.csv",
)


def _resolver_csv(
    caminho_informado: Optional[str],
    nomes: Tuple[str, ...],
    caminho_config: Optional[str] = None,
) -> Path:
    """
    Resolve o CSV na seguinte ordem:
    1. caminho explicitamente informado (erro se não existir);
    2. caminho configurado em CSV_MEMBROS/CSV_LANCAMENTOS;
    3. LEGADO_DIR do config;
    4. ./data/legado;
    5. ~/Downloads (ambiente local do operador).
    """
    if caminho_informado:
        base = Path(caminho_informado)
        if base.is_file():
            return base.resolve()
        if base.is_dir():
            for nome in nomes:
                alvo = base / nome
                if alvo.is_file():
                    return alvo.resolve()
        raise FileNotFoundError(
            f"Arquivo informado não encontrado: {caminho_informado}"
        )

    candidatos: List[Path] = []
    if caminho_config:
        candidatos.append(Path(caminho_config))
    candidatos.append(Path(config.LEGADO_DIR))
    candidatos.append(Path("data/legado"))
    candidatos.append(Path.home() / "Downloads")

    for base in candidatos:
        if base.is_file():
            return base.resolve()
        for nome in nomes:
            alvo = base / nome
            if alvo.is_file():
                return alvo.resolve()

    procurados = ", ".join(nomes)
    raise FileNotFoundError(
        f"CSV não encontrado ({procurados}). Informe o caminho via argumento "
        f"ou coloque o arquivo em {config.LEGADO_DIR}/."
    )


# ---------------------------------------------------------------------------
# Normalizações
# ---------------------------------------------------------------------------


def _limpar(valor: Any) -> Optional[str]:
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def _normalizar_data(valor: Any) -> Optional[str]:
    """Converte datas dd/mm/aaaa ou aaaa-mm-dd para ISO; mantém o resto."""
    texto = _limpar(valor)
    if not texto:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        return texto
    match = re.search(r"(\d{2})/(\d{2})/(\d{4})", texto)
    if match:
        dia, mes, ano = match.groups()
        return f"{ano}-{mes}-{dia}"
    return texto


def _normalizar_desligamento(valor: Any) -> Optional[str]:
    """
    O CSV traz texto livre no campo de desligamento
    ("Prorr. 30/06/2026 (...)", "Vigente", "2025").

    * texto sem data útil ("Vigente", "Sem data...") -> None;
    * data completa -> ISO;
    * ano isolado ou texto não reconhecido -> preservado como veio.
    """
    texto = _limpar(valor)
    if not texto:
        return None
    if texto.lower().startswith(("vigente", "sem data", "indefinid", "-")):
        return None

    data = _normalizar_data(texto)
    if data and re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
        return data
    if re.fullmatch(r"\d{4}", texto):
        return texto
    return texto


def _flag_binaria(valor: Any) -> int:
    texto = (_limpar(valor) or "").upper()
    return 1 if texto in {"SIM", "S", "1", "TRUE", "YES"} else 0


def _parse_float(valor: Any, default: float = 0.0) -> float:
    texto = _limpar(valor)
    if not texto:
        return default
    texto = texto.replace("R$", "").replace(" ", "")
    # Aceita "1.234,56" e "1234.56"
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return default


def _ler_csv(caminho: Path) -> List[Dict[str, str]]:
    with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


# ---------------------------------------------------------------------------
# Importação
# ---------------------------------------------------------------------------


def importar_membros(linhas: List[Dict[str, str]]) -> Dict[str, Any]:
    relatorio = {
        "lidos": len(linhas),
        "inseridos": 0,
        "atualizados": 0,
        "ignorados": 0,
        "mapa_id_ref": {},
        "ativos": 0,
        "ex_bolsistas": 0,
    }

    for linha in linhas:
        id_ref = _limpar(linha.get("id_ref"))
        nome = _limpar(linha.get("nome"))
        if not id_ref or not nome:
            relatorio["ignorados"] += 1
            print(f"  ⚠️  Linha de membro ignorada (id/nome ausente): {linha}")
            continue

        try:
            ex_bolsista = _flag_binaria(linha.get("ex_bolsista"))
            id_membro, criado = db.salvar_membro_legado(
                nome=nome,
                ra=linha.get("ra"),
                status_vinculo=_limpar(linha.get("status_vinculo")) or "ATIVO",
                ex_bolsista=ex_bolsista,
                modalidade_bolsa=_limpar(linha.get("modalidade_bolsa")),
                data_inicio=_normalizar_data(linha.get("data_inicio")),
                data_desligamento=_normalizar_desligamento(
                    linha.get("data_desligamento_ou_termino")
                ),
            )
        except (sqlite3.Error, ValueError) as exc:
            relatorio["ignorados"] += 1
            print(f"  ⚠️  Falha ao importar membro {id_ref} ({nome}): {exc}")
            continue

        relatorio["mapa_id_ref"][id_ref] = id_membro
        if criado:
            relatorio["inseridos"] += 1
        else:
            relatorio["atualizados"] += 1

        if ex_bolsista:
            relatorio["ex_bolsistas"] += 1
        else:
            relatorio["ativos"] += 1

    return relatorio


def importar_lancamentos(
    linhas: List[Dict[str, str]],
    mapa_id_ref: Dict[str, int],
    forcar: bool = False,
) -> Dict[str, Any]:
    relatorio = {
        "lidos": len(linhas),
        "inseridos": 0,
        "atualizados": 0,
        "ignorados": 0,
        "pagos": 0,
        "pendentes": 0,
        "aguardando": 0,
        "valor_pago_csv": 0.0,
    }

    for linha in linhas:
        id_ref = _limpar(linha.get("membro_id_ref"))
        mes = _limpar(linha.get("mes"))
        if not id_ref or not mes:
            relatorio["ignorados"] += 1
            continue

        id_membro = mapa_id_ref.get(id_ref)
        if id_membro is None:
            relatorio["ignorados"] += 1
            print(
                f"  ⚠️  Lançamento sem membro correspondente: "
                f"id_ref={id_ref} mes={mes}"
            )
            continue

        if not re.fullmatch(r"\d{4}-\d{2}", mes):
            relatorio["ignorados"] += 1
            print(f"  ⚠️  Mês inválido ignorado: id_ref={id_ref} mes={mes!r}")
            continue

        quitado = _flag_binaria(linha.get("quitado"))
        status_detalhado = (_limpar(linha.get("status_detalhado")) or "").upper()

        if quitado:
            status = db.STATUS_PAGO
        elif "AGUARDANDO" in status_detalhado:
            status = db.STATUS_AGUARDANDO_AUDITORIA
        else:
            status = db.STATUS_PENDENTE

        valor = _parse_float(linha.get("valor_pago"))
        # No CSV, PENDENTE vem com valor_pago = 0. No banco, valor_pago
        # representa o valor da cota/cobrança daquele mês.
        if valor <= 0:
            valor = float(config.VALOR_CONTRIBUICAO)

        try:
            inserido, atualizado = db.importar_lancamento(
                membro_id=id_membro,
                mes=mes,
                valor_pago=valor,
                quitado=quitado,
                observacoes=_limpar(linha.get("observacoes")),
                status_pagamento=status,
                forcar=forcar,
            )
        except (sqlite3.Error, ValueError) as exc:
            relatorio["ignorados"] += 1
            print(f"  ⚠️  Falha no lançamento {id_ref}/{mes}: {exc}")
            continue

        if inserido:
            relatorio["inseridos"] += 1
        elif atualizado:
            relatorio["atualizados"] += 1

        if status == db.STATUS_PAGO:
            relatorio["pagos"] += 1
            relatorio["valor_pago_csv"] += valor
        elif status == db.STATUS_AGUARDANDO_AUDITORIA:
            relatorio["aguardando"] += 1
        else:
            relatorio["pendentes"] += 1

    return relatorio


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def imprimir_relatorio(
    membros: Dict[str, Any],
    lancamentos: Dict[str, Any],
    resumo_db: Dict[str, Dict[str, float]],
) -> None:
    ativos = resumo_db["ativos"]
    ex = resumo_db["ex_bolsistas"]

    print("\n" + "=" * 68)
    print("📊 RELATÓRIO DE AUDITORIA DA CARGA LEGADA")
    print("=" * 68)

    print("\n👥 MEMBROS")
    print(f"  CSV lido ............... {membros['lidos']}")
    print(f"  Inseridos .............. {membros['inseridos']}")
    print(f"  Atualizados ............ {membros['atualizados']}")
    print(f"  Ignorados .............. {membros['ignorados']}")
    print(f"  Ativos (CSV) ........... {membros['ativos']}")
    print(f"  Ex-bolsistas (CSV) ..... {membros['ex_bolsistas']}")
    print(f"  Total no banco ......... {ativos['membros'] + ex['membros']}")
    total_banco = ativos["membros"] + ex["membros"]
    if total_banco != membros["lidos"]:
        print(
            f"  ℹ️  Inclui {int(total_banco - membros['lidos'])} registro(s) "
            f"pré-existente(s) fora do CSV."
        )

    print("\n💳 LANÇAMENTOS")
    print(f"  CSV lido ............... {lancamentos['lidos']}")
    print(f"  Inseridos .............. {lancamentos['inseridos']}")
    print(f"  Atualizados ............ {lancamentos['atualizados']}")
    print(f"  Ignorados .............. {lancamentos['ignorados']}")
    print(f"  Status PAGO ............ {lancamentos['pagos']}")
    print(f"  Status PENDENTE ........ {lancamentos['pendentes']}")
    print(f"  Aguardando auditoria ... {lancamentos['aguardando']}")

    print("\n💰 ATIVOS")
    print(f"  Lançamentos ............ {int(ativos['lancamentos'])}")
    print(f"  Cotas pagas ............ {int(ativos['pagos'])} "
          f"({_brl(ativos['valor_pago'])})")
    print(f"  Cotas pendentes ........ {int(ativos['pendentes'])} "
          f"({_brl(ativos['saldo_devedor'])})")
    print(f"  Em auditoria ........... {int(ativos['em_auditoria'])}")

    print("\n🎓 EX-BOLSISTAS (histórico)")
    print(f"  Lançamentos ............ {int(ex['lancamentos'])}")
    print(f"  Cotas pagas ............ {int(ex['pagos'])} "
          f"({_brl(ex['valor_pago'])})")
    print(f"  Pendências históricas .. {int(ex['pendentes'])} "
          f"({_brl(ex['saldo_devedor'])})")
    print(f"  Em auditoria ........... {int(ex['em_auditoria'])}")

    print("\n🧾 TOTAIS")
    print(f"  Cotas pagas ............ "
          f"{int(ativos['pagos'] + ex['pagos'])} "
          f"({_brl(ativos['valor_pago'] + ex['valor_pago'])})")
    print(f"  Saldo devedor total .... "
          f"{_brl(ativos['saldo_devedor'] + ex['saldo_devedor'])}")
    print("=" * 68)
    print("✅ Carga idempotente: executar novamente atualiza, sem duplicar.")
    print("=" * 68)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa o histórico legado de cotizações da ITCP."
    )
    parser.add_argument(
        "--membros",
        default=None,
        help=f"CSV de membros (padrão: {config.CSV_MEMBROS})",
    )
    parser.add_argument(
        "--lancamentos",
        default=None,
        help=f"CSV de lançamentos (padrão: {config.CSV_LANCAMENTOS})",
    )
    parser.add_argument(
        "--db",
        default=None,
        help=f"Caminho do SQLite (padrão: {config.DB_PATH})",
    )
    parser.add_argument(
        "--forcar",
        action="store_true",
        help="Sobrescreve status já avançados (pago/aguardando) com o CSV.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)

    if args.db:
        config.DB_PATH = args.db

    try:
        caminho_membros = _resolver_csv(
            args.membros, NOMES_MEMBROS, config.CSV_MEMBROS
        )
        caminho_lancamentos = _resolver_csv(
            args.lancamentos, NOMES_LANCAMENTOS, config.CSV_LANCAMENTOS
        )
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return 2

    print("🌱 Importação do legado da caixinha ITCP")
    print(f"   Membros:     {caminho_membros}")
    print(f"   Lançamentos: {caminho_lancamentos}")
    print(f"   Banco:       {os.path.abspath(config.DB_PATH)}")
    if args.forcar:
        print("   Modo:        forçado (CSV sobrescreve status operacionais)")

    try:
        db.init_db()
        linhas_membros = _ler_csv(caminho_membros)
        linhas_lancamentos = _ler_csv(caminho_lancamentos)

        print(f"\n📥 Importando {len(linhas_membros)} membros...")
        rel_membros = importar_membros(linhas_membros)

        print(f"📥 Importando {len(linhas_lancamentos)} lançamentos...")
        rel_lancamentos = importar_lancamentos(
            linhas_lancamentos, rel_membros["mapa_id_ref"], forcar=args.forcar
        )

        resumo = db.obter_resumo_financeiro()
        imprimir_relatorio(rel_membros, rel_lancamentos, resumo)
        return 0
    except sqlite3.Error as exc:
        print(f"❌ Erro de banco de dados: {exc}")
        return 1
    except (OSError, UnicodeError, csv.Error) as exc:
        print(f"❌ Erro ao ler CSV: {exc}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Importação interrompida pelo usuário.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
