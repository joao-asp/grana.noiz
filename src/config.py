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
# A cota da ITCP é R$ 5,00 (uma cota por mês por bolsista ativo).
VALOR_CONTRIBUICAO = float(os.getenv("VALOR_CONTRIBUICAO", "5.0"))

# ================================
# INTERFACE WEB
# ================================

# Servidor HTTP embutido (sem framework): http://localhost:8080
WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
WEB_PORT = int(os.getenv("WEB_PORT", "8080"))

# URL pública exibida no bot (ajuste para o domínio em produção)
WEB_PUBLIC_URL = os.getenv("WEB_PUBLIC_URL", "http://localhost:8080")

# Credenciais do painel /admin.
# Prefira WEB_ADMIN_PASSWORD_HASH em produção; WEB_ADMIN_PASSWORD é o fallback
# simples para desenvolvimento local.
WEB_ADMIN_USER = os.getenv("WEB_ADMIN_USER", "admin")
WEB_ADMIN_PASSWORD = os.getenv("WEB_ADMIN_PASSWORD", "")
WEB_ADMIN_PASSWORD_HASH = os.getenv("WEB_ADMIN_PASSWORD_HASH", "")

# Token opcional para scripts/curl (não é usado pelo formulário de login).
WEB_ADMIN_TOKEN = os.getenv("WEB_ADMIN_TOKEN", "")

# Sessão do painel admin
WEB_SESSION_TTL_HOURS = int(os.getenv("WEB_SESSION_TTL_HOURS", "12"))
WEB_COOKIE_SECURE = os.getenv("WEB_COOKIE_SECURE", "false").lower() == "true"

# Chave Pix exibida na área do membro (opcional).
PIX_CHAVE = os.getenv("PIX_CHAVE", "")

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

# Raiz do projeto (funciona tanto com "python -m src.bot" quanto com
# execução direta a partir de src/).
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _caminho_local(valor: str) -> str:
    """Resolve caminhos relativos contra a raiz do projeto."""
    return valor if os.path.isabs(valor) else os.path.join(BASE_DIR, valor)


# Caminho para o arquivo do banco SQLite
DB_PATH = _caminho_local(os.getenv("DB_PATH", "data/caixinha.db"))

# Diretório padrão dos arquivos CSV de carga legada.
# Pode ser sobrescrito por LEGADO_DIR ou pelos argumentos do script.
LEGADO_DIR = _caminho_local(os.getenv("LEGADO_DIR", "data/legado"))

# Nomes canônicos dos arquivos de carga legada
CSV_MEMBROS = _caminho_local(
    os.getenv(
        "CSV_MEMBROS",
        os.path.join(LEGADO_DIR, "cotizacoes_itcp_ativos_e_ex_bolsistas.csv"),
    )
)
CSV_LANCAMENTOS = _caminho_local(
    os.getenv(
        "CSV_LANCAMENTOS",
        os.path.join(LEGADO_DIR, "carga_lancamentos_mensais_grana_noiz.csv"),
    )
)

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
