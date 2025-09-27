#!/bin/bash

# 🧹 Reset Completo do Bot da Caixinha
# ====================================
# CUIDADO: Este script vai DELETAR todos os dados do bot!
# Use apenas para desenvolvimento ou quando quiser começar do zero
# TODOS os pagamentos e registros serão perdidos permanentemente

set -e  # Para no primeiro erro

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}⚠️  ATENÇÃO: RESET COMPLETO DO BOT${NC}"
echo "====================================="
echo ""
echo -e "${RED}Este script vai deletar:${NC}"
echo "• Banco de dados (todos os pagamentos)"
echo "• Logs do sistema"
echo "• Backups automáticos"
echo "• Cache Python"
echo ""

# Confirmação de segurança
read -p "Tem CERTEZA que quer continuar? Digite 'RESET' para confirmar: " confirmation
if [ "$confirmation" != "RESET" ]; then
    echo -e "${GREEN}Operação cancelada. Nada foi deletado.${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}🛑 Parando bot se estiver rodando...${NC}"

# Parar containers Docker
if command -v docker-compose &> /dev/null; then
    docker-compose down 2>/dev/null || true
    echo -e "${GREEN}✅ Containers Docker parados${NC}"
fi

# Parar processos Python
pkill -f "python.*src.bot" 2>/dev/null || true
pkill -f "python.*src/bot.py" 2>/dev/null || true
echo -e "${GREEN}✅ Processos Python parados${NC}"

echo ""
echo -e "${YELLOW}🗃️ Removendo dados...${NC}"

# Remover banco de dados
rm -f data/caixinha.db 2>/dev/null || true
rm -f caixinha.db 2>/dev/null || true  # Compatibilidade com versão antiga
echo -e "${GREEN}✅ Banco de dados removido${NC}"

# Remover logs
rm -rf logs/* 2>/dev/null || true
echo -e "${GREEN}✅ Logs limpos${NC}"

# Remover backups
rm -rf backup/* 2>/dev/null || true
echo -e "${GREEN}✅ Backups removidos${NC}"

echo ""
echo -e "${YELLOW}🧽 Limpando cache...${NC}"

# Limpar cache Python
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Cache Python limpo${NC}"

# Limpar volumes Docker se existirem
if command -v docker &> /dev/null; then
    docker system prune -f --volumes 2>/dev/null || true
    echo -e "${GREEN}✅ Volumes Docker limpos${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Reset completo realizado!${NC}"
echo ""
echo -e "${YELLOW}� Para usar o bot novamente:${NC}"
echo "1. Configure o .env se não estiver configurado"
echo "2. Execute: make dev (Docker) ou python -m src.bot (local)"
echo "3. Teste no Telegram com /start"
echo "4. O banco será criado automaticamente no primeiro uso"
echo ""
echo -e "${GREEN}💚 Bot está limpo e pronto para recomeçar!${NC}"
