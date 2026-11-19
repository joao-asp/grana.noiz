# =============================================================================
# grana.noiz — Outputs Terraform (Azure)
# =============================================================================

output "resource_group_name" {
  description = "Nome do Resource Group provisionado na Azure."
  value       = azurerm_resource_group.main.name
}

output "web_app_url" {
  description = "URL pública HTTPS da aplicação grana.noiz no Azure Container Apps."
  value       = "https://${azurerm_container_app.web.ingress[0].fqdn}"
}

output "container_app_name" {
  description = "Nome do Azure Container App."
  value       = azurerm_container_app.web.name
}

output "storage_account_name" {
  description = "Nome do Storage Account onde o banco SQLite é persistido."
  value       = azurerm_storage_account.data.name
}

output "storage_file_share_name" {
  description = "Nome do Azure File Share montado em /app/data."
  value       = azurerm_storage_share.sqlite_data.name
}

output "acr_login_server" {
  description = "Servidor de login do Azure Container Registry (quando create_acr = true)."
  value       = var.create_acr ? azurerm_container_registry.acr[0].login_server : null
}
