"""
Camada de acesso ao banco SQLite da caixinha
============================================

Mantém apenas a biblioteca padrão (sqlite3) — sem ORMs.

Schema atual (versão 2)
-----------------------
membros:
    id, nome, ra, telegram_id (nullable/unique), status_vinculo,
    ex_bolsista, modalidade_bolsa, data_inicio, data_desligamento

pagamentos:
    id, membro_id, mes, valor_pago, quitado, data_pagamento,
    status_pagamento ('pendente' | 'aguardando_auditoria' | 'pago'),
    observacoes

Regras de compatibilidade:
    * ``quitado`` continua existindo e vale 1 somente quando
      ``status_pagamento = 'pago'``.
    * ``valor_pago`` guarda o valor da cota/cobrança daquele mês. Para
      lançamentos pendentes importados com valor 0, normalizamos para o
      valor da cota (R$ 5,00), pois as rotinas de dívida usam essa coluna.
"""

from __future__ import annotations

import logging
import os
import re
import sqlite3
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:  # importado como pacote (python -m src.bot / src.admin)
    from .. import config
except ImportError:  # executado com src/ no sys.path (python admin.py)
    import config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes de domínio
# ---------------------------------------------------------------------------

STATUS_PENDENTE = "pendente"
STATUS_AGUARDANDO_AUDITORIA = "aguardando_auditoria"
STATUS_PAGO = "pago"
STATUS_PAGAMENTO_VALIDOS = (
    STATUS_PENDENTE,
    STATUS_AGUARDANDO_AUDITORIA,
    STATUS_PAGO,
)

SCHEMA_VERSION = 3


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------


def _ensure_db_dir() -> None:
    """Garante que o diretório do banco exista antes de abrir a conexão."""
    diretorio = os.path.dirname(os.path.abspath(config.DB_PATH))
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)


def _connect() -> sqlite3.Connection:
    """Abre uma conexão com row_factory por nome e FK habilitada."""
    _ensure_db_dir()
    conn = sqlite3.connect(config.DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def _table_exists(conn: sqlite3.Connection, tabela: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (tabela,),
    ).fetchone()
    return row is not None


def _columns(conn: sqlite3.Connection, tabela: str) -> Dict[str, sqlite3.Row]:
    """Retorna {nome_coluna: info} via PRAGMA table_info."""
    if not _table_exists(conn, tabela):
        return {}
    return {
        row["name"]: row
        for row in conn.execute(f"PRAGMA table_info({tabela})").fetchall()
    }


def normalizar_ra(ra: Any) -> Optional[str]:
    """
    Normaliza RA vindo de CSV/planilha.

    ``"248340.0"`` -> ``"248340"``; vazio/None -> ``None``.
    """
    if ra is None:
        return None
    texto = str(ra).strip()
    if not texto or texto.lower() in {"nan", "none", "null", "-"}:
        return None
    # Planilhas exportam RA como float ("248340.0")
    if re.fullmatch(r"\d+\.0+", texto):
        texto = texto.split(".", 1)[0]
    return texto


def normalizar_nome(nome: Any) -> str:
    """Normaliza nome para comparação (sem acento, minúsculo, espaços únicos)."""
    if nome is None:
        return ""
    decomposto = unicodedata.normalize("NFKD", str(nome))
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento).strip().lower()


def _mes_valido(mes: str) -> bool:
    try:
        datetime.strptime(mes, "%Y-%m")
        return True
    except (TypeError, ValueError):
        return False


def _bool_int(valor: Any) -> int:
    if isinstance(valor, str):
        return 1 if valor.strip().lower() in {"1", "sim", "s", "true", "yes"} else 0
    return 1 if bool(valor) else 0


# ---------------------------------------------------------------------------
# Schema / migração
# ---------------------------------------------------------------------------

_DDL_MEMBROS = """
CREATE TABLE membros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ra TEXT,
    telegram_id INTEGER UNIQUE,
    status_vinculo TEXT DEFAULT 'ATIVO',
    ex_bolsista BOOLEAN NOT NULL DEFAULT 0,
    modalidade_bolsa TEXT,
    data_inicio TEXT,
    data_desligamento TEXT
)
"""

_DDL_PAGAMENTOS = """
CREATE TABLE pagamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    membro_id INTEGER NOT NULL,
    mes TEXT NOT NULL,
    valor_pago REAL NOT NULL,
    quitado BOOLEAN NOT NULL DEFAULT 0,
    data_pagamento TEXT,
    status_pagamento TEXT NOT NULL DEFAULT 'pendente'
        CHECK (status_pagamento IN ('pendente', 'aguardando_auditoria', 'pago')),
    observacoes TEXT,
    FOREIGN KEY (membro_id) REFERENCES membros (id) ON DELETE CASCADE,
    UNIQUE (membro_id, mes)
)
"""

_DDL_DESPESAS = """
CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    categoria TEXT,
    valor REAL NOT NULL CHECK (valor > 0),
    data TEXT NOT NULL,
    comprovante TEXT,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def _criar_tabelas(conn: sqlite3.Connection) -> None:
    conn.execute(_DDL_MEMBROS)
    conn.execute(_DDL_PAGAMENTOS)
    conn.execute(_DDL_DESPESAS)


def _criar_indices(conn: sqlite3.Connection) -> None:
    # RA pode ser NULL (membros sem RA na fonte). Só criamos índice único
    # quando não há duplicidade nos dados legados já existentes.
    duplicado = conn.execute(
        """
        SELECT ra FROM membros
        WHERE ra IS NOT NULL AND TRIM(ra) <> ''
        GROUP BY ra HAVING COUNT(*) > 1
        LIMIT 1
        """
    ).fetchone()
    if duplicado is None:
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_membros_ra
            ON membros (ra)
            WHERE ra IS NOT NULL AND TRIM(ra) <> ''
            """
        )
    else:
        logger.warning(
            "RA duplicado encontrado (%s); criando índice não único.",
            duplicado["ra"],
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_membros_ra ON membros (ra)"
        )

    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_pagamentos_membro ON pagamentos (membro_id)"
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_pagamentos_status
        ON pagamentos (status_pagamento)
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_pagamentos_mes ON pagamentos (mes)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_despesas_data ON despesas (data)"
    )


