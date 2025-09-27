.PHONY: help setup dev prod clean admin logs

# Cores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

help: ## 📋 Mostrar ajuda
	@echo "$(GREEN)🤖 Bot da Caixinha - Comandos Disponíveis$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

setup: ## ⚙️ Configurar projeto inicial
	@echo "$(GREEN)🔧 Configurando projeto...$(NC)"
	@chmod +x scripts/*.sh
	@./scripts/setup.sh

dev: ## 🛠️ Iniciar ambiente de desenvolvimento
	@echo "$(GREEN)🐳 Iniciando desenvolvimento...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠️  Criando .env...$(NC)"; \
		cp .env.example .env; \
		echo "$(RED)❗ Configure seu token em .env$(NC)"; \
	fi
	@docker-compose up -d --build
	@echo "$(GREEN)✅ Bot iniciado!$(NC)"

prod: ## 🚀 Deploy para produção
	@echo "$(GREEN)🚀 Deploy para produção...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Arquivo .env não encontrado!$(NC)"; \
		exit 1; \
	fi
	@docker-compose up -d --build
	@echo "$(GREEN)✅ Bot em produção!$(NC)"

clean: ## 🧹 Limpar containers
	@echo "$(GREEN)🧹 Limpando ambiente...$(NC)"
	@docker-compose down --volumes --rmi local --remove-orphans 2>/dev/null || true
	@echo "$(GREEN)✅ Ambiente limpo!$(NC)"

admin: ## 🛡️ Acessar painel administrativo
	@echo "$(GREEN)🛡️ Acessando painel administrativo...$(NC)"
	@docker-compose exec bot-caixinha python -m src.admin

logs: ## 📄 Ver logs do bot
	@docker-compose logs -f

stop: ## ⏹️ Parar bot
	@docker-compose down