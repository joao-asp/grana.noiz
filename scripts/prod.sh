#!/bin/bash

# 🚀 Deploy para Produção do Bot da Caixinha
# ==========================================
# Este script faz deploy seguro do bot em produção
# CUIDADO: Só execute em servidor de produção, nunca em desenvolvimento
# Faz backup automático antes de atualizar

set -e  # Para no primeiro erro

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploy para Produção${NC}"
echo "========================"
echo ""

# 1. VERIFICAÇÕES DE SEGURANÇA - Para se não estiver tudo certo
echo -e "${YELLOW}🔒 Verificações de segurança...${NC}"

# Verificar branch (só permite deploy da main)
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo -e "${RED}❌ Deploy só pode ser feito da branch main${NC}"
    echo "   Atual: $BRANCH"
    echo "   Execute: git checkout main"
    exit 1
fi
echo -e "${GREEN}✅ Branch main confirmada${NC}"

# Verificar se há mudanças não commitadas
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ Há mudanças não commitadas${NC}"
    echo "   Commit suas mudanças antes do deploy"
    exit 1
fi
echo -e "${GREEN}✅ Nenhuma mudança pendente${NC}"

# Verificar se .env existe e está configurado
if [ ! -f .env ]; then
    echo -e "${RED}❌ Arquivo .env não encontrado!${NC}"
    echo "   Crie: cp .env.example .env e configure"
    exit 1
fi

if grep -q "SEU_TOKEN_AQUI\|your_bot_token_here" .env; then
    echo -e "${RED}❌ Token não configurado em .env${NC}"
    echo "   Configure TELEGRAM_BOT_TOKEN com token real"
    exit 1
fi
echo -e "${GREEN}✅ Configuração .env válida${NC}"

# Verificar Docker
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose não encontrado${NC}"
    echo "   Instale Docker e Docker Compose primeiro"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose disponível${NC}"

echo ""

# 2. BACKUP AUTOMÁTICO - Protege dados antes de atualizar
echo -e "${YELLOW}💾 Fazendo backup dos dados...${NC}"

mkdir -p backup

# Backup do banco se existir
if [ -f data/caixinha.db ]; then
    BACKUP_NAME="caixinha_backup_$(date +%Y%m%d_%H%M%S).db"
    cp data/caixinha.db backup/$BACKUP_NAME
    echo -e "${GREEN}✅ Backup criado: backup/$BACKUP_NAME${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhum banco encontrado para backup${NC}"
fi

# Backup dos logs se existirem
if [ -d logs ] && [ "$(ls -A logs)" ]; then
    tar -czf backup/logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz logs/
    echo -e "${GREEN}✅ Backup dos logs criado${NC}"
fi

echo ""

# 3. DEPLOY - Para e recria os containers
echo -e "${YELLOW}🛑 Parando versão anterior...${NC}"
docker-compose down
echo -e "${GREEN}✅ Containers parados${NC}"

echo -e "${YELLOW}🔨 Construindo nova versão...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✅ Build concluído${NC}"

echo -e "${YELLOW}🚀 Iniciando produção...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ Containers iniciados${NC}"

echo ""

# 4. VERIFICAÇÃO DE SAÚDE - Confirma se funcionou
echo -e "${YELLOW}🏥 Verificando saúde do deploy...${NC}"

# Aguarda containers subirem
sleep 10

# Verifica se containers estão rodando
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Containers ativos${NC}"
    
    # Testa conectividade básica (opcional)
    echo -e "${YELLOW}🔍 Testando bot...${NC}"
    sleep 5  # Aguarda bot inicializar
    
    if docker-compose logs bot-caixinha | grep -q "Bot iniciado\|Application started\|Started polling"; then
        echo -e "${GREEN}✅ Bot funcionando${NC}"
    else
        echo -e "${YELLOW}⚠️  Bot pode estar inicializando ainda${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
    echo ""
    echo -e "${BLUE}📋 Comandos úteis pós-deploy:${NC}"
    echo "   📊 Ver logs: make logs"
    echo "   📊 Status: docker-compose ps"
    echo "   🛡️ Admin: make admin"
    echo "   🔄 Restart: docker-compose restart"
    echo "   ⏹️ Parar: make stop"
    echo ""
    echo -e "${GREEN}💚 Bot em produção e funcionando!${NC}"
    
else
    echo -e "${RED}❌ FALHA NO DEPLOY${NC}"
    echo ""
    echo -e "${YELLOW}🔍 Diagnóstico:${NC}"
    docker-compose ps
    echo ""
    echo -e "${YELLOW}📋 Verificar logs:${NC}"
    echo "   docker-compose logs"
    echo ""
    echo -e "${YELLOW}🔄 Para tentar novamente:${NC}"
    echo "   ./scripts/prod.sh"
    exit 1
fi