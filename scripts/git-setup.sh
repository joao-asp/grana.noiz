#!/bin/bash

echo "🌳 Configurando workflow Git..."

# Verificar se já está em um repositório
if [ ! -d ".git" ]; then
    echo "📂 Inicializando repositório Git..."
    git init
    git branch -M main
fi

# Definir branches padrão
echo "🌿 Configurando branches..."

# Criar develop se não existir
if ! git show-ref --verify --quiet refs/heads/develop; then
    git checkout -b develop
    echo "✅ Branch 'develop' criada"
else
    echo "ℹ️  Branch 'develop' já existe"
fi

# Voltar para main
git checkout main

# Configurar hooks
echo "🪝 Configurando Git hooks..."
mkdir -p .git/hooks

# Hook pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "🔍 Executando verificações pre-commit..."

# Verificar se há secrets no código
if grep -r "TELEGRAM_BOT_TOKEN.*[0-9]" src/ --exclude-dir=__pycache__; then
    echo "❌ ERRO: Token do Telegram encontrado no código!"
    echo "   Use variáveis de ambiente (.env) em vez de hardcode"
    exit 1
fi

# Verificar sintaxe Python
python -m py_compile src/*.py src/**/*.py 2>/dev/null || {
    echo "❌ ERRO: Erro de sintaxe Python encontrado"
    exit 1
}

echo "✅ Verificações pre-commit OK"
EOF

# Hook pre-push
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash

echo "🚀 Executando verificações pre-push..."

# Verificar branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ]; then
    echo "⚠️  ATENÇÃO: Você está fazendo push para MAIN"
    read -p "Tem certeza? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Push cancelado"
        exit 1
    fi
fi

echo "✅ Verificações pre-push OK"
EOF

# Tornar hooks executáveis
chmod +x .git/hooks/pre-commit .git/hooks/pre-push

echo "✅ Git workflow configurado!"
echo ""
echo "📋 Branches disponíveis:"
echo "  • main     - Produção (código estável)"
echo "  • develop  - Desenvolvimento (integração)"
echo "  • feature/* - Novas funcionalidades"
echo "  • hotfix/*  - Correções urgentes"
echo ""
echo "🔄 Workflow recomendado:"
echo "  1. git checkout develop"
echo "  2. git checkout -b feature/minha-funcionalidade"
echo "  3. # desenvolver..."
echo "  4. git push origin feature/minha-funcionalidade"
echo "  5. # abrir PR para develop"