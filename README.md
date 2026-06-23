```markdown
# grana.noiz

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![Docker](https://img.shields.io/badge/docker-ready-green.svg)](https://www.docker.com)
[![License](https://img.shields.io/badge/license-AGPL--3.0-red.svg)](LICENSE)

Sistema baseado no Telegram para gestão financeira, transparência e automação de cobranças para coletivos e organizações autônomas.

## Recursos

- **Gestão de Membros:** Cadastro descentralizado via interação com o bot.
- **Controle Financeiro:** Registro de pagamentos mensais, entradas e saídas.
- **Transparência:** Consulta em tempo real de dívidas individuais e status da caixinha.
- **Automação (Cron):** Rotinas programáveis de cobrança e notificação de pendências.
- **Administração:** Painel de controle para ajustes manuais e auditoria.
- **Infraestrutura:** Pronto para produção utilizando containers Docker.

## Como rodar

### 1. Autenticação
1. Inicie uma conversa com o [@BotFather](https://t.me/botfather) no Telegram.
2. Envie o comando `/newbot` e siga os passos para criar a aplicação.
3. Guarde o token gerado.

### 2. Deploy Local / Desenvolvimento

**Via Docker (Recomendado):**
```bash
git clone [https://github.com/joao-asp/grana.noiz.git](https://github.com/joao-asp/grana.noiz.git)
cd grana.noiz
cp .env.example .env
# Adicione seu token e ID no arquivo .env
make dev

```

**Instalação nativa:**

```bash
git clone [https://github.com/joao-asp/grana.noiz.git](https://github.com/joao-asp/grana.noiz.git)
cd grana.noiz
pip install -r requirements.txt
cp .env.example .env
# Adicione seu token e ID no arquivo .env
python -m src.bot

```

## Uso e Comandos

**Usuários padrão:**

* `/start` - Inicia a interação e cadastra o usuário no banco de dados.
* `/pagar` - Registra o pagamento referente ao mês vigente.
* `/divida` - Retorna o extrato de pendências financeiras do usuário.
* `/paguei AAAA-MM` - Registra o pagamento de um mês retroativo ou específico (ex: `/paguei 2026-04`).

**Administradores:**

* `/status` - Retorna o balanço geral e quem já pagou no mês atual.
* `/divida_manual <id> <mes> <valor>` - Insere uma pendência no sistema manualmente.

## Configuração de Ambiente (.env)

Para descobrir seu ID de administrador, envie uma mensagem para o [@userinfobot](https://t.me/userinfobot) e copie o ID numérico.

O arquivo `.env` deve seguir esta estrutura:

```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
VALOR_CONTRIBUICAO=50.0
ADMINS=seu_id_numerico_aqui
COBRANCA_DIA=10
COBRANCA_HORA=9

```

## CLI / Makefile

O projeto conta com comandos Makefile para facilitar a esteira de desenvolvimento e deploy:

```bash
make help     # Lista todos os comandos disponíveis
make dev      # Sobe a aplicação em modo de desenvolvimento
make prod     # Sobe a aplicação otimizada para produção
make logs     # Exibe a saída do container
make admin    # Acessa o terminal interativo/painel admin
make clean    # Remove containers, imagens e volumes não utilizados

```

## Arquitetura do Projeto

```text
grana.noiz/
├── src/
│   ├── bot.py          # Lógica principal de roteamento do bot
│   ├── config.py       # Carregamento de variáveis de ambiente
│   ├── admin.py        # Módulo de comandos restritos
│   └── utils/
│       └── db.py       # Interface de persistência de dados
├── scripts/            # Scripts de automação e setup
├── Makefile            # Automação de tarefas (build/run)
└── .env.example        # Template de variáveis de ambiente

```

## Rotinas Automatizadas

O sistema possui um job interno que roda de acordo com as variáveis `COBRANCA_DIA` e `COBRANCA_HORA`. O comportamento padrão é:

1. Geração das cobranças do mês vigente para todos os membros ativos.
2. Disparo de notificações de lembrete para usuários com pendências em aberto.
3. Compilação das dívidas acumuladas (mês atual + retroativos).

## Troubleshooting

Caso o bot pare de responder ou apresente instabilidade na conexão (Polling/Webhook):

```bash
# Inspecionar os logs de erro
make logs

# Fazer um hard reset no ambiente local
make clean && make dev

```

Se o erro for de autenticação (Unauthorized), valide o `TELEGRAM_BOT_TOKEN` e garanta que o arquivo `.env` está sendo lido corretamente na raiz do projeto.

## Contribuição

1. Faça o fork do repositório.
2. Crie sua branch de feature: `git checkout -b feature/nova-funcionalidade`
3. Faça o commit das suas alterações: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Faça o push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request.

## Licença

Distribuído sob a licença AGPL-3.0. Veja o arquivo [LICENSE](https://www.google.com/search?q=LICENSE) para mais detalhes.

---

Desenvolvido para fortalecer a autonomia e organização financeira de coletivos.

```

```
