# 🤖 Bot da Caixinha Coletiva

Bot do Telegram para gerenciar contribuições mensais de coletivos de forma organizada e transparente.

## 📁 Estrutura do Projeto

```
bot_caixinha_telegram/
├── 📄 main.py              # Bot principal
├── 🗃️ db.py                # Gerenciamento do banco SQLite  
├── ⚙️ config.py            # Configurações
├── 🛠️ admin.py             # Painel administrativo
├── 📋 requirements.txt     # Dependências Python
├── 🗃️ caixinha.db          # Banco de dados (criado automaticamente)
├── � docs/               # Documentação
│   ├── README.md          # Este arquivo
│   └── ESTRUTURA.md       # Detalhes técnicos
├── 📁 scripts/            # Scripts utilitários
│   ├── reset.sh           # Reset completo do sistema
│   ├── instalar.sh        # Instalação automática
│   └── .env.modelo        # Modelo de configuração
└── 📁 backup/             # Backups automáticos
```

## 🚀 Início Rápido

### 1. Configure o Bot

1. **Crie um bot no Telegram:**
   - Converse com @BotFather
   - Use `/newbot` e siga as instruções
   - Copie o token gerado

2. **Configure o projeto:**
   - Edite `config.py` e coloque seu token
   - Ajuste o valor da contribuição mensal
   - Adicione seu ID como admin (use @userinfobot)

### 2. Instale e Execute

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar o bot
python3 main.py
```

### 3. Reset (se necessário)

```bash
# Limpar tudo e recomeçar
./scripts/reset.sh
```

## 📱 Comandos do Bot

### Para Todos os Membros:
- `/start` - Cadastro automático e boas-vindas
- `/pagar` - Marcar pagamento do mês atual  
- `/divida` - Ver dívidas pendentes
- `/paguei 2025-01` - Marcar mês específico

### Para Administradores:
- `/status` - Ver quem pagou no mês
- `/divida_manual <id> <mes> <valor>` - Adicionar dívida histórica

## 🛠️ Painel Administrativo

```bash
python3 admin.py
```

**Funcionalidades:**
- Ver todos os membros
- Adicionar membros manualmente
- Ver dívidas de qualquer membro
- Status de pagamentos do mês
- Criar cobranças manuais
- Adicionar dívidas históricas
- Fazer backup do banco

## ⚙️ Configurações

### Cobrança Automática
- **Dia:** 10 de cada mês
- **Horário:** 9h da manhã
- **Função:** Cria cobranças e envia lembretes

### Personalização
Edite `config.py` para alterar:
- Valor da contribuição
- Dia/hora da cobrança
- Lista de administradores

## 🔒 Segurança

- ✅ Token do bot protegido
- ✅ Comandos de admin restritos
- ✅ Banco de dados local (SQLite)
- ✅ Logs de atividade
- ✅ Backup automático

## 🆘 Resolução de Problemas

### Bot não responde
```bash
# Verificar se está rodando
ps aux | grep python.*main.py

# Reiniciar
./scripts/reset.sh && python3 main.py
```

### Dívidas não aparecem
```bash
# Verificar banco de dados
python3 admin.py
# Opção 1: Ver todos os membros
# Opção 3: Ver dívidas de um membro
```

### Limpar tudo
```bash
./scripts/reset.sh
```

## 💡 Dicas de Uso

1. **Para o coletivo:**
   - Definam regras claras sobre valores e prazos
   - Usem o `/status` regularmente para transparência
   - Façam backup do banco periodicamente

2. **Para administradores:**
   - Usem o painel `admin.py` para gestão avançada
   - Adicionem dívidas históricas com `/divida_manual`
   - Monitorem os logs para problemas

3. **Para desenvolvimento:**
   - Use `./scripts/reset.sh` para testes
   - Logs estão em tempo real no terminal
   - Backup automático na pasta `backup/`

## 🎯 Status Atual

✅ **Funcionando perfeitamente!**

- [x] Cadastro automático de membros
- [x] Registro de pagamentos
- [x] Consulta de dívidas  
- [x] Cobrança automática (dia 10)
- [x] Adição de dívidas manuais
- [x] Painel administrativo
- [x] Sistema de backup
- [x] Comandos para admins
- [x] Estrutura organizada

**Pronto para uso em produção! 🚀**
