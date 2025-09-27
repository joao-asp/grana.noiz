#!/bin/bash

echo "🚀 Deploy para produção..."

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se estamos na branch main
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo -e "${RED}❌ Deploy só pode ser feito da branch main${NC}"
    echo "   Atual: $BRANCH"
    echo "   Execute: git checkout main"
    exit 1
fi

# Verificar se há mudanças não commitadas
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ Há mudanças não commitadas${NC}"
    echo "   Commit ou stash suas mudanças primeiro"
    exit 1
fi

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo "   Copie e configure: cp .env.example .env"
    exit 1
fi

# Verificar se token está configurado
if grep -q "SEU_TOKEN_AQUI" .env; then
    echo -e "${RED}❌ Token não configurado em .env${NC}"
    echo "   Configure o TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Parar versão antiga se existir
echo -e "${YELLOW}⏹️ Parando versão anterior...${NC}"
docker-compose down

# Fazer backup antes do deploy
echo -e "${GREEN}💾 Fazendo backup...${NC}"
if [ -f data/caixinha.db ]; then
    mkdir -p backup
    cp data/caixinha.db backup/caixinha_backup_$(date +%Y%m%d_%H%M%S).db
    echo -e "${GREEN}✅ Backup criado${NC}"
fi

# Build nova versão
echo -e "${GREEN}🔨 Construindo nova versão...${NC}"
docker-compose build --no-cache

# Iniciar
echo -e "${GREEN}🚀 Iniciando produção...${NC}"
docker-compose up -d

# Aguardar subir
echo -e "${GREEN}⏳ Aguardando containers...${NC}"
sleep 10

# Verificar se está rodando
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Bot em produção!${NC}"
    echo ""
    echo -e "${YELLOW}📋 Comandos úteis:${NC}"
    echo "   📊 Ver logs: make logs"
    echo "   🛡️  Admin: make admin"
    echo "   ⏹️ Parar: make stop"
    echo "   📊 Status: make status"
    echo ""
    echo -e "${GREEN}🎉 Deploy concluído com sucesso!${NC}"
else
    echo -e "${RED}❌ Falha no deploy${NC}"
    echo "   Verifique os logs: docker-compose logs"
    exit 1
fi