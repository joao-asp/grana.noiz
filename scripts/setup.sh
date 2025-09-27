#!/bin/bash

# 🚀 Setup Completo do Bot da Caixinha
# ====================================

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "🤖 ======================================"  
echo "    BOT DA CAIXINHA COLETIVA - SETUP"
echo "======================================${NC}"
echo ""

# 1. Verificações iniciais
echo -e "${YELLOW}🔍 1. Verificações iniciais...${NC}"

# Verificar Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git não encontrado. Instale o Git primeiro.${NC}"
    exit 1
fi

# Verificar Docker (opcional)
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker encontrado${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  Docker não encontrado (desenvolvimento será local)${NC}"
    DOCKER_AVAILABLE=false
fi

# Verificar Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python encontrado${NC}"
else
    echo -e "${RED}❌ Python 3 não encontrado. Instale Python 3.11+ primeiro.${NC}"
    exit 1
fi

echo ""

# 2. Configurar Git
echo -e "${YELLOW}🌳 2. Configurando Git...${NC}"
./scripts/git-setup.sh

echo ""

# 3. Configurar ambiente
echo -e "${YELLOW}⚙️ 3. Configurando ambiente...${NC}"

if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Criando arquivo .env...${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Configure seu token em .env${NC}"
fi

if [ ! -f .env.dev ]; then
    echo -e "${BLUE}📝 Criando arquivo .env.dev...${NC}"
    cp .env.dev.example .env.dev
    echo -e "${RED}❗ Configure seu token de teste em .env.dev${NC}"
fi

# Criar diretórios
mkdir -p data logs backup

echo ""

# 4. Instalar dependências
echo -e "${YELLOW}📦 4. Instalando dependências...${NC}"

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "${GREEN}🐳 Usando Docker...${NC}"
    # Docker irá instalar as dependências automaticamente
else
    echo -e "${GREEN}🐍 Instalando com pip...${NC}"
    if [ ! -d ".venv" ]; then
        echo -e "${BLUE}📦 Criando ambiente virtual...${NC}"
        python3 -m venv .venv
    fi
    
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
fi

echo ""

# 5. Testar configuração
echo -e "${YELLOW}🧪 5. Testando configuração...${NC}"

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo -e "${GREEN}🐳 Testando com Docker...${NC}"
    docker-compose -f docker-compose.dev.yml config > /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Configuração Docker válida${NC}"
    else
        echo -e "${RED}❌ Erro na configuração Docker${NC}"
    fi
else
    echo -e "${GREEN}🐍 Testando imports Python...${NC}"
    source .venv/bin/activate
    python3 -c "import sys; sys.path.append('src'); import config; print('✅ Config OK')"
fi

echo ""

# 6. Mostrar instruções finais
echo -e "${BLUE}🎯 Setup concluído!${NC}"
echo ""
echo -e "${YELLOW}📋 Próximos passos:${NC}"
echo ""
echo -e "${GREEN}1. Configure seus tokens:${NC}"
echo "   - Edite .env com token de produção"
echo "   - Edite .env.dev com token de teste"
echo "   - Adicione seu ID do Telegram em ADMINS"
echo ""
echo -e "${GREEN}2. Execute o bot:${NC}"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "   🐳 Com Docker:"
    echo "      make dev     # Desenvolvimento"
    echo "      make prod    # Produção"
    echo "      make logs    # Ver logs"
    echo "      make admin   # Painel admin"
else
    echo "   🐍 Local:"
    echo "      source .venv/bin/activate"
    echo "      python -m src.bot"
fi
echo ""
echo -e "${GREEN}3. Comandos úteis:${NC}"
echo "   make help      # Ver todos os comandos"
echo "   make test      # Executar testes"
echo "   make clean     # Limpar ambiente"
echo ""
echo -e "${GREEN}4. Para contribuir:${NC}"
echo "   git checkout -b feature/minha-funcionalidade"
echo "   # desenvolver..."
echo "   git push origin feature/minha-funcionalidade"
echo ""
echo -e "${BLUE}🎉 Bot da Caixinha está pronto para uso!${NC}"
echo ""
echo -e "${YELLOW}💡 Dicas:${NC}"
echo "   - Leia o CONTRIBUTING.md para contribuir"
echo "   - Use @BotFather para criar seu bot no Telegram"
echo "   - Use @userinfobot para descobrir seu ID"
echo "   - Mantenha seus tokens em segredo!"
echo ""
echo -e "${GREEN}💚 Feito com amor para fortalecer coletivos!${NC}"