def _rebuild_schema(
    conn: sqlite3.Connection,
    membros_existe: bool,
    pagamentos_existe: bool,
) -> None:
    """
    Reconstrói as tabelas preservando os dados.

    Necessário porque SQLite não permite remover ``NOT NULL`` de uma coluna
    existente (caso de ``membros.telegram_id`` no schema antigo) nem adicionar
    ``UNIQUE`` via ALTER TABLE.
    """
    if pagamentos_existe:
        conn.execute("ALTER TABLE pagamentos RENAME TO pagamentos_legacy")
    if membros_existe:
        conn.execute("ALTER TABLE membros RENAME TO membros_legacy")

    _criar_tabelas(conn)

    if membros_existe:
        cols = _columns(conn, "membros_legacy")
        ra = "ra" if "ra" in cols else "NULL"
        status = "status_vinculo" if "status_vinculo" in cols else "'ATIVO'"
        ex = "ex_bolsista" if "ex_bolsista" in cols else "0"
        modalidade = "modalidade_bolsa" if "modalidade_bolsa" in cols else "NULL"
        inicio = "data_inicio" if "data_inicio" in cols else "NULL"
        deslig = "data_desligamento" if "data_desligamento" in cols else "NULL"
        conn.execute(
            f"""
            INSERT INTO membros
                (id, nome, ra, telegram_id, status_vinculo, ex_bolsista,
                 modalidade_bolsa, data_inicio, data_desligamento)
            SELECT id, nome, {ra}, telegram_id, {status}, {ex},
                   {modalidade}, {inicio}, {deslig}
            FROM membros_legacy
            """
        )
        conn.execute("DROP TABLE membros_legacy")

    if pagamentos_existe:
        cols = _columns(conn, "pagamentos_legacy")
        status = (
            "COALESCE(status_pagamento, CASE WHEN quitado = 1 THEN 'pago' ELSE 'pendente' END)"
            if "status_pagamento" in cols
            else "CASE WHEN quitado = 1 THEN 'pago' ELSE 'pendente' END"
        )
        obs = "observacoes" if "observacoes" in cols else "NULL"
        data_pag = "data_pagamento" if "data_pagamento" in cols else "NULL"
        conn.execute(
            f"""
            INSERT INTO pagamentos
                (id, membro_id, mes, valor_pago, quitado, data_pagamento,
                 status_pagamento, observacoes)
            SELECT id, membro_id, mes, valor_pago, quitado, {data_pag},
                   {status}, {obs}
            FROM pagamentos_legacy
            """
        )
        conn.execute("DROP TABLE pagamentos_legacy")


def _adicionar_colunas_faltantes(conn: sqlite3.Connection) -> None:
    """ALTER TABLE ADD COLUMN para schemas que já são compatíveis."""
    membros_cols = _columns(conn, "membros")
    novas_membros = {
        "ra": "TEXT",
        "telegram_id": "INTEGER",  # quando ausente, entra sem UNIQUE; init corrige
        "status_vinculo": "TEXT DEFAULT 'ATIVO'",
        "ex_bolsista": "BOOLEAN NOT NULL DEFAULT 0",
        "modalidade_bolsa": "TEXT",
        "data_inicio": "TEXT",
        "data_desligamento": "TEXT",
    }
    for coluna, definicao in novas_membros.items():
        if coluna not in membros_cols:
            conn.execute(f"ALTER TABLE membros ADD COLUMN {coluna} {definicao}")

    pagamentos_cols = _columns(conn, "pagamentos")
    if "status_pagamento" not in pagamentos_cols:
        conn.execute(
            "ALTER TABLE pagamentos ADD COLUMN "
            "status_pagamento TEXT NOT NULL DEFAULT 'pendente'"
        )
    if "observacoes" not in pagamentos_cols:
        conn.execute("ALTER TABLE pagamentos ADD COLUMN observacoes TEXT")

    # Backfill de bancos intermediários
    conn.execute(
        """
        UPDATE pagamentos
        SET status_pagamento = CASE WHEN quitado = 1 THEN 'pago' ELSE 'pendente' END
        WHERE status_pagamento IS NULL OR status_pagamento = ''
        """
    )
    conn.execute(
        """
        UPDATE pagamentos
        SET quitado = CASE WHEN status_pagamento = 'pago' THEN 1 ELSE 0 END
        WHERE status_pagamento IN ('pendente', 'aguardando_auditoria', 'pago')
          AND quitado <> CASE WHEN status_pagamento = 'pago' THEN 1 ELSE 0 END
        """
    )


def _migrar_schema(conn: sqlite3.Connection) -> None:
    membros_existe = _table_exists(conn, "membros")
    pagamentos_existe = _table_exists(conn, "pagamentos")

    if not membros_existe and not pagamentos_existe:
        _criar_tabelas(conn)
    else:
        m_cols = _columns(conn, "membros")
        p_cols = _columns(conn, "pagamentos")

        precisa_rebuild_membros = membros_existe and (
            "telegram_id" not in m_cols
            or bool(m_cols["telegram_id"]["notnull"])
            or any(
                c not in m_cols
                for c in (
                    "ra",
                    "status_vinculo",
                    "ex_bolsista",
                    "modalidade_bolsa",
                    "data_inicio",
                    "data_desligamento",
                )
            )
        )
        precisa_rebuild_pagamentos = pagamentos_existe and any(
            c not in p_cols for c in ("status_pagamento", "observacoes")
        )

        if precisa_rebuild_membros or precisa_rebuild_pagamentos:
            _rebuild_schema(conn, membros_existe, pagamentos_existe)
        else:
            if not membros_existe:
                conn.execute(_DDL_MEMBROS)
            if not pagamentos_existe:
                conn.execute(_DDL_PAGAMENTOS)
            _adicionar_colunas_faltantes(conn)

    # A tabela de despesas é aditiva e pode ser criada sem rebuild.
    conn.execute(_DDL_DESPESAS)
    _criar_indices(conn)
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def init_db() -> None:
    """
    Cria o schema e executa a migração segura (idempotente).

    Pode ser chamada a cada inicialização do bot/CLI.
    """
    _ensure_db_dir()
    conn = _connect()
    try:
        # WAL permite leitura concorrente enquanto bot/web escrevem.
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA foreign_keys = OFF")
        with conn:
            _migrar_schema(conn)
        conn.execute("PRAGMA foreign_keys = ON")
    except sqlite3.Error as exc:
        logger.error("Erro ao inicializar/migrar o banco: %s", exc)
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Membros
# ---------------------------------------------------------------------------


def _localizar_membro_legado(
    conn: sqlite3.Connection, nome: str, ra: Optional[str]
) -> Optional[sqlite3.Row]:
    """Localiza um membro por RA; se não houver, por nome normalizado exato."""
    ra_norm = normalizar_ra(ra)
    if ra_norm:
        row = conn.execute(
            "SELECT * FROM membros WHERE ra = ? LIMIT 1", (ra_norm,)
        ).fetchone()
        if row is not None:
            return row

    alvo = normalizar_nome(nome)
    if not alvo:
        return None
    for row in conn.execute("SELECT * FROM membros").fetchall():
        if normalizar_nome(row["nome"]) == alvo:
            return row
    return None


