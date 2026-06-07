###################################
# Resource Group
###################################

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

###################################
# SQL SERVER
###################################

resource "azurerm_mssql_server" "sqlserver" {

  name                         = var.sql_server_name
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location

  version                      = "12.0"

  administrator_login          = var.sql_admin_user
  administrator_login_password = var.sql_admin_password

  minimum_tls_version = "1.2"
}

###################################
# SQL DATABASE
###################################

resource "azurerm_mssql_database" "sqldb" {

  name      = "SampleDB"
  server_id = azurerm_mssql_server.sqlserver.id

  sku_name = "Basic"

  zone_redundant = false
}