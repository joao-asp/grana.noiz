# 🤖 Bot da Caixinha Coletiva

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://www.docker.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Bot do Telegram para gerenciar contribuições mensais de coletivos de forma organizada, transparente e automatizada.

## ✨ Funcionalidades

- 🔐 **Cadastro automático** de membros via Telegram
- 💰 **Registro de pagamentos** mensais simplificado  
- 📊 **Consulta de dívidas** individuais
- ⏰ **Cobrança automática** mensal programável
- 🛡️ **Painel administrativo** para gestão avançada
- 📱 **Interface intuitiva** via comandos do Telegram
- 🐳 **Docker** para deploy fácil e reprodutível

## 🚀 Início Rápido

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/bot-caixinha-telegram.git
cd bot-caixinha-telegram

# Configure o ambiente
cp .env.example .env
# Edite .env com seu token do @BotFather

# Execute
docker-compose up -d

# Veja os logs
docker-compose logs -f
```

### Opção 2: Python Local

```bash
# Clone e configure
git clone https://github.com/SEU_USUARIO/bot-caixinha-telegram.git
cd bot-caixinha-telegram

# Instale dependências
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edite .env com suas configurações

# Execute
python -m src.bot
```

## 📋 Comandos do Bot

### Para Todos os Membros:
- `/start` - Cadastro automático e boas-vindas
- `/pagar` - Marcar pagamento do mês atual  
- `/divida` - Ver dívidas pendentes
- `/paguei 2025-01` - Marcar mês específico

### Para Administradores:
- `/status` - Ver quem pagou no mês
- `/divida_manual <id> <mes> <valor>` - Adicionar dívida histórica

## ⚙️ Configuração

### 1. Token do Bot
1. Converse com @BotFather no Telegram
2. Use `/newbot` e siga as instruções
3. Copie o token para o arquivo `.env`

### 2. Descobrir seu ID
1. Converse com @userinfobot no Telegram
2. Copie seu ID numérico para `ADMINS` no `.env`

### 3. Personalizar
Edite as configurações no `.env`:
```bash
VALOR_CONTRIBUICAO=50.0    # Valor mensal
COBRANCA_DIA=10           # Dia da cobrança automática
COBRANCA_HORA=9           # Horário da cobrança
```

## 🛠️ Desenvolvimento

### Setup Local
```bash
# Clone e entre na pasta
git clone <repo> && cd bot-caixinha-telegram

# Configure Git workflow
./scripts/git-setup.sh

# Configure ambiente de desenvolvimento
cp .env.dev.example .env.dev
# Edite .env.dev com token de teste

# Execute desenvolvimento
make dev
```

### Comandos Úteis
```bash
make dev      # Ambiente de desenvolvimento
make prod     # Deploy produção  
make test     # Executar testes
make clean    # Limpar containers
make admin    # Painel administrativo
make logs     # Ver logs em tempo real
```

### Workflow Git
```bash
# Desenvolvimento
git checkout develop
git checkout -b feature/minha-funcionalidade
# ... desenvolver ...
git push origin feature/minha-funcionalidade

# Produção (só após PR aprovado)
git checkout main
make prod
```

## 📁 Estrutura do Projeto

```
bot-caixinha-telegram/
├── src/                    # Código fonte
│   ├── bot.py             # Bot principal
│   ├── config.py          # Configurações (sem secrets!)
│   ├── admin.py           # Painel administrativo
│   └── utils/
│       └── db.py          # Gerenciamento banco SQLite
├── scripts/               # Scripts utilitários
├── docs/                  # Documentação
├── tests/                 # Testes automatizados
├── data/                  # Banco de dados (ignorado)
├── logs/                  # Logs (ignorado)
├── backup/                # Backups (ignorado)
├── docker-compose.yml     # Produção
├── docker-compose.dev.yml # Desenvolvimento
├── Makefile              # Comandos rápidos
└── .env.example          # Template configuração
```

## 🔒 Segurança

- ✅ **Tokens protegidos** - Nunca commitados no Git
- ✅ **Dados sensíveis** - Armazenados em volumes Docker
- ✅ **Comandos admin** - Restritos por ID do Telegram  
- ✅ **Backup automático** - Proteção contra perda de dados
- ✅ **Git hooks** - Previnem commit de secrets

## 📊 Cobrança Automática

O bot executa automaticamente **todo dia 10 às 9h**:
1. Cria cobranças do mês para todos os membros
2. Envia mensagem privada para quem tem pendências
3. Lista dívida atual + meses em atraso
4. Registra logs da operação

## 🆘 Resolução de Problemas

### Bot não responde
```bash
# Verificar se está rodando
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart
```

### Configuração incorreta
```bash
# Verificar arquivo .env
cat .env

# Recriar configuração
cp .env.example .env
# Editar novamente
```

### Limpar tudo
```bash
make clean
docker-compose down --volumes
```

## 🤝 Contribuindo

Adoramos contribuições! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/sua-funcionalidade`
3. Commit: `git commit -m 'Adicionar funcionalidade'`
4. Push: `git push origin feature/sua-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Veja [LICENSE](LICENSE) para detalhes.

## 💚 Filosofia

Este bot foi criado para **fortalecer a organização coletiva**. Acreditamos que a transparência e a facilidade de uso são fundamentais para manter coletivos financeiramente saudáveis e organizados.

---

**Feito com ❤️ para coletivos que transformam o mundo**