
resource "azurerm_resource_group" "rg" {
  name     = "storage-rg"
  location = var.location
}

resource "azurerm_storage_account" "storage" {
  name                     = "varinder${random_string.rand.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  static_website {
    index_document     = "index.html"
    error_404_document = "404.html"
  }
}

resource "random_string" "rand" {
  length  = 5
  special = false
  upper   = false
}

resource "azurerm_storage_blob" "index" {
  name                   = "index.html"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = "$web"
  type                   = "Block"
  source                 = "../website/index.html"
}

resource "azurerm_storage_blob" "error" {
  name                   = "404.html"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = "$web"
  type                   = "Block"
  source                 = "../website/404.html"
}
