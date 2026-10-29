# grana.noiz

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://www.docker.com)
[![License](https://img.shields.io/badge/license-AGPL--3.0-red.svg)](LICENSE)

Sistema baseado no Telegram para gestão financeira, transparência e automação
de cobranças para coletivos e organizações autônomas.

## Funcionalidades

- 🔐 Cadastro automático de membros e vínculo por RA
- 💰 Registro de pagamentos com auditoria (`aguardando_auditoria`)
- 📊 Consulta de dívidas individuais e balanço ativos/ex-bolsistas
- ⏰ Cobrança automática programável
- 🛡️ Painel administrativo (CLI e web)
- 🌐 Interface web mobile-first e responsiva para desktop
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
# Edite .env com o token do bot, a senha do /admin e o WEB_PUBLIC_URL
make dev
# Bot: em execução | Web: http://localhost:8080
```

**Sem Docker:**
```bash
git clone https://github.com/SEU_USUARIO/bot-caixinha-telegram.git
cd bot-caixinha-telegram
pip install -r requirements.txt
cp .env.example .env
# Edite .env com o token do bot, a senha do /admin e o WEB_PUBLIC_URL
python -m src.bot     # bot
python -m src.web     # painel em http://localhost:8080
```

## 🌐 Interface web

O painel é servido por um HTTP server da biblioteca padrão (sem framework
adicional) e lê o mesmo SQLite do bot. A interface é **mobile-first**, com
bottom navigation no celular e sidebar + grid no desktop.

Telas públicas:
- **Início** — identificação por **RA** logo no topo: a pessoa vê o total em
  aberto, os meses pendentes, o histórico e pode avisar o pagamento de um mês
  específico (entra em auditoria).
- **Coletivo / Transparência** — apenas pessoas **ativas**, adesão do mês e
  saúde geral. **Não expõe nomes de quem está devendo nem valores individuais.**
  Ex-bolsistas ficam arquivados no histórico interno e não aparecem na lista.
- **Caixa** — arrecadação, despesas, saldo, gráfico dos últimos 12 meses.
  As cotas recebidas aparecem de forma anônima (“Cota recebida”).
- **Assistente** — respostas determinísticas com os dados reais (sua dívida
  via RA, adesão agregada, saldo, Pix, próxima cobrança), sem LLM/custo externo.

### 🔒 Painel da gestão em `/admin`

O painel administrativo é uma **rota oculta**, sem link no site público e com
`noindex`/`robots.txt` bloqueando indexação:

```
http://localhost:8080/admin
```

O login usa usuário e senha (`WEB_ADMIN_USER` / `WEB_ADMIN_PASSWORD` no
`.env`). A sessão fica em cookie HttpOnly + SameSite=Strict, com expiração
configurável. Após entrar, a gestão pode:

- aprovar/rejeitar pagamentos em auditoria;
- gerar cobranças do mês;
- cadastrar pessoas e vincular Telegram;
- ver detalhes financeiros individuais;
- lançar/remover despesas;
- **disparar cobranças no Telegram** para bolsistas ativos com pendência e
  Telegram vinculado (mensagem humana, sem marcar pagamento automaticamente);
- filtrar **ex-bolsistas arquivados** e exportar a lista em CSV
  (`/api/admin/membros/ex-bolsistas.csv`).

Para ver a senha inicial gerada localmente:

```bash
grep '^WEB_ADMIN_PASSWORD=' .env
```

Para produção, prefira um hash PBKDF2:

```bash
python -c "from src.web import gerar_hash_senha; print(gerar_hash_senha('SUA_SENHA'))"
```

e coloque o resultado em `WEB_ADMIN_PASSWORD_HASH`, deixando
`WEB_ADMIN_PASSWORD` vazio.

Em produção, exponha o painel atrás de HTTPS (reverse proxy), defina
`WEB_COOKIE_SECURE=true` e use uma senha forte. O servidor não abre CORS e
exige `Content-Type: application/json` nas escritas.

```bash
make web          # rodar a web localmente
make web-docker   # subir apenas o serviço web no Docker
make web-logs     # logs da web
```

## 📋 Comandos do Bot

**Para todos:**
- `/start` - Cadastro e boas-vindas
- `/vincular <RA>` - Vincular o Telegram ao cadastro legado da ITCP
- `/pagar` - Solicitar baixa do mês atual (fica `aguardando_auditoria`)
- `/divida` - Ver pendências em aberto e em auditoria
- `/paguei 2025-01` - Solicitar baixa de um mês específico

**Para administradores:**
- `/status` - Balanço de bolsistas ativos, ex-bolsistas e auditoria
- `/divida_manual <id> <mes> <valor>` - Adicionar dívida
- `make admin` - Aprovar pagamentos, listar ex-bolsistas e vincular Telegram

## ⚙️ Configuração

### Descobrir seu ID do Telegram
1. Converse com @userinfobot no Telegram
2. Copie seu ID numérico para `ADMINS` no arquivo `.env`

### Personalizar
Edite o arquivo `.env`:
```bash
TELEGRAM_BOT_TOKEN=seu_token_aqui
VALOR_CONTRIBUICAO=5.0
ADMINS=seu_id_aqui
COBRANCA_DIA=10
COBRANCA_HORA=9

# Interface web
WEB_HOST=0.0.0.0
WEB_PORT=8080
WEB_PUBLIC_URL=http://localhost:8080

# Login do painel oculto /admin
WEB_ADMIN_USER=admin
WEB_ADMIN_PASSWORD=uma-senha-forte
# Opcional/recomendado: hash PBKDF2 no lugar da senha em texto
WEB_ADMIN_PASSWORD_HASH=
WEB_SESSION_TTL_HOURS=12
WEB_COOKIE_SECURE=false

# Token opcional para scripts/curl (não é o login do painel)
WEB_ADMIN_TOKEN=

PIX_CHAVE=sua-chave-pix
```

Gere uma senha forte para o painel com:

```bash
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

Depois reinicie a web para o `.env` ser recarregado.

## 📥 Carga do histórico legado

Coloque os CSVs em `data/legado/` (ou informe os caminhos via `ARGS`):

```bash
make import-legado          # ambiente local (.venv quando existir)
make import-legado-docker   # via docker-compose run
```

O script `scripts/importar_legado.py` é idempotente: localiza membros por RA
(ou nome normalizado, quando não há RA) e faz UPSERT dos lançamentos pela
chave `(membro_id, mes)`. Ao final, imprime um relatório com cotas pagas e
saldo devedor separados entre ativos e ex-bolsistas.

## 🛠️ Comandos de Desenvolvimento

```bash
make help             # Ver todos os comandos
make dev              # Bot + web em desenvolvimento
make prod             # Bot + web em produção
make web              # Rodar só a interface web (local)
make web-docker       # Subir só a web no Docker
make logs             # Ver logs de bot e web
make admin            # Painel administrativo CLI
make import-legado    # Carga do histórico legado
make clean            # Limpar ambiente
```

## 📁 Estrutura

```
bot-caixinha-telegram/
├── src/
│   ├── bot.py              # Bot principal
│   ├── web.py              # HTTP server + API JSON
│   ├── config.py           # Configurações
│   ├── admin.py            # Painel admin CLI
│   └── utils/db.py         # Banco de dados + migrações
├── web/
│   ├── index.html          # Shell da SPA
│   ├── styles.css          # Design mobile-first + desktop
│   └── app.js              # Rotas, telas e chamadas de API
├── scripts/
│   └── importar_legado.py  # Carga idempotente dos CSVs
├── data/legado/            # CSVs de carga (não versionados)
├── Makefile                # Comandos
└── .env.example            # Template config
```

## 📊 Como Funciona

O bot executa automaticamente todo **dia 10 às 9h**:
1. Cria cobranças do mês apenas para bolsistas ativos (`ex_bolsista = 0`)
2. Envia lembretes para quem tem pendências
3. Lista dívida atual + meses em atraso

O bot e a web compartilham o mesmo SQLite em modo **WAL**, permitindo leitura
concorrente enquanto um dos processos grava.

Ex-bolsistas permanecem no banco para preservar o histórico, mas **não**
recebem novas cobranças automáticas. Pagamentos informados pelo bot ficam
como `aguardando_auditoria` até a conferência no painel admin.

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
