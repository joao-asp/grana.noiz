# 🤖 Bot da Caixinha Coletiva

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://www.docker.com)
[![License](https://img.shields.io/badge/license-AGPL--3.0-red.svg)](LICENSE)

Bot do Telegram para gerenciar contribuições mensais de coletivos de forma organizada e transparente.

##  Funcionalidades

- 🔐 Cadastro automático de membros
- 💰 Registro de pagamentos mensais
- 📊 Consulta de dívidas individuais
- ⏰ Cobrança automática programável
- 🛡️ Painel administrativo
- 🐳 Deploy com Docker

## 🚀 Início Rápido

### 1. Configure o Bot no Telegram
1. Converse com @BotFather no Telegram
2. Use `/newbot` e siga as instruções
3. Copie o token gerado

### 2. Execute o Bot

**Com Docker (Recomendado):**
```bash
git clone https://github.com/SEU_USUARIO/bot-caixinha-telegram.git
cd bot-caixinha-telegram
cp .env.example .env
# Edite .env com seu token
make dev
```

**Sem Docker:**
```bash
git clone https://github.com/SEU_USUARIO/bot-caixinha-telegram.git
cd bot-caixinha-telegram
pip install -r requirements.txt
cp .env.example .env
# Edite .env com seu token
python -m src.bot
```

## 📋 Comandos do Bot

**Para todos:**
- `/start` - Cadastro e boas-vindas
- `/pagar` - Marcar pagamento do mês atual  
- `/divida` - Ver dívidas pendentes
- `/paguei 2025-01` - Marcar mês específico

**Para administradores:**
- `/status` - Ver quem pagou no mês
- `/divida_manual <id> <mes> <valor>` - Adicionar dívida

## ⚙️ Configuração

### Descobrir seu ID do Telegram
1. Converse com @userinfobot no Telegram
2. Copie seu ID numérico para `ADMINS` no arquivo `.env`

### Personalizar
Edite o arquivo `.env`:
```bash
TELEGRAM_BOT_TOKEN=seu_token_aqui
VALOR_CONTRIBUICAO=50.0
ADMINS=seu_id_aqui
COBRANCA_DIA=10
COBRANCA_HORA=9
```

## 🛠️ Comandos de Desenvolvimento

```bash
make help     # Ver todos os comandos
make dev      # Ambiente de desenvolvimento
make prod     # Produção
make logs     # Ver logs
make admin    # Painel administrativo
make clean    # Limpar ambiente
```

## 📁 Estrutura

```
bot-caixinha-telegram/
├── src/
│   ├── bot.py          # Bot principal
│   ├── config.py       # Configurações
│   ├── admin.py        # Painel admin
│   └── utils/db.py     # Banco de dados
├── scripts/            # Scripts úteis
├── Makefile           # Comandos
└── .env.example       # Template config
```

## 📊 Como Funciona

O bot executa automaticamente todo **dia 10 às 9h**:
1. Cria cobranças do mês para todos os membros
2. Envia lembretes para quem tem pendências
3. Lista dívida atual + meses em atraso

## 🆘 Problemas Comuns

**Bot não responde:**
```bash
# Verificar logs
make logs

# Reiniciar
make clean && make dev
```

**Token inválido:**
- Verifique o arquivo `.env`
- Confirme o token com @BotFather

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Faça commit: `git commit -m 'Adicionar funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto usa AGPL-3.0 - uma licença com copyleft forte para proteger o trabalho coletivo. Veja [LICENSE](LICENSE) para detalhes.

---

💚 **Feito com amor para fortalecer coletivos!**
