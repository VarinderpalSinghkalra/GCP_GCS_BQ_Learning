provider "azurerm" {
  features {}
}

# Random suffix to ensure global uniqueness
resource "random_string" "suffix" {
  length  = 5
  special = false
  upper   = false
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "rg-static-website"
  location = "East US"
}

# Storage Account with Static Website enabled
resource "azurerm_storage_account" "storage" {
  name                     = "varinderweb${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  static_website {
    index_document     = "index.html"
    error_404_document = "404.html"
  }

  tags = {
    project = "assignment"
  }
}

# Upload index.html
resource "azurerm_storage_blob" "index" {
  name                   = "index.html"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = "$web"
  type                   = "Block"
  source                 = "index.html"
  content_type           = "text/html"
}

# Upload 404.html
resource "azurerm_storage_blob" "error" {
  name                   = "404.html"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = "$web"
  type                   = "Block"
  source                 = "404.html"
  content_type           = "text/html"
}

# Output website URL
output "static_website_url" {
  value = azurerm_storage_account.storage.primary_web_endpoint
}