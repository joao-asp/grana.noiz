output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "vm_name" {
  value = azurerm_linux_virtual_machine.main.name
}

output "public_ip" {
  value = azurerm_public_ip.main.ip_address
}

output "ssh_command" {
  value = "ssh ${var.admin_username}@${azurerm_public_ip.main.ip_address}"
}

output "web_url_8080" {
  value = "http://${azurerm_public_ip.main.ip_address}:8080"
}
