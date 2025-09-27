import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional
import config

def init_db():
    """
    Cria as tabelas do banco de dados se não existirem.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Criar tabela de membros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telegram_id INTEGER UNIQUE NOT NULL
        )
    ''')
    
    # Criar tabela de pagamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            membro_id INTEGER NOT NULL,
            mes TEXT NOT NULL,
            valor_pago REAL NOT NULL,
            quitado BOOLEAN NOT NULL DEFAULT 0,
            data_pagamento TEXT,
            FOREIGN KEY (membro_id) REFERENCES membros (id),
            UNIQUE(membro_id, mes)
        )
    ''')
    
    conn.commit()
    conn.close()

def adicionar_membro(nome: str, telegram_id: int) -> bool:
    """
    Adiciona um novo membro ao banco de dados.
    Retorna True se adicionado com sucesso, False se já existir.
    """
    try:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO membros (nome, telegram_id)
            VALUES (?, ?)
        ''', (nome, telegram_id))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Membro já existe
        return False

def buscar_membro_por_telegram_id(telegram_id: int) -> Optional[Tuple[int, str, int]]:
    """
    Busca um membro pelo ID do Telegram.
    Retorna (id, nome, telegram_id) ou None se não encontrar.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, nome, telegram_id FROM membros
        WHERE telegram_id = ?
    ''', (telegram_id,))
    
    resultado = cursor.fetchone()
    conn.close()
    
    return resultado

def buscar_todos_membros() -> List[Tuple[int, str, int]]:
    """
    Retorna lista de todos os membros: [(id, nome, telegram_id), ...]
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, nome, telegram_id FROM membros')
    resultado = cursor.fetchall()
    conn.close()
    
    return resultado

def criar_cobranca_mensal(mes: str) -> int:
    """
    Cria cobranças para todos os membros para o mês especificado.
    Retorna o número de cobranças criadas.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Buscar todos os membros
    cursor.execute('SELECT id FROM membros')
    membros = cursor.fetchall()
    
    cobranças_criadas = 0
    
    for (membro_id,) in membros:
        try:
            cursor.execute('''
                INSERT INTO pagamentos (membro_id, mes, valor_pago, quitado)
                VALUES (?, ?, ?, 0)
            ''', (membro_id, mes, config.VALOR_CONTRIBUICAO))
            cobranças_criadas += 1
        except sqlite3.IntegrityError:
            # Cobrança já existe para este membro/mês
            pass
    
    conn.commit()
    conn.close()
    
    return cobranças_criadas

def marcar_pagamento(telegram_id: int, mes: str) -> bool:
    """
    Marca um pagamento como quitado para um membro específico.
    Retorna True se marcado com sucesso, False se não encontrar.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Buscar o membro
    membro = buscar_membro_por_telegram_id(telegram_id)
    if not membro:
        conn.close()
        return False
    
    membro_id = membro[0]
    
    # Marcar como pago
    cursor.execute('''
        UPDATE pagamentos 
        SET quitado = 1, data_pagamento = ?
        WHERE membro_id = ? AND mes = ?
    ''', (datetime.now().isoformat(), membro_id, mes))
    
    alterado = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return alterado

def buscar_dividas(telegram_id: int) -> List[Tuple[str, float]]:
    """
    Busca todas as dívidas (meses não pagos) de um membro.
    Retorna lista de (mes, valor) não quitados.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Buscar o membro
    membro = buscar_membro_por_telegram_id(telegram_id)
    if not membro:
        conn.close()
        return []
    
    membro_id = membro[0]
    
    cursor.execute('''
        SELECT mes, valor_pago FROM pagamentos
        WHERE membro_id = ? AND quitado = 0
        ORDER BY mes
    ''', (membro_id,))
    
    resultado = cursor.fetchall()
    conn.close()
    
    return resultado

def buscar_pagamentos_mes_atual(mes: str) -> List[Tuple[str, bool]]:
    """
    Busca quem já pagou no mês especificado.
    Retorna lista de (nome_membro, quitado).
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.nome, p.quitado
        FROM membros m
        JOIN pagamentos p ON m.id = p.membro_id
        WHERE p.mes = ?
        ORDER BY m.nome
    ''', (mes,))
    
    resultado = cursor.fetchall()
    conn.close()
    
    return resultado

def buscar_mes_atual() -> str:
    """
    Retorna o mês atual no formato YYYY-MM.
    """
    return datetime.now().strftime("%Y-%m")

def adicionar_divida_manual(telegram_id: int, mes: str, valor: float) -> bool:
    """
    Adiciona uma dívida manual para um membro específico.
    Útil para informatizar dívidas históricas.
    Retorna True se adicionado com sucesso, False se já existir ou membro não encontrar.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Buscar o membro
    membro = buscar_membro_por_telegram_id(telegram_id)
    if not membro:
        conn.close()
        return False
    
    membro_id = membro[0]
    
    try:
        cursor.execute('''
            INSERT INTO pagamentos (membro_id, mes, valor_pago, quitado)
            VALUES (?, ?, ?, 0)
        ''', (membro_id, mes, valor))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Dívida já existe para este membro/mês
        conn.close()
        return False

def listar_membros_simples() -> List[Tuple[str, int]]:
    """
    Retorna lista simplificada de membros: [(nome, telegram_id), ...]
    Útil para interfaces administrativas.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT nome, telegram_id FROM membros ORDER BY nome')
    resultado = cursor.fetchall()
    conn.close()
    
    return resultado
