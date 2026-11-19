variable "location" {
  description = "Região do Azure permitida pela política da assinatura"
  type        = string
  default     = "eastus2"
}

variable "prefix" {
  description = "Prefixo base dos recursos (use apenas letras minúsculas, números e hífen)"
  type        = string
  default     = "grananoiz"
}

variable "vm_size" {
  description = "SKU da VM Linux"
  type        = string
  default     = "Standard_B2ats_v2"
}

variable "admin_username" {
  description = "Usuário SSH na VM Linux"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key_path" {
  description = "Caminho local da chave pública SSH"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "repo_url" {
  description = "URL do repositório Git do projeto"
  type        = string
  default     = "https://github.com/joao-asp/grana.noiz.git"
}
