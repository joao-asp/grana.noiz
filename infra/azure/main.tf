# =============================================================================
# grana.noiz — Infraestrutura Azure (Container Apps + Storage File Share SQLite)
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {}
}

locals {
  name_prefix = lower(replace("${var.project_name}-${var.environment}", "/[^a-zA-Z0-9-]/", ""))
  common_tags = merge(var.tags, {
    environment = var.environment
  })
}

resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

# -----------------------------------------------------------------------------
# 1. Resource Group
# -----------------------------------------------------------------------------
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.common_tags
}

# -----------------------------------------------------------------------------
# 2. Storage Account + File Share (persistência de /app/data/caixinha.db)
# -----------------------------------------------------------------------------
resource "azurerm_storage_account" "data" {
  name                            = substr("st${replace(local.name_prefix, "-", "")}${random_string.suffix.result}", 0, 24)
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  tags                            = local.common_tags
}

resource "azurerm_storage_share" "sqlite_data" {
  name                 = "grananoiz-data"
  storage_account_name = azurerm_storage_account.data.name
  quota                = var.file_share_quota_gb
}

# -----------------------------------------------------------------------------
# 3. Azure Container Registry (opcional: var.create_acr = true)
# -----------------------------------------------------------------------------
resource "azurerm_container_registry" "acr" {
  count               = var.create_acr ? 1 : 0
  name                = substr("acr${replace(local.name_prefix, "-", "")}${random_string.suffix.result}", 0, 50)
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = true
  tags                = local.common_tags
}

# -----------------------------------------------------------------------------
# 4. Log Analytics + Container App Environment + Storage Mount
# -----------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "logs" {
  name                = "log-${local.name_prefix}"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = local.common_tags
}

resource "azurerm_container_app_environment" "env" {
  name                       = "cae-${local.name_prefix}"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logs.id
  tags                       = local.common_tags
}

resource "azurerm_container_app_environment_storage" "sqlite_mount" {
  name                         = "sqlite-data-mount"
  container_app_environment_id = azurerm_container_app_environment.env.id
  account_name                 = azurerm_storage_account.data.name
  share_name                   = azurerm_storage_share.sqlite_data.name
  access_key                   = azurerm_storage_account.data.primary_access_key
  access_mode                  = "ReadWrite"
}

# -----------------------------------------------------------------------------
# 5. Azure Container App (Interface Web + API do grana.noiz)
#    Nota: min_replicas = 1 e max_replicas = 1 garantem acesso exclusivo
#    seguro ao banco SQLite montado em /app/data.
# -----------------------------------------------------------------------------
resource "azurerm_container_app" "web" {
  name                         = "ca-${local.name_prefix}"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.common_tags

  dynamic "registry" {
    for_each = var.create_acr ? [azurerm_container_registry.acr[0]] : []
    content {
      server               = registry.value.login_server
      username             = registry.value.admin_username
      password_secret_name = "acr-password"
    }
  }

  dynamic "secret" {
    for_each = var.create_acr ? [azurerm_container_registry.acr[0]] : []
    content {
      name  = "acr-password"
      value = secret.value.admin_password
    }
  }

  secret {
    name  = "web-admin-password"
    value = var.web_admin_password != "" ? var.web_admin_password : "change-me-in-production"
  }

  secret {
    name  = "web-admin-password-hash"
    value = var.web_admin_password_hash != "" ? var.web_admin_password_hash : " "
  }

  secret {
    name  = "telegram-bot-token"
    value = var.telegram_bot_token != "" ? var.telegram_bot_token : "SEU_TOKEN_AQUI"
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    transport        = "auto"

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = 1
    max_replicas = 1

    volume {
      name         = "sqlite-data"
      storage_type = "AzureFile"
      storage_name = azurerm_container_app_environment_storage.sqlite_mount.name
    }

    container {
      name   = "grananoiz-web"
      image  = var.container_image
      cpu    = var.container_cpu
      memory = var.container_memory

      command = ["python", "-m", "src.web"]

      volume_mounts {
        name = "sqlite-data"
        path = "/app/data"
      }

      env {
        name  = "ENV"
        value = "production"
      }
      env {
        name  = "WEB_HOST"
        value = "0.0.0.0"
      }
      env {
        name  = "PORT"
        value = "8080"
      }
      env {
        name  = "DB_PATH"
        value = "/app/data/caixinha.db"
      }
      env {
        name  = "SQLITE_JOURNAL_MODE"
        value = "DELETE"
      }
      env {
        name  = "WEB_COOKIE_SECURE"
        value = "true"
      }
      env {
        name  = "VALOR_CONTRIBUICAO"
        value = var.valor_contribuicao
      }
      env {
        name  = "PIX_CHAVE"
        value = var.pix_chave
      }
      env {
        name  = "COBRANCA_DIA"
        value = var.cobranca_dia
      }
      env {
        name  = "WEB_ADMIN_USER"
        value = var.web_admin_user
      }
      env {
        name        = "WEB_ADMIN_PASSWORD"
        secret_name = "web-admin-password"
      }
      env {
        name        = "WEB_ADMIN_PASSWORD_HASH"
        secret_name = "web-admin-password-hash"
      }
      env {
        name        = "TELEGRAM_BOT_TOKEN"
        secret_name = "telegram-bot-token"
      }
      env {
        name  = "ADMINS"
        value = var.admins
      }

      liveness_probe {
        transport = "HTTP"
        port      = 8080
        path      = "/api/health"
      }

      readiness_probe {
        transport = "HTTP"
        port      = 8080
        path      = "/api/health"
      }
    }
  }
}
