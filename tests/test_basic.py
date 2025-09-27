"""
Testes básicos para o Bot da Caixinha
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_config_loading():
    """Testa carregamento de configurações"""
    from src import config
    
    # Verificar se constantes existem
    assert hasattr(config, 'TELEGRAM_BOT_TOKEN')
    assert hasattr(config, 'VALOR_CONTRIBUICAO')
    assert hasattr(config, 'ADMINS')

def test_db_functions_exist():
    """Testa se funções do banco existem"""
    from src.utils import db
    
    # Verificar se funções principais existem
    assert hasattr(db, 'init_db')
    assert hasattr(db, 'adicionar_membro')
    assert hasattr(db, 'buscar_membro_por_telegram_id')
    assert hasattr(db, 'marcar_pagamento')
    assert hasattr(db, 'buscar_dividas')

@pytest.mark.asyncio
async def test_start_command():
    """Testa comando /start"""
    # Este seria um teste mais completo com mock do Telegram
    pass

@pytest.mark.asyncio 
async def test_pagar_command():
    """Testa comando /pagar"""
    # Este seria um teste mais completo
    pass

def test_environment_variables():
    """Testa se variáveis de ambiente são lidas corretamente"""
    with patch.dict('os.environ', {'VALOR_CONTRIBUICAO': '25.0'}):
        # Recarregar config
        import importlib
        from src import config
        importlib.reload(config)
        
        assert config.VALOR_CONTRIBUICAO == 25.0

def test_admin_list_parsing():
    """Testa parsing da lista de administradores"""
    with patch.dict('os.environ', {'ADMINS': '123,456,789'}):
        import importlib
        from src import config
        importlib.reload(config)
        
        assert 123 in config.ADMINS
        assert 456 in config.ADMINS  
        assert 789 in config.ADMINS