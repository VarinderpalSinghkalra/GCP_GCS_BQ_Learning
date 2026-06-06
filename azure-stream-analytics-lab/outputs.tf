output "eventhub_name" {
  value = azurerm_eventhub.telecom_eventhub.name
}

output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "stream_job_name" {
  value = azurerm_stream_analytics_job.job.name
}