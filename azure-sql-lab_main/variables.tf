variable "subscription_id" {}

variable "location" {
  default = "Central India"
}

variable "resource_group_name" {
  default = "GL-SQL-RG"
}

variable "sql_server_name" {
  default = "glsqlserver01terraform"
}

variable "sql_admin_user" {
  default = "mbadmin"
}

variable "sql_admin_password" {
  sensitive = true
}

variable "vm_admin_username" {
  default = "azureuser"
}

variable "vm_admin_password" {
  sensitive = true
}