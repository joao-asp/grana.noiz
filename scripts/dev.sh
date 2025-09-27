#!/bin/bash

echo "🛠️  Iniciando ambiente de desenvolvimento..."

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando${NC}"
    echo "   Inicie o Docker Desktop primeiro"
    exit 1
fi

# Verificar se existe docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose não encontrado${NC}"
    echo "   Instale o Docker Compose primeiro"
    exit 1
fi

# Criar arquivo .env.dev se não existir
if [ ! -f .env.dev ]; then
    echo -e "${YELLOW}📝 Criando .env.dev...${NC}"
    cp .env.dev.example .env.dev
    echo -e "${RED}❗ Configure seu token em .env.dev antes de continuar!${NC}"
    read -p "Pressione Enter após configurar..."
fi

# Criar diretórios necessários
echo -e "${GREEN}📁 Criando diretórios...${NC}"
mkdir -p data logs backup

# Build e start
echo -e "${GREEN}🐳 Construindo e iniciando containers...${NC}"
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d

# Aguardar containers subirem
echo -e "${GREEN}⏳ Aguardando containers...${NC}"
sleep 5

# Verificar se está rodando
if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Ambiente de desenvolvimento iniciado!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Comandos úteis:${NC}"
    echo "   📊 Ver logs: make logs"
    echo "   🛑 Parar: make stop"  
    echo "   🛡️  Admin: make admin"
    echo "   🧪 Testes: make test"
    echo ""
    echo -e "${GREEN}🤖 Bot rodando em modo desenvolvimento!${NC}"
else
    echo -e "${RED}❌ Falha ao iniciar containers${NC}"
    echo "   Verifique os logs: docker-compose -f docker-compose.dev.yml logs"
    exit 1
fi