#!/bin/bash

# Script de instalação do Bot da Caixinha Coletiva
# Este script automatiza a configuração inicial do projeto

echo "🤖 Instalador do Bot da Caixinha Coletiva"
echo "========================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "⚙️  Criando arquivo de configuração..."
    cp .env.exemplo .env
    echo "📝 Edite o arquivo .env com suas configurações!"
fi

# Inicializar banco de dados
echo "🗃️  Inicializando banco de dados..."
python admin.py << EOF
7
EOF

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Edite o arquivo .env com o token do seu bot"
echo "2. Execute: python main.py"
echo "3. Converse com seu bot no Telegram!"
echo ""
echo "💡 Use 'python admin.py' para gerenciar membros e dados."

# Desativar ambiente virtual
deactivate
