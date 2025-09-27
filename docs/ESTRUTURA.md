# Estrutura do Projeto Bot da Caixinha

```
bot_caixinha_telegram/
├── main.py              # Arquivo principal do bot
├── db.py                # Gerenciamento do banco SQLite
├── config.py            # Configurações do projeto
├── admin.py             # Script para tarefas administrativas
├── requirements.txt     # Dependências Python
├── README.md            # Documentação completa
├── .env.exemplo         # Exemplo de configurações
├── instalar.sh          # Script de instalação automática
└── caixinha.db          # Banco de dados (criado automaticamente)
```

## Arquivos Principais

### 📱 main.py
- Bot principal do Telegram
- Comandos: /start, /pagar, /divida, /paguei, /status
- Cobrança automática mensal
- Sistema de agendamento

### 🗃️ db.py
- Gerenciamento do banco SQLite
- Funções para membros e pagamentos
- Consultas e relatórios

### ⚙️ config.py
- Token do bot
- Valor da contribuição
- Lista de administradores
- Configurações gerais

### 🛠️ admin.py
- Interface administrativa
- Adicionar membros manualmente
- Ver relatórios e status
- Fazer backup do banco

## Como Usar

1. **Configuração inicial:**
   ```bash
   ./instalar.sh
   ```

2. **Editar configurações:**
   ```bash
   cp .env.exemplo .env
   # Edite .env com seus dados
   ```

3. **Rodar o bot:**
   ```bash
   python main.py
   ```

4. **Administração:**
   ```bash
   python admin.py
   ```

## Funcionalidades Implementadas

✅ Cadastro automático de membros  
✅ Registro de pagamentos  
✅ Consulta de dívidas  
✅ Cobrança automática mensal  
✅ Relatórios para administradores  
✅ Interface administrativa  
✅ Backup do banco de dados  
✅ Configuração via arquivo .env  
✅ Documentação completa  

## Próximas Melhorias

🔮 Integração com PIX  
🔮 Relatórios em PDF  
🔮 Interface web  
🔮 Deploy automático  
🔮 Notificações avançadas  
