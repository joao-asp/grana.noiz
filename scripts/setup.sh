#!/bin/bash

# 🚀 Setup Automático do Bot da Caixinha Coletiva
# ===============================================
# Este script configura tudo que você precisa para rodar o bot
# CUIDADO: Vai criar arquivos e pastas no diretório atual

set -e  # Para no primeiro erro

# Cores para output bonito
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🤖 Bot da Caixinha Coletiva - Setup${NC}"
echo "======================================"
echo ""

# 1. VERIFICAÇÕES - Para antes de começar se algo não estiver instalado
echo -e "${YELLOW}🔍 Verificando dependências...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Instale Python 3.11+ primeiro.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python encontrado${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker não encontrado. Instalação será local.${NC}"
    USE_DOCKER=false
else
    echo -e "${GREEN}✅ Docker encontrado${NC}"
    USE_DOCKER=true
fi

echo ""

# 2. CONFIGURAÇÃO - Cria arquivos necessários
echo -e "${YELLOW}⚙️ Configurando arquivos...${NC}"

# Cria .env se não existir
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Criando .env...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ CONFIGURE SEU TOKEN EM .env ANTES DE CONTINUAR${NC}"
else
    echo -e "${GREEN}✅ .env já existe${NC}"
fi

# Cria pastas necessárias
echo -e "${BLUE}📁 Criando diretórios...${NC}"
mkdir -p data logs backup
echo -e "${GREEN}✅ Diretórios criados${NC}"

echo ""

# 3. DEPENDÊNCIAS - Instala o que precisa
echo -e "${YELLOW}📦 Instalando dependências...${NC}"

if [ "$USE_DOCKER" = true ]; then
    echo -e "${GREEN}🐳 Usando Docker (recomendado)${NC}"
    echo "   As dependências serão instaladas automaticamente"
else
    echo -e "${GREEN}🐍 Instalação local com pip${NC}"
    
    # Cria ambiente virtual se não existir
    if [ ! -d ".venv" ]; then
        echo -e "${BLUE}📦 Criando ambiente virtual...${NC}"
        python3 -m venv .venv
    fi
    
    # Ativa e instala
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependências instaladas${NC}"
fi

echo ""

# 4. INSTRUÇÕES FINAIS - O que fazer depois
echo -e "${BLUE}🎯 Setup concluído!${NC}"
echo ""
echo -e "${YELLOW}📋 Próximos passos OBRIGATÓRIOS:${NC}"
echo ""
echo -e "${RED}1. CONFIGURE SEUS TOKENS EM .env:${NC}"
echo "   - Vá ao @BotFather no Telegram"
echo "   - Crie um bot com /newbot"
echo "   - Cole o token em TELEGRAM_BOT_TOKEN no .env"
echo "   - Use @userinfobot para descobrir seu ID"
echo "   - Cole seu ID em ADMINS no .env"
echo ""

if [ "$USE_DOCKER" = true ]; then
    echo -e "${GREEN}2. EXECUTE O BOT COM DOCKER:${NC}"
    echo "   make dev     # Desenvolvimento"
    echo "   make logs    # Ver se funcionou"
    echo "   make admin   # Painel administrativo"
else
    echo -e "${GREEN}2. EXECUTE O BOT LOCALMENTE:${NC}"
    echo "   source .venv/bin/activate"
    echo "   python -m src.bot"
fi

echo ""
echo -e "${GREEN}3. TESTE NO TELEGRAM:${NC}"
echo "   - Mande /start para seu bot"
echo "   - Use /ajuda para ver comandos"
echo ""
echo -e "${YELLOW}💡 Problemas? Veja README.md ou abra uma issue no GitHub${NC}"
echo ""
echo -e "${GREEN}💚 Pronto para fortalecer seu coletivo!${NC}"