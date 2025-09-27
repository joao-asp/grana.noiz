# 🤝 Contribuindo com o Bot da Caixinha

Obrigado por considerar contribuir com nosso projeto! Este guia te ajudará a começar.

## 🌟 Como Contribuir

### 1. Configuração Inicial
```bash
# Fork o repositório no GitHub

# Clone seu fork
git clone https://github.com/SEU_USUARIO/bot-caixinha-telegram.git
cd bot-caixinha-telegram

# Configure upstream
git remote add upstream https://github.com/USUARIO_ORIGINAL/bot-caixinha-telegram.git

# Configure o ambiente
./scripts/git-setup.sh
cp .env.dev.example .env.dev
# Configure seu token de teste em .env.dev
```

### 2. Workflow de Desenvolvimento
```bash
# Sempre comece do develop atualizado
git checkout develop
git pull upstream develop

# Crie uma branch para sua feature
git checkout -b feature/nome-da-funcionalidade
# ou
git checkout -b fix/nome-do-bug

# Configure ambiente de desenvolvimento
make dev

# Desenvolva com hot reload ativo
# Seus arquivos em src/ são recarregados automaticamente
```

### 3. Testando suas Alterações
```bash
# Execute testes
make test

# Teste manualmente no Telegram
# Use um bot de teste (crie outro no @BotFather)

# Verifique logs
make logs
```

### 4. Enviando sua Contribuição
```bash
# Commit suas mudanças
git add .
git commit -m "feat: adicionar nova funcionalidade X"

# Push para seu fork
git push origin feature/nome-da-funcionalidade

# Abra um Pull Request no GitHub para a branch 'develop'
```

## 📝 Padrões de Código

### Commits
Seguimos [Conventional Commits](https://conventionalcommits.org/):
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Alterações na documentação
- `style:` - Formatação, não afeta lógica
- `refactor:` - Refatoração de código
- `test:` - Adicionar ou corrigir testes

Exemplos:
```
feat: adicionar comando /relatorio mensal
fix: corrigir bug no cálculo de dívidas
docs: atualizar README com novos comandos
```

### Python
- Use **Python 3.11+**
- Siga [PEP 8](https://pep8.org/)
- Docstrings para todas as funções públicas
- Type hints quando possível

```python
async def marcar_pagamento(user_id: int, mes: str) -> bool:
    """
    Marca pagamento de um usuário para um mês específico.
    
    Args:
        user_id: ID do usuário no Telegram
        mes: Mês no formato YYYY-MM
        
    Returns:
        True se marcado com sucesso, False caso contrário
    """
    # implementação...
```

### Estrutura de Arquivos
- **src/bot.py** - Lógica principal do bot
- **src/config.py** - Configurações (sem secrets!)
- **src/utils/db.py** - Funções de banco de dados
- **src/handlers/** - Handlers específicos de comandos
- **tests/** - Testes automatizados

## 🧪 Escrevendo Testes

```python
# tests/test_pagamentos.py
import pytest
from src.utils.db import marcar_pagamento

@pytest.mark.asyncio
async def test_marcar_pagamento_sucesso():
    # Arrange
    user_id = 123456789
    mes = "2025-01"
    
    # Act
    resultado = await marcar_pagamento(user_id, mes)
    
    # Assert
    assert resultado is True
```

Execute testes:
```bash
make test
# ou
docker-compose exec bot-dev pytest
```

## 🐳 Desenvolvimento com Docker

### Comandos Úteis
```bash
make dev      # Inicia ambiente de desenvolvimento
make logs     # Vê logs em tempo real
make admin    # Acessa painel administrativo
make clean    # Limpa containers e volumes
```

### Estrutura Docker
- **Dockerfile.dev** - Imagem para desenvolvimento
- **docker-compose.dev.yml** - Ambiente com hot reload
- **volumes** - Código montado para reload automático

### Debugging
```python
# Use ipdb para debugging
import ipdb; ipdb.set_trace()
```

## 🔍 Tipos de Contribuições

### 🐛 Reportar Bugs
- Use nosso template de issue
- Inclua logs relevantes
- Descreva passos para reproduzir
- Informe seu ambiente (Docker, Python local, etc.)

### ✨ Sugerir Funcionalidades
- Descreva o problema que resolve
- Proponha uma solução
- Considere casos extremos
- Pense na experiência do usuário

### 📖 Melhorar Documentação
- README desatualizado
- Comentários no código
- Exemplos de uso
- Guias para iniciantes

### 🛠️ Contribuições de Código

#### Funcionalidades Desejadas:
- **Relatórios avançados** (gráficos, estatísticas)
- **Integração PIX** (gerar códigos de pagamento)
- **Notificações customizáveis**
- **Backup automático** para cloud
- **API REST** para integrações externas
- **Temas/personalização** das mensagens
- **Múltiplas caixinhas** por coletivo

#### Melhorias Técnicas:
- **Testes automatizados** (coverage > 80%)
- **CI/CD pipeline** (GitHub Actions)
- **Monitoring/Observabilidade**
- **Performance/Otimizações**
- **Segurança** (rate limiting, validação)

## ❓ Dúvidas e Suporte

### Canais de Comunicação
- **Issues**: Para bugs e sugestões
- **Discussions**: Para dúvidas gerais
- **Email**: contato@exemplo.com (se aplicável)

### Antes de Perguntar
1. Procure nas issues existentes
2. Consulte a documentação
3. Verifique os logs de erro
4. Teste com ambiente limpo

## 🎯 Roadmap

### Próximas Versões
- **v1.1** - Relatórios e estatísticas
- **v1.2** - Integração com PIX
- **v1.3** - API REST
- **v2.0** - Interface web

### Como Participar
- Vote em features nas discussions
- Implemente funcionalidades do roadmap
- Proponha novas ideias

## 🏆 Reconhecimento

Todos os contribuidores são listados no README e releases. Contribuições significativas podem resultar em:
- Mention especial nos release notes
- Acesso antecipado a novas features
- Participação nas decisões de roadmap

## 📋 Checklist para Pull Requests

Antes de submeter:
- [ ] Código segue os padrões estabelecidos
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada se necessário
- [ ] Commit messages seguem padrão
- [ ] Não há secrets hardcoded
- [ ] Testado localmente
- [ ] README atualizado se aplicável

---

**Obrigado por contribuir! Juntos tornamos os coletivos mais organizados! 💚**