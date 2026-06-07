variable "subscription_id" {}

variable "location" {
  default = "Central India"
}

variable "resource_group_name" {
  default = "GL-SQL-RG"
}

variable "sql_admin_username" {
  default = "mbadmin"
}

variable "sql_admin_password" {
  sensitive = true
}

variable "vm_username" {
  default = "azureuser"
}