.PHONY: help setup dev prod test clean admin logs backup

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
	@./scripts/git-setup.sh
	@echo "$(GREEN)✅ Projeto configurado!$(NC)"
	@echo ""
	@echo "$(YELLOW)📝 Próximos passos:$(NC)"
	@echo "   1. cp .env.example .env"
	@echo "   2. Edite .env com seu token"
	@echo "   3. make dev"

dev: ## 🛠️ Iniciar ambiente de desenvolvimento
	@echo "$(GREEN)🐳 Iniciando ambiente de desenvolvimento...$(NC)"
	@if [ ! -f .env.dev ]; then \
		echo "$(YELLOW)⚠️  Criando .env.dev...$(NC)"; \
		cp .env.dev.example .env.dev; \
		echo "$(RED)❗ Configure seu token em .env.dev$(NC)"; \
	fi
	@docker-compose -f docker-compose.dev.yml build --quiet
	@docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✅ Ambiente dev iniciado!$(NC)"
	@echo "$(YELLOW)📊 Ver logs: make logs$(NC)"
	@echo "$(YELLOW)🛑 Parar: make stop$(NC)"

prod: ## 🚀 Deploy para produção
	@echo "$(GREEN)🚀 Deploy para produção...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ Arquivo .env não encontrado!$(NC)"; \
		echo "   cp .env.example .env"; \
		exit 1; \
	fi
	@if [ "$$(git branch --show-current)" != "main" ]; then \
		echo "$(RED)❌ Deploy só pode ser feito da branch main$(NC)"; \
		exit 1; \
	fi
	@docker-compose build --quiet
	@docker-compose up -d
	@echo "$(GREEN)✅ Bot em produção!$(NC)"

test: ## 🧪 Executar testes
	@echo "$(GREEN)🧪 Executando testes...$(NC)"
	@if [ "$$(docker-compose -f docker-compose.dev.yml ps -q bot-dev)" ]; then \
		docker-compose -f docker-compose.dev.yml exec bot-dev python -m pytest tests/ -v; \
	else \
		echo "$(RED)❌ Ambiente dev não está rodando$(NC)"; \
		echo "   Execute: make dev"; \
		exit 1; \
	fi

lint: ## 🔍 Verificar código (linting)
	@echo "$(GREEN)🔍 Verificando código...$(NC)"
	@docker-compose -f docker-compose.dev.yml exec bot-dev python -m flake8 src/
	@docker-compose -f docker-compose.dev.yml exec bot-dev python -m black --check src/
	@echo "$(GREEN)✅ Código ok!$(NC)"

format: ## ✨ Formatar código
	@echo "$(GREEN)✨ Formatando código...$(NC)"
	@docker-compose -f docker-compose.dev.yml exec bot-dev python -m black src/
	@echo "$(GREEN)✅ Código formatado!$(NC)"

clean: ## 🧹 Limpar containers e volumes
	@echo "$(GREEN)🧹 Limpando ambiente...$(NC)"
	@docker-compose -f docker-compose.dev.yml down --volumes --rmi local --remove-orphans 2>/dev/null || true
	@docker-compose down --volumes --rmi local --remove-orphans 2>/dev/null || true
	@docker system prune -f
	@echo "$(GREEN)✅ Ambiente limpo!$(NC)"

admin: ## 🛡️ Acessar painel administrativo
	@echo "$(GREEN)🛡️ Acessando painel administrativo...$(NC)"
	@if [ "$$(docker-compose ps -q bot-caixinha-prod)" ]; then \
		docker-compose exec bot-caixinha-prod python -m src.admin; \
	elif [ "$$(docker-compose -f docker-compose.dev.yml ps -q bot-dev)" ]; then \
		docker-compose -f docker-compose.dev.yml exec bot-dev python -m src.admin; \
	else \
		echo "$(RED)❌ Nenhum bot rodando$(NC)"; \
		echo "   Execute: make dev ou make prod"; \
	fi

logs: ## 📄 Ver logs do bot
	@if [ "$$(docker-compose ps -q bot-caixinha-prod)" ]; then \
		echo "$(GREEN)📄 Logs de produção:$(NC)"; \
		docker-compose logs -f; \
	elif [ "$$(docker-compose -f docker-compose.dev.yml ps -q bot-dev)" ]; then \
		echo "$(GREEN)📄 Logs de desenvolvimento:$(NC)"; \
		docker-compose -f docker-compose.dev.yml logs -f; \
	else \
		echo "$(RED)❌ Nenhum bot rodando$(NC)"; \
		echo "   Execute: make dev ou make prod"; \
	fi

stop: ## ⏹️ Parar bot
	@echo "$(GREEN)⏹️ Parando bot...$(NC)"
	@docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
	@docker-compose down 2>/dev/null || true
	@echo "$(GREEN)✅ Bot parado!$(NC)"

restart: ## 🔄 Reiniciar bot
	@echo "$(GREEN)🔄 Reiniciando bot...$(NC)"
	@make stop
	@if [ -f docker-compose.dev.yml ] && [ "$$(docker-compose -f docker-compose.dev.yml config)" ]; then \
		make dev; \
	else \
		make prod; \
	fi

backup: ## 💾 Fazer backup do banco
	@echo "$(GREEN)💾 Fazendo backup...$(NC)"
	@mkdir -p backup
	@if [ -f data/caixinha.db ]; then \
		cp data/caixinha.db backup/caixinha_backup_$$(date +%Y%m%d_%H%M%S).db; \
		echo "$(GREEN)✅ Backup criado em backup/$(NC)"; \
	else \
		echo "$(RED)❌ Banco de dados não encontrado$(NC)"; \
	fi

status: ## 📊 Status dos serviços
	@echo "$(GREEN)📊 Status dos serviços:$(NC)"
	@echo ""
	@echo "$(YELLOW)Produção:$(NC)"
	@docker-compose ps 2>/dev/null || echo "  Não rodando"
	@echo ""
	@echo "$(YELLOW)Desenvolvimento:$(NC)"
	@docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "  Não rodando"

shell: ## 🐚 Abrir shell no container
	@if [ "$$(docker-compose -f docker-compose.dev.yml ps -q bot-dev)" ]; then \
		echo "$(GREEN)🐚 Abrindo shell no container dev...$(NC)"; \
		docker-compose -f docker-compose.dev.yml exec bot-dev /bin/bash; \
	elif [ "$$(docker-compose ps -q bot-caixinha-prod)" ]; then \
		echo "$(GREEN)🐚 Abrindo shell no container prod...$(NC)"; \
		docker-compose exec bot-caixinha-prod /bin/bash; \
	else \
		echo "$(RED)❌ Nenhum container rodando$(NC)"; \
	fi

# Aliases para comandos comuns
build: dev ## Alias para 'dev'
run: prod ## Alias para 'prod'  
up: dev ## Alias para 'dev'
down: stop ## Alias para 'stop'