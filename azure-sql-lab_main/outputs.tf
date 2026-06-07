output "resource_group" {
  value = azurerm_resource_group.rg.name
}

output "sql_server_name" {
  value = azurerm_mssql_server.sqlserver.name
}

output "sql_server_fqdn" {
  value = azurerm_mssql_server.sqlserver.fully_qualified_domain_name
}

output "vm_public_ip" {
  value = azurerm_public_ip.publicip.ip_address
}