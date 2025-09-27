# 🤝 Como Contribuir

Obrigado por querer ajudar! É super simples:

## 🚀 Processo Simples

### 1. Baixe o projeto
```bash
git clone https://github.com/joao-asp/caixinha_coletiva.git
cd bot-caixinha_telegram
```

### 2. Configure
```bash
cp .env.example .env
# Configure seu token de teste no .env
```

### 3. Desenvolva

#### Para mudanças pequenas (correções):
```bash
git pull                                    # Baixar última versão
# faça suas mudanças...
git add .
git commit -m "fix: corrigir problema X"
git push
```

#### Para mudanças grandes (novas funcionalidades):
```bash
git checkout -b minha-funcionalidade        # Criar branch
# desenvolva...
git add .
git commit -m "feat: adicionar funcionalidade Y"
git push origin minha-funcionalidade
# abra um Pull Request no GitHub
```

## 🌿 Git Workflow Ultra-Simples

### ⚡ Comandos do dia-a-dia:
```bash
git status              # Ver o que mudou
git log --oneline       # Ver histórico
git diff                # Ver diferenças antes de commit
git pull                # Sempre puxar antes de começar
```

### 🔄 Para funcionalidades complexas:
```bash
# 1. Criar branch
git checkout -b nova-funcionalidade

# 2. Desenvolver e testar
git add .
git commit -m "feat: adicionar relatórios mensais"

# 3. Abrir Pull Request (recomendado)
git push origin nova-funcionalidade
# Ou se preferir merge direto:
# git checkout main && git merge nova-funcionalidade

# 4. Limpar branch local
git branch -d nova-funcionalidade
```

### 🆘 Comandos de emergência:
```bash
# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Voltar arquivo específico
git checkout HEAD -- nome-do-arquivo.py

# Ver mudanças que serão commitadas
git diff --staged
```

## 📝 Regras Básicas

- **Teste** antes de enviar
- **Commits pequenos** são melhores que commits grandes
- **Mensagens claras**: `fix: problema X` ou `feat: funcionalidade Y`
- **Pull primeiro**: sempre `git pull` antes de `git push`
- **Uma mudança** por vez
- **Pergunte** se tiver dúvida

## 🆘 Precisa de Ajuda?

- Abra uma issue no GitHub
- Pergunte no grupo do coletivo
- Olhe o código existente como exemplo

---

**Lembre: código é coletivo, Git é para colaborar, não complicar! 💚🤝**