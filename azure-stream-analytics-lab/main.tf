####################################
# RESOURCE GROUP
####################################

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

####################################
# EVENT HUB NAMESPACE
####################################

resource "azurerm_eventhub_namespace" "eventhub_ns" {

  name                = "gleventproc12345"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku      = "Standard"
  capacity = 1
}

####################################
# EVENT HUB
####################################

resource "azurerm_eventhub" "telecom_eventhub" {

  name         = "telecomeventhub"
  namespace_id = azurerm_eventhub_namespace.eventhub_ns.id

  partition_count   = 2
  message_retention = 1
}

####################################
# STORAGE ACCOUNT
####################################

resource "azurerm_storage_account" "storage" {

  name                     = "gleventstorage12345"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location

  account_tier             = "Standard"
  account_replication_type = "LRS"
}

####################################
# STORAGE CONTAINER
####################################

resource "azurerm_storage_container" "container" {

  name                  = "telecomoutputstorage"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}

####################################
# STREAM ANALYTICS JOB
####################################

resource "azurerm_stream_analytics_job" "job" {

  name                = "telecomfakecallsjob"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  compatibility_level = "1.2"
  data_locale         = "en-US"

  streaming_units = 1

  transformation_query = <<QUERY
SELECT
    System.Timestamp AS WindowEnd,
    COUNT(*) AS FraudulentCalls

INTO gltelecomoutput

FROM gltelecominput CS1 TIMESTAMP BY CallRecTime

JOIN gltelecominput CS2 TIMESTAMP BY CallRecTime

ON CS1.CallingIMSI = CS2.CallingIMSI

AND DATEDIFF(ss, CS1, CS2) BETWEEN 1 AND 5

WHERE CS1.SwitchNum != CS2.SwitchNum

GROUP BY TumblingWindow(Duration(second,1))
QUERY
}

####################################
# STREAM INPUT EVENT HUB
####################################

resource "azurerm_stream_analytics_stream_input_eventhub" "input" {

  name                      = "gltelecominput"
  stream_analytics_job_name = azurerm_stream_analytics_job.job.name
  resource_group_name       = azurerm_resource_group.rg.name

  eventhub_name                = azurerm_eventhub.telecom_eventhub.name
  servicebus_namespace         = azurerm_eventhub_namespace.eventhub_ns.name
  eventhub_consumer_group_name = "$Default"

  shared_access_policy_name = "RootManageSharedAccessKey"
  shared_access_policy_key  = azurerm_eventhub_namespace.eventhub_ns.default_primary_key

  serialization {
    type     = "Json"
    encoding = "UTF8"
  }
}

####################################
# STREAM OUTPUT BLOB
####################################

resource "azurerm_stream_analytics_output_blob" "output" {

  name                      = "gltelecomoutput"
  stream_analytics_job_name = azurerm_stream_analytics_job.job.name
  resource_group_name       = azurerm_resource_group.rg.name

  storage_account_name   = azurerm_storage_account.storage.name
  storage_account_key    = azurerm_storage_account.storage.primary_access_key
  storage_container_name = azurerm_storage_container.container.name

  path_pattern = "output"

  date_format = "yyyy/MM/dd"
  time_format = "HH"

  serialization {
    type     = "Json"
    encoding = "UTF8"
    format   = "LineSeparated"
  }
}