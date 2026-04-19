resource "random_string" "rand" {
  length  = 5
  special = false
  upper   = false
}

resource "azurerm_resource_group" "rg" {
  name     = "storage-rg"
  location = "East US"
}

resource "azurerm_storage_account" "storage" {
  name                     = "varinder${random_string.rand.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = "East US"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Static website (creates $web container)
resource "azurerm_storage_account_static_website" "static" {
  storage_account_id = azurerm_storage_account.storage.id
  index_document     = "index.html"
  error_404_document = "404.html"
}

# Wait for container
resource "azurerm_storage_blob" "index" {
  name                   = "index.html"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = "$web"
  type                   = "Block"
  source                 = "../website/index.html"

  depends_on = [
    azurerm_storage_account_static_website.static
  ]
}

resource "azurerm_storage_blob" "error" {
  name                   = "404.html"
  storage_account_name   = azurerm_storage_account.storage.name
  storage_container_name = "$web"
  type                   = "Block"
  source                 = "../website/404.html"

  depends_on = [
    azurerm_storage_account_static_website.static
  ]
}
