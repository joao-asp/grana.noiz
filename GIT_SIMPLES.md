# 🌿 Git Simples para Coletivos

## 📋 Workflow Ultra Simples

### Para uso diário:
```bash
# 1. Baixar última versão
git pull

# 2. Fazer suas mudanças
# (editar arquivos...)

# 3. Salvar mudanças
git add .
git commit -m "fix: corrigir bug do pagamento"

# 4. Enviar para todos
git push
```

### Para funcionalidades grandes:
```bash
# 1. Criar branch
git checkout -b nova-funcionalidade

# 2. Desenvolver
# (fazer mudanças...)
git add .
git commit -m "feat: adicionar relatórios"

# 3. Voltar para main
git checkout main
git merge nova-funcionalidade

# 4. Limpar
git branch -d nova-funcionalidade
git push
```

## ⚡ Comandos Rápidos

```bash
git status              # Ver o que mudou
git log --oneline       # Ver histórico
git diff                # Ver diferenças
```

## 🆘 Emergência

```bash
# Desfazer última mudança
git reset --soft HEAD~1

# Voltar arquivo específico
git checkout HEAD -- arquivo.py

# Ver mudanças antes de commit
git diff --staged
```

## 💡 Dicas

- **Commits pequenos** são melhores que commits grandes
- **Mensagens claras**: "fix: problema X" ou "feat: funcionalidade Y"
- **Teste antes** de fazer push
- **Pull primeiro** antes de push (evita conflitos)

---

**Lembre: Git é para colaborar, não complicar! 🤝**