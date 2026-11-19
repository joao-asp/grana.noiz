# =============================================================================
# grana.noiz — Variáveis Terraform (Azure Container Apps + Azure Files SQLite)
# =============================================================================

variable "project_name" {
  description = "Nome base do projeto usado para nomear recursos na Azure."
  type        = string
  default     = "grananoiz"
}

variable "environment" {
  description = "Ambiente de implantação (ex.: prod, staging)."
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Região da Azure para provisionar os recursos."
  type        = string
  default     = "brazilsouth"
}

variable "resource_group_name" {
  description = "Nome do Resource Group na Azure."
  type        = string
  default     = "rg-grananoiz-prod"
}

variable "create_acr" {
  description = "Se true, cria um Azure Container Registry (Basic) para hospedar a imagem Docker."
  type        = bool
  default     = false
}

variable "container_image" {
  description = "Imagem Docker da aplicação (ex.: ghcr.io/joao-asp/grana.noiz:latest ou imagem do ACR)."
  type        = string
  default     = "ghcr.io/joao-asp/grana.noiz:latest"
}

variable "container_cpu" {
  description = "vCPUs alocadas para o container (ex.: 0.25, 0.5)."
  type        = number
  default     = 0.25
}

variable "container_memory" {
  description = "Memória alocada para o container (ex.: 0.5Gi, 1.0Gi)."
  type        = string
  default     = "0.5Gi"
}

variable "file_share_quota_gb" {
  description = "Quota (em GB) do Azure Storage File Share montado em /app/data para o SQLite."
  type        = number
  default     = 5
}

variable "valor_contribuicao" {
  description = "Valor padrão da contribuição mensal da caixinha (em R$)."
  type        = string
  default     = "5.0"
}

variable "pix_chave" {
  description = "Chave Pix oficial exibida na interface da caixinha."
  type        = string
  default     = ""
}

variable "cobranca_dia" {
  description = "Dia do mês para geração de cobranças mensais."
  type        = string
  default     = "10"
}

variable "web_admin_user" {
  description = "Usuário do painel /admin."
  type        = string
  default     = "admin"
}

variable "web_admin_password" {
  description = "Senha do painel /admin (ou use web_admin_password_hash)."
  type        = string
  default     = ""
  sensitive   = true
}

variable "web_admin_password_hash" {
  description = "Hash PBKDF2-SHA256 da senha do painel /admin."
  type        = string
  default     = ""
  sensitive   = true
}

variable "telegram_bot_token" {
  description = "Token do bot do Telegram (@BotFather) para lembretes e notificações."
  type        = string
  default     = ""
  sensitive   = true
}

variable "admins" {
  description = "Lista de IDs do Telegram dos administradores separados por vírgula."
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags padrão aplicadas aos recursos na Azure."
  type        = map(string)
  default = {
    project    = "grana.noiz"
    collective = "itcp-unicamp"
    managed_by = "terraform"
  }
}
