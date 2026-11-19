# grana.noiz

Ferramenta aberta de gestão financeira, transparência e cobrança para coletivos autônomos e organizações populares — criada originalmente para a caixinha da ITCP/Unicamp. Combina um bot no Telegram, um painel web mobile-first e um banco SQLite compartilhado sem depender de serviços externos pagos.

## Prints da interface

> Adicione aqui as imagens da tela atual (por exemplo, salvando em `docs/screenshots/` ou anexando direto no repositório).

- **Início / Consulta por RA:** `<!-- ![Início e consulta por RA](docs/screenshots/inicio.png) -->`
- **ITCP / Pessoas e reembolsos:** `<!-- ![Lista da ITCP e pedidos de reembolso](docs/screenshots/itcp.png) -->`
- **Caixa e movimentações:** `<!-- ![Livro caixa e despesas](docs/screenshots/caixa.png) -->`
- **Painel `/admin`:** `<!-- ![Painel de gestão](docs/screenshots/admin.png) -->`

## O que o projeto faz

- **Consulta e aviso de pagamento:** Identificação por RA para ver meses em aberto, saldo pendente, abatimento por valor e envio de aviso de pagamento para conferência.
- **Pedidos de reembolso:** Registro de despesas do cotidiano (transporte, alimentação, materiais) por equipe (`Tainã`, `Agricultura`, `Loucura`, `Gênero`, `Rede`) ou GEPA (`GEPA 1` a `GEPA 4`), com nome, chave Pix e estado de pagamento.
- **Transparência e livro caixa:** Visão pública das pessoas na ITCP e do histórico da caixa sem expor valores individuais de pendência, mantendo ex-bolsistas separados do ciclo de cobranças ativas.
- **Bot no Telegram e cobrança automática:** Comandos para consulta, vínculo de RA, aviso de pagamento e rotina programada de cobrança mensal.
- **Painel de gestão (`/admin` e CLI):** Conferência de pagamentos, gestão de despesas/reembolsos, vínculo de contas e operações administrativas.

## Como rodar

### Com Docker

```bash
git clone https://github.com/joao-asp/grana.noiz.git
cd grana.noiz
cp .env.example .env
make dev
```

* **Web:** `http://localhost:8080`
* **Bot:** em execução junto ao serviço no ambiente de desenvolvimento/produção.

### Localmente (sem Docker)

```bash
git clone https://github.com/joao-asp/grana.noiz.git
cd grana.noiz
pip install -r requirements.txt
cp .env.example .env
```

Em terminais separados:

```bash
python -m src.bot
python -m src.web
```

## Configuração essencial (`.env`)

Principais variáveis utilizadas pelo bot, pela API/web e pela gestão:

* `TELEGRAM_BOT_TOKEN`: token obtido com `@BotFather`
* `ADMINS`: IDs numéricos do Telegram separados por vírgula (via `@userinfobot`)
* `VALOR_CONTRIBUICAO`: valor mensal padrão (ex.: `5.0`)
* `COBRANCA_DIA` e `COBRANCA_HORA`: agendamento da cobrança automática
* `WEB_HOST`, `WEB_PORT` e `WEB_PUBLIC_URL`: endereço e URL pública da interface web
* `WEB_ADMIN_USER`, `WEB_ADMIN_PASSWORD` / `WEB_ADMIN_PASSWORD_HASH`, `WEB_SESSION_TTL_HOURS`, `WEB_COOKIE_SECURE`: autenticação e sessão da rota `/admin`
* `PIX_CHAVE`: chave Pix exibida para contribuição

Para gerar uma senha forte:

```bash
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

Para usar hash PBKDF2 em produção no lugar da senha em texto puro:

```bash
python -c "from src.web import gerar_hash_senha; print(gerar_hash_senha('SUA_SENHA'))"
```

## Comandos úteis

### Bot no Telegram

* `/start`: boas-vindas e cadastro inicial
* `/vincular <RA>`: vincula o usuário do Telegram ao cadastro da ITCP
* `/pagar`: registra aviso de pagamento para conferência
* `/divida`: consulta pendências em aberto e solicitações em conferência
* `/paguei AAAA-MM`: informa pagamento referente a um mês específico
* `/status` e `/divida_manual <id> <mes> <valor>`: comandos administrativos

### `Makefile`

```bash
make help               # Lista comandos disponíveis
make dev                # Sobe bot e web em desenvolvimento
make prod               # Sobe bot e web em produção
make web                # Roda apenas o servidor web local
make web-docker         # Sobe apenas o serviço web no Docker
make web-logs           # Acompanha logs da web
make logs               # Acompanha logs do projeto
make admin              # Abre o CLI administrativo
make import-legado      # Importa CSVs de histórico (local)
make import-legado-docker # Importa CSVs de histórico via Docker
make clean              # Limpa arquivos temporários / ambiente
```

## Carga de histórico legado

Coloque os arquivos CSV em `data/legado/` (ou passe os caminhos nos argumentos do comando) e execute `make import-legado` ou `make import-legado-docker`. O script `scripts/importar_legado.py` é idempotente e separa registros de membros ativos e ex-bolsistas no relatório final.

## Estrutura do projeto

```text
grana.noiz/
├── src/
│   ├── bot.py              # Bot do Telegram e rotinas agendadas
│   ├── web.py              # Servidor HTTP e endpoints JSON
│   ├── config.py           # Leitura e validação de configurações
│   ├── admin.py            # Ferramenta administrativa em linha de comando
│   └── utils/db.py         # Acesso ao SQLite e migrações de schema
├── web/
│   ├── index.html          # Estrutura HTML da aplicação
│   ├── styles.css          # Estilos responsivos e temas
│   └── app.js              # Lógica da interface e chamadas à API
├── scripts/
│   └── importar_legado.py  # Importação idempotente de dados históricos
├── data/legado/            # CSVs de carga inicial (não versionados)
├── Makefile                # Atalhos de execução e manutenção
├── Dockerfile              # Build da imagem da aplicação
├── docker-compose.yml      # Orquestração dos serviços
└── .env.example            # Exemplo de variáveis de ambiente
```

## Como contribuir

1. Faça um fork de `https://github.com/joao-asp/grana.noiz`.
2. Crie uma branch para sua alteração: `git checkout -b feature/minha-melhoria`.
3. Faça o commit das mudanças: `git commit -m "Descreve a alteração"`.
4. Envie para o seu fork: `git push origin feature/minha-melhoria`.
5. Abra um Pull Request descrevendo o contexto e o teste realizado.

Veja também o arquivo `CONTRIBUTING.md`.

## Licença

Este projeto é distribuído sob a licença **AGPL-3.0**, uma licença de software livre com copyleft forte pensada para preservar a abertura do código e o trabalho coletivo, inclusive quando o sistema é disponibilizado em rede. Consulte o arquivo `LICENSE` para o texto integral.
