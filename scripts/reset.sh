#!/bin/bash

# Script para resetar completamente o bot da caixinha
echo "🧹 Reset Completo do Bot da Caixinha"
echo "===================================="

# Parar bot se estiver rodando
echo "🛑 Parando bot..."
pkill -f "python.*main.py" 2>/dev/null || true

# Remover banco de dados
echo "🗃️  Removendo banco de dados antigo..."
rm -f caixinha.db
rm -f backup/caixinha_backup_*.db 2>/dev/null || true

# Limpar cache Python
echo "🧽 Limpando cache..."
rm -rf __pycache__/
find . -name "*.pyc" -delete 2>/dev/null || true

# Recriar banco limpo
echo "✨ Criando banco de dados limpo..."
python3 -c "import db; db.init_db(); print('✅ Banco inicializado')"

echo ""
echo "✅ Reset completo realizado!"
echo ""
echo "🚀 Para usar o bot:"
echo "1. Execute: python3 main.py"
echo "2. Teste no Telegram com /start"
echo "3. Use admin.py para gerenciar dados"
