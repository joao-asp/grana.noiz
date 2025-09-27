#!/usr/bin/env python3
"""
Configurações do Bot da Caixinha Coletiva
==========================================

Configure suas variáveis de ambiente ou use arquivo .env
"""

import os
from typing import List
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# ================================
# CONFIGURAÇÕES PRINCIPAIS
# ================================

# Token do bot do Telegram - OBRIGATÓRIO
# Obtenha com @BotFather no Telegram: /newbot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SEU_TOKEN_AQUI")

# Valor padrão da contribuição mensal (em reais)
VALOR_CONTRIBUICAO = float(os.getenv("VALOR_CONTRIBUICAO", "50.0"))

# ================================
# CONFIGURAÇÕES DE COBRANÇA
# ================================

# Quando enviar cobrança automática
COBRANCA_DIA = int(os.getenv("COBRANCA_DIA", "10"))     # Dia do mês (1-31)
COBRANCA_HORA = int(os.getenv("COBRANCA_HORA", "9"))    # Hora do dia (0-23)
COBRANCA_MINUTO = int(os.getenv("COBRANCA_MINUTO", "0")) # Minuto da hora (0-59)

# ================================
# ADMINISTRADORES
# ================================

# Lista de IDs do Telegram que podem usar comandos de admin
# Para descobrir seu ID, use @userinfobot no Telegram
ADMINS_STRING = os.getenv("ADMINS", "")
ADMINS: List[int] = []
if ADMINS_STRING:
    try:
        ADMINS = [int(x.strip()) for x in ADMINS_STRING.split(",") if x.strip()]
    except ValueError:
        print("⚠️  AVISO: IDs de administradores inválidos em ADMINS")

# ================================
# CONFIGURAÇÕES DO BANCO
# ================================

# Caminho para o arquivo do banco SQLite
DB_PATH = os.getenv("DB_PATH", "data/caixinha.db")

# ================================
# CONFIGURAÇÕES AVANÇADAS
# ================================

# Fuso horário (para logs e agendamentos)
TIMEZONE = os.getenv("TIMEZONE", "America/Sao_Paulo")

# Formato de data para exibição
DATE_FORMAT = "%d/%m/%Y"
MONTH_FORMAT = "%B/%Y"

# Ambiente (development, production)
ENV = os.getenv("ENV", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
