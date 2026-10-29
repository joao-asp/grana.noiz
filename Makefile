.PHONY: help setup dev prod clean admin logs stop web web-docker web-logs import-legado import-legado-docker

# Cores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

# Python local: usa o venv do projeto quando existir
PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

# Argumentos extras para a importação, ex.:
#   make import-legado ARGS="--membros /caminho/a.csv --lancamentos /caminho/b.csv"
ARGS ?=

help: ## 📋 Mostrar ajuda
	@echo "$(GREEN)🤖 Bot da Caixinha - Comandos Disponíveis$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-22s$(NC) %s\n", $$1, $$2}'

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
	@echo "$(GREEN)✅ Bot + web iniciados! Acesse http://localhost:8080$(NC)"

prod: ## 🚀 Deploy para produção
	@echo "$(GREEN)🚀 Deploy para produção...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Arquivo .env não encontrado!$(NC)"; \
		exit 1; \
	fi
	@docker-compose up -d --build
	@echo "$(GREEN)✅ Bot + web em produção! Web: http://localhost:8080$(NC)"

clean: ## 🧹 Limpar containers
	@echo "$(GREEN)🧹 Limpando ambiente...$(NC)"
	@docker-compose down --volumes --rmi local --remove-orphans 2>/dev/null || true
	@echo "$(GREEN)✅ Ambiente limpo!$(NC)"

admin: ## 🛡️ Acessar painel administrativo
	@echo "$(GREEN)🛡️ Acessando painel administrativo...$(NC)"
	@docker-compose exec bot-caixinha python -m src.admin

logs: ## 📄 Ver logs do bot e da web
	@docker-compose logs -f

web: ## 🌐 Rodar a interface web localmente
	@echo "$(GREEN)🌐 Iniciando interface web em http://localhost:8080$(NC)"
	@$(PYTHON) -m src.web

web-docker: ## 🌐 Subir interface web via Docker
	@docker-compose up -d --build web-caixinha
	@echo "$(GREEN)✅ Web em http://localhost:8080$(NC)"

web-logs: ## 📄 Ver logs da interface web
	@docker-compose logs -f web-caixinha

stop: ## ⏹️ Parar bot
	@docker-compose down

import-legado: ## 📥 Importar histórico legado (ambiente local)
	@echo "$(GREEN)📥 Importando histórico legado (local)...$(NC)"
	@$(PYTHON) -m scripts.importar_legado $(ARGS)

import-legado-docker: ## 🐳 Importar histórico legado (via Docker)
	@echo "$(GREEN)📥 Importando histórico legado (Docker)...$(NC)"
	@docker-compose run --rm bot-caixinha python -m scripts.importar_legado $(ARGS)