def salvar_membro_legado(
    nome: str,
    ra: Any = None,
    status_vinculo: str = "ATIVO",
    ex_bolsista: Any = False,
    modalidade_bolsa: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_desligamento: Optional[str] = None,
) -> Tuple[int, bool]:
    """
    UPSERT de membro importado do legado.

    A chave natural é o RA; para registros sem RA usamos o nome normalizado.
    Nunca sobrescreve ``telegram_id`` já vinculado.

    Retorna ``(id_membro, criado)``.
    """
    nome = (nome or "").strip()
    if not nome:
        raise ValueError("Nome do membro é obrigatório")

    ra_norm = normalizar_ra(ra)
    ex_int = _bool_int(ex_bolsista)

    conn = _connect()
    try:
        with conn:
            existente = _localizar_membro_legado(conn, nome, ra_norm)
            if existente is not None:
                # Campos vazios no CSV não apagam ajustes manuais já feitos.
                conn.execute(
                    """
                    UPDATE membros
                    SET nome = ?, ra = ?, status_vinculo = ?, ex_bolsista = ?,
                        modalidade_bolsa = ?, data_inicio = ?, data_desligamento = ?
                    WHERE id = ?
                    """,
                    (
                        nome,
                        ra_norm or existente["ra"],
                        status_vinculo or "ATIVO",
                        ex_int,
                        modalidade_bolsa or existente["modalidade_bolsa"],
                        data_inicio or existente["data_inicio"],
                        data_desligamento or existente["data_desligamento"],
                        existente["id"],
                    ),
                )
                return int(existente["id"]), False

            cursor = conn.execute(
                """
                INSERT INTO membros
                    (nome, ra, status_vinculo, ex_bolsista, modalidade_bolsa,
                     data_inicio, data_desligamento)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    nome,
                    ra_norm,
                    status_vinculo or "ATIVO",
                    ex_int,
                    modalidade_bolsa,
                    data_inicio,
                    data_desligamento,
                ),
            )
            return int(cursor.lastrowid), True
    finally:
        conn.close()


def adicionar_membro(
    nome: str,
    telegram_id: Optional[int] = None,
    ra: Any = None,
    status_vinculo: str = "ATIVO",
    ex_bolsista: Any = False,
) -> bool:
    """
    Adiciona um membro novo.

    ``telegram_id`` é opcional para permitir cadastros legados sem Telegram.
    Retorna False em caso de conflito (telegram_id/RA já existente).
    """
    try:
        conn = _connect()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO membros
                        (nome, ra, telegram_id, status_vinculo, ex_bolsista)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        nome,
                        normalizar_ra(ra),
                        telegram_id,
                        status_vinculo or "ATIVO",
                        _bool_int(ex_bolsista),
                    ),
                )
            return True
        finally:
            conn.close()
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as exc:
        logger.error("Erro ao adicionar membro %s: %s", nome, exc)
        return False


def buscar_membro_por_telegram_id(telegram_id: int) -> Optional[sqlite3.Row]:
    """Busca um membro pelo ID do Telegram (None se não cadastrado)."""
    conn = _connect()
    try:
        return conn.execute(
            "SELECT * FROM membros WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
    finally:
        conn.close()


def buscar_perfil_membro(telegram_id: int) -> Optional[sqlite3.Row]:
    """Alias explícito para leitura do perfil completo do membro."""
    return buscar_membro_por_telegram_id(telegram_id)


def buscar_membro_por_ra(ra: Any) -> Optional[sqlite3.Row]:
    ra_norm = normalizar_ra(ra)
    if not ra_norm:
        return None
    conn = _connect()
    try:
        return conn.execute(
            "SELECT * FROM membros WHERE ra = ? LIMIT 1", (ra_norm,)
        ).fetchone()
    finally:
        conn.close()


def buscar_membro_por_id(id_membro: int) -> Optional[sqlite3.Row]:
    conn = _connect()
    try:
        return conn.execute(
            "SELECT * FROM membros WHERE id = ?", (id_membro,)
        ).fetchone()
    finally:
        conn.close()


def buscar_membros_por_nome(nome: str) -> List[sqlite3.Row]:
    """Busca membros cujo nome normalizado seja igual ao informado."""
    alvo = normalizar_nome(nome)
    if not alvo:
        return []
    conn = _connect()
    try:
        return [
            row
            for row in conn.execute("SELECT * FROM membros ORDER BY nome").fetchall()
            if normalizar_nome(row["nome"]) == alvo
        ]
    finally:
        conn.close()


def buscar_todos_membros() -> List[sqlite3.Row]:
    """Todos os membros: (id, nome, telegram_id), ordenados por nome."""
    conn = _connect()
    try:
        return conn.execute(
            "SELECT id, nome, telegram_id FROM membros ORDER BY nome"
        ).fetchall()
    finally:
        conn.close()


def listar_membros_detalhado(
    ex_bolsista: Optional[bool] = None,
    apenas_sem_telegram: bool = False,
) -> List[sqlite3.Row]:
    """Lista membros com dados de vínculo/financeiro para o admin."""
    filtros: List[str] = []
    params: List[Any] = []
    if ex_bolsista is not None:
        filtros.append("ex_bolsista = ?")
        params.append(1 if ex_bolsista else 0)
    if apenas_sem_telegram:
        filtros.append("telegram_id IS NULL")

    where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
    conn = _connect()
    try:
        return conn.execute(
            f"""
            SELECT id, nome, ra, telegram_id, status_vinculo, ex_bolsista,
                   modalidade_bolsa, data_inicio, data_desligamento
            FROM membros
            {where}
            ORDER BY ex_bolsista, nome
            """,
            params,
        ).fetchall()
    finally:
        conn.close()


def listar_membros_simples() -> List[sqlite3.Row]:
    """Lista enxuta para seleção no CLI: id, nome, ra, telegram_id, ex_bolsista."""
    conn = _connect()
    try:
        return conn.execute(
            """
            SELECT id, nome, ra, telegram_id, ex_bolsista
            FROM membros ORDER BY ex_bolsista, nome
            """
        ).fetchall()
    finally:
        conn.close()


def contar_membros_por_tipo() -> Dict[str, int]:
    """Retorna {'ativos': n, 'ex_bolsistas': n}."""
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT ex_bolsista, COUNT(*) AS total FROM membros GROUP BY ex_bolsista"
        ).fetchall()
    finally:
        conn.close()

    resultado = {"ativos": 0, "ex_bolsistas": 0}
    for row in rows:
        if int(row["ex_bolsista"]) == 1:
            resultado["ex_bolsistas"] = int(row["total"])
        else:
            resultado["ativos"] = int(row["total"])
    return resultado


def buscar_membros_para_cobranca() -> List[sqlite3.Row]:
    """
    Membros que devem receber novas cobranças mensais.

    Ex-bolsistas ficam de fora por regra de negócio; membros sem Telegram
    também (não há como notificar, mas a cobrança em si é criada por
    ``criar_cobranca_mensal``).
    """
    conn = _connect()
    try:
        return conn.execute(
            """
            SELECT id, nome, telegram_id
            FROM membros
            WHERE ex_bolsista = 0
              AND telegram_id IS NOT NULL
            ORDER BY nome
            """
        ).fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Vínculo Telegram <-> cadastro legado
# ---------------------------------------------------------------------------


def _mesclar_membros(
    conn: sqlite3.Connection, origem_id: int, destino_id: int
) -> None:
    """
    Move lançamentos do membro placeholder (origem) para o legado (destino)
    e remove o placeholder. Em conflito de (membro, mês), preserva o status
    mais avançado (aguardando_auditoria > pendente) sem duplicar linhas.
    """
    if origem_id == destino_id:
        return

    pagamentos = conn.execute(
        "SELECT * FROM pagamentos WHERE membro_id = ?", (origem_id,)
    ).fetchall()
    for p in pagamentos:
        conn.execute(
            """
            INSERT INTO pagamentos
                (membro_id, mes, valor_pago, quitado, data_pagamento,
                 status_pagamento, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (membro_id, mes) DO UPDATE SET
                status_pagamento = CASE
                    WHEN excluded.status_pagamento = 'aguardando_auditoria'
                         AND pagamentos.status_pagamento = 'pendente'
                    THEN 'aguardando_auditoria'
                    ELSE pagamentos.status_pagamento
                END,
                quitado = CASE
                    WHEN excluded.status_pagamento = 'aguardando_auditoria'
                         AND pagamentos.status_pagamento = 'pendente'
                    THEN 0
                    ELSE pagamentos.quitado
                END,
                data_pagamento = COALESCE(pagamentos.data_pagamento,
                                          excluded.data_pagamento),
                observacoes = COALESCE(pagamentos.observacoes,
                                       excluded.observacoes)
            """,
            (
                destino_id,
                p["mes"],
                p["valor_pago"],
                p["quitado"],
                p["data_pagamento"],
                p["status_pagamento"],
                p["observacoes"],
            ),
        )

    conn.execute("DELETE FROM pagamentos WHERE membro_id = ?", (origem_id,))
    conn.execute("DELETE FROM membros WHERE id = ?", (origem_id,))


def vincular_telegram_id(id_membro: int, telegram_id: int) -> bool:
    """
    Vincula um ``telegram_id`` a um membro já existente.

    Se o Telegram já estiver ligado a um placeholder criado por ``/start``,
    o placeholder é mesclado no membro de destino (evita duplicidade).
    """
    try:
        conn = _connect()
        try:
            with conn:
                destino = conn.execute(
                    "SELECT * FROM membros WHERE id = ?", (id_membro,)
                ).fetchone()
                if destino is None:
                    return False

                atual = conn.execute(
                    "SELECT * FROM membros WHERE telegram_id = ?", (telegram_id,)
                ).fetchone()
                if atual is not None and int(atual["id"]) != int(id_membro):
                    _mesclar_membros(conn, int(atual["id"]), int(id_membro))

                conn.execute(
                    "UPDATE membros SET telegram_id = ? WHERE id = ?",
                    (telegram_id, id_membro),
                )
            return True
        finally:
            conn.close()
    except sqlite3.Error as exc:
        logger.error("Erro ao vincular telegram_id %s ao membro %s: %s",
                     telegram_id, id_membro, exc)
        return False


def vincular_por_ra(
    ra: Any, telegram_id: int
) -> Tuple[bool, str, Optional[int]]:
    """
    Vincula o Telegram do usuário ao cadastro legado localizado pelo RA.

    Retorna ``(ok, motivo, id_membro)`` com motivos:
    ``vinculado``, ``ja_vinculado``, ``ra_nao_encontrado``,
    ``ra_ja_vinculado``, ``telegram_em_outro_cadastro``, ``erro_banco``.
    """
    ra_norm = normalizar_ra(ra)
    if not ra_norm:
        return False, "ra_nao_encontrado", None

    try:
        conn = _connect()
        try:
            with conn:
                membro = conn.execute(
                    "SELECT * FROM membros WHERE ra = ? LIMIT 1", (ra_norm,)
                ).fetchone()
                if membro is None:
                    return False, "ra_nao_encontrado", None

                id_membro = int(membro["id"])
                tg_atual = membro["telegram_id"]
                if tg_atual == telegram_id:
                    return True, "ja_vinculado", id_membro
                if tg_atual is not None and int(tg_atual) != int(telegram_id):
                    return False, "ra_ja_vinculado", id_membro

                atual = conn.execute(
                    "SELECT * FROM membros WHERE telegram_id = ?", (telegram_id,)
                ).fetchone()
                if atual is not None and int(atual["id"]) != id_membro:
                    # Só mescla automaticamente um cadastro placeholder (sem RA).
                    # Se o Telegram já pertence a outro cadastro real, exige admin.
                    if normalizar_ra(atual["ra"]):
                        return False, "telegram_em_outro_cadastro", id_membro
                    _mesclar_membros(conn, int(atual["id"]), id_membro)

                conn.execute(
                    "UPDATE membros SET telegram_id = ? WHERE id = ?",
                    (telegram_id, id_membro),
                )
            return True, "vinculado", id_membro
        finally:
            conn.close()
    except sqlite3.Error as exc:
        logger.error("Erro ao vincular RA %s ao telegram %s: %s",
                     ra_norm, telegram_id, exc)
        return False, "erro_banco", None


# ---------------------------------------------------------------------------
# Cobranças e pagamentos
# ---------------------------------------------------------------------------


def criar_cobranca_mensal(mes: str) -> int:
    """
    Cria cobranças pendentes apenas para membros ativos (``ex_bolsista = 0``).

    Ex-bolsistas continuam no banco para preservar histórico, mas nunca
    recebem novas cobranças automáticas. Retorna quantas linhas foram criadas.
    """
    if not _mes_valido(mes):
        raise ValueError(f"Mês inválido: {mes!r}. Use o formato YYYY-MM.")

    conn = _connect()
    try:
        with conn:
            membros = conn.execute(
                """
                SELECT id FROM membros
                WHERE ex_bolsista = 0
                  AND COALESCE(status_vinculo, '') NOT LIKE 'EX-BOLSISTA%'
                """
            ).fetchall()

            criadas = 0
            for membro in membros:
                cursor = conn.execute(
                    """
                    INSERT INTO pagamentos
                        (membro_id, mes, valor_pago, quitado, status_pagamento)
                    VALUES (?, ?, ?, 0, 'pendente')
                    ON CONFLICT (membro_id, mes) DO NOTHING
                    """,
                    (membro["id"], mes, config.VALOR_CONTRIBUICAO),
                )
                if cursor.rowcount > 0:
                    criadas += 1
            return criadas
    finally:
        conn.close()


def importar_lancamento(
    membro_id: int,
    mes: str,
    valor_pago: float,
    quitado: Any,
    observacoes: Optional[str] = None,
    status_pagamento: Optional[str] = None,
    forcar: bool = False,
) -> Tuple[bool, bool]:
    """
    UPSERT idempotente de um lançamento mensal.

    Por padrão não regride status operacional já avançado:
        * ``pago`` nunca volta para ``pendente``/``aguardando``;
        * ``aguardando_auditoria`` não volta para ``pendente``.
    Use ``forcar=True`` para sobrescrever o banco com o CSV.

    Retorna ``(inserido, atualizado)``.
    """
    if not _mes_valido(mes):
        raise ValueError(f"Mês inválido: {mes!r}. Use o formato YYYY-MM.")
    if status_pagamento is None:
        status_pagamento = STATUS_PAGO if _bool_int(quitado) else STATUS_PENDENTE
    if status_pagamento not in STATUS_PAGAMENTO_VALIDOS:
        raise ValueError(f"status_pagamento inválido: {status_pagamento!r}")

    valor = float(valor_pago or 0)

    conn = _connect()
    try:
        with conn:
            existente = conn.execute(
                """
                SELECT id, status_pagamento FROM pagamentos
                WHERE membro_id = ? AND mes = ?
                """,
                (membro_id, mes),
            ).fetchone()

            if existente is None:
                quitado_int = 1 if status_pagamento == STATUS_PAGO else 0
                conn.execute(
                    """
                    INSERT INTO pagamentos
                        (membro_id, mes, valor_pago, quitado, status_pagamento,
                         observacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (membro_id, mes, valor, quitado_int, status_pagamento,
                     observacoes),
                )
                return True, False

            status_anterior = existente["status_pagamento"]
            status_final = status_pagamento
            if not forcar:
                if (
                    status_anterior == STATUS_PAGO
                    and status_pagamento != STATUS_PAGO
                ):
                    status_final = STATUS_PAGO
                elif (
                    status_anterior == STATUS_AGUARDANDO_AUDITORIA
                    and status_pagamento == STATUS_PENDENTE
                ):
                    status_final = STATUS_AGUARDANDO_AUDITORIA

            quitado_int = 1 if status_final == STATUS_PAGO else 0
            conn.execute(
                """
                UPDATE pagamentos
                SET valor_pago = ?, quitado = ?, status_pagamento = ?,
                    data_pagamento = CASE
                        WHEN ? = 'pendente' THEN NULL
                        ELSE data_pagamento
                    END,
                    observacoes = CASE
                        WHEN ? IS NOT NULL AND TRIM(?) <> '' THEN ?
                        ELSE observacoes
                    END
                WHERE id = ?
                """,
                (valor, quitado_int, status_final, status_final,
                 observacoes, observacoes, observacoes, existente["id"]),
            )
            return False, True
    finally:
        conn.close()


def registrar_solicitacao_pagamento_membro(
    membro_id: int, mes: str, origem: str = "bot"
) -> Tuple[bool, str]:
    """
    Núcleo da autodeclaração de pagamento, por id de membro.

    Usado pelo bot (via telegram_id) e pela interface web (via RA).
    """
    if not _mes_valido(mes):
        return False, "mes_invalido"

    agora = datetime.now().isoformat(timespec="seconds")
    obs = f"Solicitação de pagamento via {origem} em {agora}"
    try:
        conn = _connect()
        try:
            with conn:
                membro = conn.execute(
                    "SELECT id FROM membros WHERE id = ?", (membro_id,)
                ).fetchone()
                if membro is None:
                    return False, "nao_cadastrado"

                pagamento = conn.execute(
                    """
                    SELECT * FROM pagamentos
                    WHERE membro_id = ? AND mes = ?
                    """,
                    (membro_id, mes),
                ).fetchone()

                if pagamento is not None:
                    if pagamento["status_pagamento"] == STATUS_PAGO:
                        return False, "ja_pago"
                    if (
                        pagamento["status_pagamento"]
                        == STATUS_AGUARDANDO_AUDITORIA
                    ):
                        return False, "ja_aguardando"

                    conn.execute(
                        """
                        UPDATE pagamentos
                        SET status_pagamento = 'aguardando_auditoria',
                            quitado = 0,
                            data_pagamento = ?,
                            observacoes = CASE
                                WHEN observacoes IS NULL OR TRIM(observacoes) = ''
                                THEN ?
                                ELSE observacoes || ' | ' || ?
                            END
                        WHERE id = ?
                        """,
                        (agora, obs, obs, pagamento["id"]),
                    )
                else:
                    conn.execute(
                        """
                        INSERT INTO pagamentos
                            (membro_id, mes, valor_pago, quitado,
                             data_pagamento, status_pagamento, observacoes)
                        VALUES (?, ?, ?, 0, ?, 'aguardando_auditoria', ?)
                        """,
                        (membro_id, mes, config.VALOR_CONTRIBUICAO, agora, obs),
                    )
            return True, "ok"
        finally:
            conn.close()
    except sqlite3.Error as exc:
        logger.error("Erro ao registrar solicitação do membro %s/%s: %s",
                     membro_id, mes, exc)
        return False, "erro_banco"


def registrar_solicitacao_pagamento(
    telegram_id: int, mes: str
) -> Tuple[bool, str]:
    """
    Registra a autodeclaração de pagamento do usuário como
    ``aguardando_auditoria`` (não marca como pago).

    Retorna ``(ok, motivo)`` com motivos:
    ``ok``, ``nao_cadastrado``, ``ja_pago``, ``ja_aguardando``,
    ``mes_invalido``, ``erro_banco``.
    """
    membro = buscar_membro_por_telegram_id(telegram_id)
    if membro is None:
        return False, "nao_cadastrado"
    return registrar_solicitacao_pagamento_membro(
        int(membro["id"]), mes, origem="bot"
    )

def marcar_pagamento(telegram_id: int, mes: str) -> bool:
    """
    Marca um pagamento como pago diretamente (uso administrativo).

    O fluxo normal do bot passa por ``registrar_solicitacao_pagamento`` e
    auditoria via extrato/CLI.
    """
    agora = datetime.now().isoformat(timespec="seconds")
    conn = _connect()
    try:
        with conn:
            membro = conn.execute(
                "SELECT id FROM membros WHERE telegram_id = ?", (telegram_id,)
            ).fetchone()
            if membro is None:
                return False

            cursor = conn.execute(
                """
                UPDATE pagamentos
                SET status_pagamento = 'pago', quitado = 1, data_pagamento = ?
                WHERE membro_id = ? AND mes = ?
                """,
                (agora, membro["id"], mes),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def aprovar_pagamento(
    pagamento_id: int,
    aprovado: bool = True,
    observacao: Optional[str] = None,
) -> bool:
    """Aprova (pago) ou rejeita (volta a pendente) uma solicitação em auditoria."""
    agora = datetime.now().isoformat(timespec="seconds")
    conn = _connect()
    try:
        with conn:
            row = conn.execute(
                "SELECT * FROM pagamentos WHERE id = ?", (pagamento_id,)
            ).fetchone()
            if row is None:
                return False

            if aprovado:
                conn.execute(
                    """
                    UPDATE pagamentos
                    SET status_pagamento = 'pago', quitado = 1, data_pagamento = ?,
                        observacoes = CASE
                            WHEN ? IS NULL OR TRIM(?) = '' THEN observacoes
                            WHEN observacoes IS NULL OR TRIM(observacoes) = ''
                            THEN ?
                            ELSE observacoes || ' | ' || ?
                        END
                    WHERE id = ?
                    """,
                    (agora, observacao, observacao, observacao, observacao,
                     pagamento_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE pagamentos
                    SET status_pagamento = 'pendente', quitado = 0,
                        data_pagamento = NULL,
                        observacoes = CASE
                            WHEN ? IS NULL OR TRIM(?) = '' THEN observacoes
                            WHEN observacoes IS NULL OR TRIM(observacoes) = ''
                            THEN ?
                            ELSE observacoes || ' | ' || ?
                        END
                    WHERE id = ?
                    """,
                    (observacao, observacao, observacao, observacao,
                     pagamento_id),
                )
            return True
    finally:
        conn.close()


def buscar_dividas_por_membro_id(
    membro_id: int, incluir_em_auditoria: bool = False
) -> List[Tuple[str, float]]:
    """Meses em aberto de um membro: [(mes, valor), ...]."""
    status = (
        (STATUS_PENDENTE, STATUS_AGUARDANDO_AUDITORIA)
        if incluir_em_auditoria
        else (STATUS_PENDENTE,)
    )
    placeholders = ", ".join("?" for _ in status)
    conn = _connect()
    try:
        return [
            (row["mes"], float(row["valor"]))
            for row in conn.execute(
                f"""
                SELECT mes,
                       CASE WHEN valor_pago > 0 THEN valor_pago ELSE ? END AS valor
                FROM pagamentos
                WHERE membro_id = ?
                  AND status_pagamento IN ({placeholders})
                  AND quitado = 0
                ORDER BY mes
                """,
                (config.VALOR_CONTRIBUICAO, membro_id, *status),
            ).fetchall()
        ]
    finally:
        conn.close()


def buscar_dividas(telegram_id: int) -> List[Tuple[str, float]]:
    """Compatibilidade: dívidas a partir do telegram_id."""
    membro = buscar_membro_por_telegram_id(telegram_id)
    if membro is None:
        return []
    return buscar_dividas_por_membro_id(int(membro["id"]))


def buscar_dividas_em_auditoria(telegram_id: int) -> List[Tuple[str, float]]:
    """Meses com autodeclaração aguardando auditoria (não são cobrados)."""
    membro = buscar_membro_por_telegram_id(telegram_id)
    if membro is None:
        return []

    conn = _connect()
    try:
        return [
            (row["mes"], float(row["valor"]))
            for row in conn.execute(
                """
                SELECT mes,
                       CASE WHEN valor_pago > 0 THEN valor_pago ELSE ? END AS valor
                FROM pagamentos
                WHERE membro_id = ?
                  AND status_pagamento = 'aguardando_auditoria'
                ORDER BY mes
                """,
                (config.VALOR_CONTRIBUICAO, membro["id"]),
            ).fetchall()
        ]
    finally:
        conn.close()


def listar_pagamentos_aguardando_auditoria() -> List[sqlite3.Row]:
    """Solicitações pendentes de conferência no extrato."""
    conn = _connect()
    try:
        return conn.execute(
            """
            SELECT p.id, p.membro_id, m.nome, m.ra, m.ex_bolsista,
                   p.mes, p.valor_pago, p.data_pagamento, p.observacoes
            FROM pagamentos p
            JOIN membros m ON m.id = p.membro_id
            WHERE p.status_pagamento = 'aguardando_auditoria'
            ORDER BY p.data_pagamento, m.nome
            """
        ).fetchall()
    finally:
        conn.close()


def buscar_status_mes(mes: str) -> List[sqlite3.Row]:
    """Status de todos os membros para um mês (inclui ex-bolsistas)."""
    conn = _connect()
    try:
        return conn.execute(
            """
            SELECT m.id AS membro_id, m.nome, m.ra, m.ex_bolsista,
                   p.mes AS mes, p.status_pagamento, p.quitado, p.valor_pago
            FROM membros m
            JOIN pagamentos p ON p.membro_id = m.id
            WHERE p.mes = ?
            ORDER BY m.ex_bolsista, m.nome
            """,
            (mes,),
        ).fetchall()
    finally:
        conn.close()


def buscar_pagamentos_mes_atual(mes: str) -> List[Tuple[str, bool]]:
    """Compatibilidade: [(nome, quitado), ...] do mês."""
    return [
        (row["nome"], bool(row["quitado"])) for row in buscar_status_mes(mes)
    ]


# ---------------------------------------------------------------------------
# Relatórios / resumos
# ---------------------------------------------------------------------------


def _resumo_por_categoria(
    conn: sqlite3.Connection,
    where: str = "",
    params: Tuple[Any, ...] = (),
) -> Dict[str, Dict[str, float]]:
    resultado: Dict[str, Dict[str, float]] = {
        "ativos": {
            "membros": 0,
            "lancamentos": 0,
            "pagos": 0,
            "pendentes": 0,
            "em_auditoria": 0,
            "valor_pago": 0.0,
            "saldo_devedor": 0.0,
        },
        "ex_bolsistas": {
            "membros": 0,
            "lancamentos": 0,
            "pagos": 0,
            "pendentes": 0,
            "em_auditoria": 0,
            "valor_pago": 0.0,
            "saldo_devedor": 0.0,
        },
    }

    for row in conn.execute(
        "SELECT ex_bolsista, COUNT(*) AS total FROM membros GROUP BY ex_bolsista"
    ).fetchall():
        chave = "ex_bolsistas" if int(row["ex_bolsista"]) == 1 else "ativos"
        resultado[chave]["membros"] = int(row["total"])

    rows = conn.execute(
        f"""
        SELECT m.ex_bolsista AS ex,
               COUNT(*) AS lancamentos,
               SUM(CASE WHEN p.status_pagamento = 'pago' THEN 1 ELSE 0 END) AS pagos,
               SUM(CASE WHEN p.status_pagamento = 'pendente' THEN 1 ELSE 0 END) AS pendentes,
               SUM(CASE WHEN p.status_pagamento = 'aguardando_auditoria' THEN 1 ELSE 0 END) AS em_auditoria,
               SUM(CASE WHEN p.status_pagamento = 'pago' THEN p.valor_pago ELSE 0 END) AS valor_pago,
               SUM(CASE WHEN p.status_pagamento <> 'pago'
                        THEN (CASE WHEN p.valor_pago > 0 THEN p.valor_pago ELSE ? END)
                        ELSE 0 END) AS saldo_devedor
        FROM membros m
        JOIN pagamentos p ON p.membro_id = m.id
        {where}
        GROUP BY m.ex_bolsista
        """,
        (config.VALOR_CONTRIBUICAO, *params),
    ).fetchall()

    for row in rows:
        chave = "ex_bolsistas" if int(row["ex"]) == 1 else "ativos"
        resultado[chave].update(
            {
                "lancamentos": int(row["lancamentos"] or 0),
                "pagos": int(row["pagos"] or 0),
                "pendentes": int(row["pendentes"] or 0),
                "em_auditoria": int(row["em_auditoria"] or 0),
                "valor_pago": float(row["valor_pago"] or 0),
                "saldo_devedor": float(row["saldo_devedor"] or 0),
            }
        )

    return resultado


def obter_resumo_financeiro() -> Dict[str, Dict[str, float]]:
    """Balanço histórico separado entre ativos e ex-bolsistas."""
    conn = _connect()
    try:
        return _resumo_por_categoria(conn)
    finally:
        conn.close()


def obter_resumo_mes(mes: str) -> Dict[str, Dict[str, float]]:
    """Balanço de um mês específico, separado por categoria."""
    if not _mes_valido(mes):
        raise ValueError(f"Mês inválido: {mes!r}. Use o formato YYYY-MM.")
    conn = _connect()
    try:
        return _resumo_por_categoria(conn, "WHERE p.mes = ?", (mes,))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------


def buscar_mes_atual() -> str:
    """Mês atual no formato YYYY-MM."""
    return datetime.now().strftime("%Y-%m")


def adicionar_divida_manual_membro(
    membro_id: int, mes: str, valor: float
) -> bool:
    """
    Adiciona uma dívida manual por id de membro (funciona também para
    cadastros legados ainda sem Telegram). Retorna False se já existir.
    """
    if not _mes_valido(mes):
        return False
    try:
        conn = _connect()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO pagamentos
                        (membro_id, mes, valor_pago, quitado, status_pagamento)
                    VALUES (?, ?, ?, 0, 'pendente')
                    """,
                    (membro_id, mes, float(valor)),
                )
            return True
        finally:
            conn.close()
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as exc:
        logger.error("Erro ao adicionar dívida manual: %s", exc)
        return False


def adicionar_divida_manual(telegram_id: int, mes: str, valor: float) -> bool:
    """
    Adiciona uma dívida manual para um membro (útil para ajustes históricos).
    Retorna False se já existir cobrança para o par membro/mês.
    """
    membro = buscar_membro_por_telegram_id(telegram_id)
    if membro is None:
        return False
    return adicionar_divida_manual_membro(int(membro["id"]), mes, valor)


# ---------------------------------------------------------------------------
# Consultas para a interface web
# ---------------------------------------------------------------------------


def _ultimos_meses(quantidade: int = 12) -> List[str]:
    """Lista os últimos N meses (YYYY-MM) em ordem cronológica."""
    hoje = datetime.now()
    indice_atual = hoje.year * 12 + (hoje.month - 1)
    meses: List[str] = []
    for i in range(quantidade - 1, -1, -1):
        indice = indice_atual - i
        ano, mes = divmod(indice, 12)
        meses.append(f"{ano:04d}-{mes + 1:02d}")
    return meses


def listar_membros_web(
    tipo: str = "todos",
    busca: Optional[str] = None,
    mes: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Lista membros com agregados financeiros para o painel web.

    ``tipo``: ``todos``, ``ativos`` ou ``ex_bolsistas``.
    A busca é feita em Python (nome sem acento ou RA).
    """
    mes = mes or buscar_mes_atual()
    where = ""
    params: List[Any] = [config.VALOR_CONTRIBUICAO, mes]
    if tipo == "ativos":
        where = "WHERE m.ex_bolsista = 0"
    elif tipo == "ex_bolsistas":
        where = "WHERE m.ex_bolsista = 1"

    conn = _connect()
    try:
        rows = conn.execute(
            f"""
            SELECT m.id, m.nome, m.ra, m.telegram_id, m.status_vinculo,
                   m.ex_bolsista, m.modalidade_bolsa, m.data_inicio,
                   m.data_desligamento,
                   COALESCE(SUM(CASE WHEN p.status_pagamento = 'pago'
                                     THEN 1 ELSE 0 END), 0) AS cotas_pagas,
                   COALESCE(SUM(CASE WHEN p.status_pagamento = 'pago'
                                     THEN p.valor_pago ELSE 0 END), 0) AS total_pago,
                   COALESCE(SUM(CASE WHEN p.status_pagamento = 'pendente'
                                     THEN 1 ELSE 0 END), 0) AS cotas_pendentes,
                   COALESCE(SUM(CASE WHEN p.status_pagamento = 'pendente'
                                     THEN (CASE WHEN p.valor_pago > 0
                                                THEN p.valor_pago ELSE ? END)
                                     ELSE 0 END), 0) AS saldo_devedor,
                   COALESCE(SUM(CASE WHEN p.status_pagamento = 'aguardando_auditoria'
                                     THEN 1 ELSE 0 END), 0) AS em_auditoria,
                   MAX(CASE WHEN p.status_pagamento = 'pago'
                            THEN p.mes END) AS ultimo_pagamento,
                   MAX(CASE WHEN p.mes = ? THEN p.status_pagamento END)
                       AS status_mes_atual
            FROM membros m
            LEFT JOIN pagamentos p ON p.membro_id = m.id
            {where}
            GROUP BY m.id
            ORDER BY m.ex_bolsista, m.nome
            """,
            params,
        ).fetchall()
    finally:
        conn.close()

    resultado: List[Dict[str, Any]] = []
    termo = normalizar_nome(busca) if busca else ""
    termo_ra = (busca or "").strip()
    for row in rows:
        item = dict(row)
        item["ex_bolsista"] = bool(item["ex_bolsista"])
        item["cotas_pagas"] = int(item["cotas_pagas"] or 0)
        item["cotas_pendentes"] = int(item["cotas_pendentes"] or 0)
        item["em_auditoria"] = int(item["em_auditoria"] or 0)
        item["total_pago"] = float(item["total_pago"] or 0)
        item["saldo_devedor"] = float(item["saldo_devedor"] or 0)
        item["status_mes_atual"] = item["status_mes_atual"] or "sem_cobranca"
        if termo and termo not in normalizar_nome(item["nome"]):
            if not (termo_ra and termo_ra in (item["ra"] or "")):
                continue
        resultado.append(item)
    return resultado


def obter_detalhe_membro_web(membro_id: int) -> Optional[Dict[str, Any]]:
    """Perfil + histórico de pagamentos de um membro."""
    membro = buscar_membro_por_id(membro_id)
    if membro is None:
        return None

    itens = listar_membros_web("todos", mes=buscar_mes_atual())
    base = next((i for i in itens if int(i["id"]) == int(membro_id)), None)
    if base is None:
        base = dict(membro)
        base["ex_bolsista"] = bool(base["ex_bolsista"])

    conn = _connect()
    try:
        pagamentos = [
            dict(row)
            for row in conn.execute(
                """
                SELECT mes, valor_pago, quitado, status_pagamento,
                       data_pagamento, observacoes
                FROM pagamentos
                WHERE membro_id = ?
                ORDER BY mes DESC
                """,
                (membro_id,),
            ).fetchall()
        ]
    finally:
        conn.close()

    for p in pagamentos:
        p["valor_pago"] = float(p["valor_pago"] or 0)
        p["quitado"] = bool(p["quitado"])

    detalhe = dict(base)
    detalhe["pagamentos"] = pagamentos
    return detalhe


def obter_detalhe_membro_por_ra(ra: Any) -> Optional[Dict[str, Any]]:
    membro = buscar_membro_por_ra(ra)
    if membro is None:
        return None
    return obter_detalhe_membro_web(int(membro["id"]))


def listar_despesas(limite: int = 50) -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        return [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, descricao, categoria, valor, data, comprovante, criado_em
                FROM despesas
                ORDER BY data DESC, id DESC
                LIMIT ?
                """,
                (int(limite),),
            ).fetchall()
        ]
    finally:
        conn.close()


def adicionar_despesa(
    descricao: str,
    valor: float,
    data: Optional[str] = None,
    categoria: Optional[str] = None,
    comprovante: Optional[str] = None,
) -> int:
    """
    Lança uma despesa no livro caixa. Retorna o id criado.

    ``data`` no formato YYYY-MM-DD; se omitida, usa hoje.
    """
    descricao = (descricao or "").strip()
    if not descricao:
        raise ValueError("Descrição é obrigatória")
    valor = float(valor)
    if valor <= 0:
        raise ValueError("Valor da despesa deve ser positivo")

    data = (data or datetime.now().strftime("%Y-%m-%d")).strip()
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Data da despesa deve estar em YYYY-MM-DD") from exc

    conn = _connect()
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO despesas (descricao, categoria, valor, data, comprovante)
                VALUES (?, ?, ?, ?, ?)
                """,
                (descricao, categoria, valor, data, comprovante),
            )
            return int(cursor.lastrowid)
    finally:
        conn.close()


def remover_despesa(despesa_id: int) -> bool:
    conn = _connect()
    try:
        with conn:
            cursor = conn.execute("DELETE FROM despesas WHERE id = ?", (despesa_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def obter_resumo_caixa(mes: Optional[str] = None) -> Dict[str, Any]:
    """
    Livro caixa consolidado: arrecadação de cotas, despesas e série mensal.
    """
    mes = mes or buscar_mes_atual()
    conn = _connect()
    try:
        total_pago = float(
            conn.execute(
                "SELECT COALESCE(SUM(valor_pago), 0) FROM pagamentos "
                "WHERE status_pagamento = 'pago'"
            ).fetchone()[0]
        )
        total_despesas = float(
            conn.execute(
                "SELECT COALESCE(SUM(valor), 0) FROM despesas"
            ).fetchone()[0]
        )
        pago_mes = float(
            conn.execute(
                "SELECT COALESCE(SUM(valor_pago), 0) FROM pagamentos "
                "WHERE status_pagamento = 'pago' AND mes = ?",
                (mes,),
            ).fetchone()[0]
        )
        despesas_mes = float(
            conn.execute(
                "SELECT COALESCE(SUM(valor), 0) FROM despesas "
                "WHERE substr(data, 1, 7) = ?",
                (mes,),
            ).fetchone()[0]
        )
        serie_rows = conn.execute(
            """
            SELECT mes,
                   SUM(CASE WHEN status_pagamento = 'pago'
                            THEN valor_pago ELSE 0 END) AS arrecadado,
                   SUM(CASE WHEN status_pagamento <> 'pago'
                            THEN (CASE WHEN valor_pago > 0
                                       THEN valor_pago ELSE ? END)
                            ELSE 0 END) AS pendente
            FROM pagamentos
            GROUP BY mes
            """,
            (config.VALOR_CONTRIBUICAO,),
        ).fetchall()
        serie_map = {
            row["mes"]: {
                "arrecadado": float(row["arrecadado"] or 0),
                "pendente": float(row["pendente"] or 0),
            }
            for row in serie_rows
        }
        serie = [
            {
                "mes": m,
                "arrecadado": serie_map.get(m, {}).get("arrecadado", 0.0),
                "pendente": serie_map.get(m, {}).get("pendente", 0.0),
            }
            for m in _ultimos_meses(12)
        ]
        pagamentos_recentes = [
            dict(row)
            for row in conn.execute(
                """
                SELECT p.mes, p.valor_pago, p.data_pagamento,
                       m.nome, m.ex_bolsista
                FROM pagamentos p
                JOIN membros m ON m.id = p.membro_id
                WHERE p.status_pagamento = 'pago'
                ORDER BY p.mes DESC, p.id DESC
                LIMIT 12
                """
            ).fetchall()
        ]
        despesas_recentes = [
            dict(row)
            for row in conn.execute(
                """
                SELECT id, descricao, categoria, valor, data, comprovante
                FROM despesas
                ORDER BY data DESC, id DESC
                LIMIT 12
                """
            ).fetchall()
        ]
    finally:
        conn.close()

    for p in pagamentos_recentes:
        p["valor_pago"] = float(p["valor_pago"] or 0)
        p["ex_bolsista"] = bool(p["ex_bolsista"])
    for d in despesas_recentes:
        d["valor"] = float(d["valor"] or 0)

    return {
        "mes": mes,
        "total_pago": total_pago,
        "total_despesas": total_despesas,
        "saldo": total_pago - total_despesas,
        "pago_mes": pago_mes,
        "despesas_mes": despesas_mes,
        "serie": serie,
        "pagamentos_recentes": pagamentos_recentes,
        "despesas_recentes": despesas_recentes,
    }
