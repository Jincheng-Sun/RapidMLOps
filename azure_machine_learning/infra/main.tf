resource "azurerm_resource_group" "rg" {
  location = var.location
  name     = var.resource_group.name
  tags     = var.resource_group.tags
}

resource "azurerm_log_analytics_workspace" "law" {
  location            = var.location
  name                = var.azure_monitor.law.name
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.azure_monitor.law.tags
  # TODO: pep
}

resource "azurerm_application_insights" "appi" {
  location            = var.location
  name                = var.azure_monitor.appi.name
  resource_group_name = azurerm_resource_group.rg.name
  workspace_id        = azurerm_log_analytics_workspace.law.id
  application_type    = var.azure_monitor.appi.application_type
  tags                = var.app_insights.appi.tags
  # TODO: azurerm_monitor_diagnostic_setting log and metric
}

resource "azurerm_key_vault" "kv" {
  location                      = var.location
  name                          = var.key_vault.name
  resource_group_name           = azurerm_resource_group.rg.name
  sku_name                      = var.key_vault.sku_name
  tenant_id                     = var.tenant_id
  tags                          = var.key_vault.tags
  enabled_for_disk_encryption   = true
  soft_delete_retention_days    = var.key_vault.soft_delete_retention_days
  purge_protection_enabled      = true
  enable_rbac_authorization     = true
  public_network_access_enabled = false
  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }
  # TODO: azurerm_monitor_diagnostic_setting log and metric
}

resource "azurerm_virtual_network" "vnet" {
  location            = var.location
  name                = var.virtual_network.name
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.virtual_network.tags
  address_space       = var.virtual_network.address_space
  dns_servers         = var.virtual_network.dns_servers
}

# resource "azurerm_network_security_group" "nsg" {
#   for_each            = var.virtual_network.nsgs
#   location            = var.location
#   name                = each.key
#   resource_group_name = azurerm_resource_group.rg.name
# }

resource "azurerm_subnet" "resource" {
  name                 = "${var.virtual_network.name}-resource-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = var.virtual_network.resource_subnet_address_prefixes
  # TODO: azurerm_subnet_networks_security_group_association
  # TODO: azurerm_subnet_route_table_association
}

resource "azurerm_storage_account" "st" {
  location                          = var.location
  name                              = var.storage_account.name
  resource_group_name               = azurerm_resource_group.rg.name
  account_tier                      = var.storage_account.access_tier
  account_replication_type          = var.storage_account.account_replication_type
  tags                              = var.storage_account.tags
  account_kind                      = var.storage_account.account_kind
  https_traffic_only_enabled        = false
  allow_nested_items_to_be_public   = false
  public_network_access_enabled     = false
  default_to_oauth_authentication   = true
  is_hns_enabled                    = var.storage_account.is_hns_enabled
  local_user_enabled                = false
  queue_encryption_key_type         = var.storage_account.account_kind == "StorageV2" ? "Account" : null
  table_encryption_key_type         = var.storage_account.account_kind == "StorageV2" ? "Account" : null
  infrastructure_encryption_enabled = var.storage_account.infrastructure_encryption_enabled
  allowed_copy_scope                = "PrivateLink"
  # TODO: azurerm_monitor_diagnostic_setting log and metric
}

resource "azurerm_storage_container" "sc" {
  for_each = var.storage_account.storage_containers

  name                  = each.key
  storage_account_name  = azurerm_storage_account.st.name
  container_access_type = each.value.container_access_type
  metadata              = each.value.metadata
}

resource "azurerm_container_registry" "acr" {
  location                      = var.location
  name                          = var.container_registry.name
  resource_group_name           = azurerm_resource_group.rg.name
  sku                           = var.container_registry.sku
  tags                          = var.container_registry.tags
  public_network_access_enabled = false
}

resource "azurerm_user_assigned_identity" "uami" {
  location            = var.location
  name                = var.managed_identity.name
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.managed_identity.tags
}

resource "azurerm_machine_learning_workspace" "mlw" {
  location                = var.location
  name                    = var.mlw_workspace.name
  resource_group_name     = azurerm_resource_group.rg.name
  application_insights_id = azurerm_application_insights.appi.id
  key_vault_id            = ""
  storage_account_id      = azurerm_storage_account.st.id
  identity {
    type         = "SystemAssigned, UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.uami.id]
  }
  container_registry_id         = azurerm_container_registry.acr.id
  public_network_access_enabled = false
}

resource "azurerm_private_endpoint" "law_pep" {
  location            = var.location
  name                = "${azurerm_log_analytics_workspace.law.name}-azuremonitor-pep"
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.resource.id
  private_service_connection {
    name                           = "${azurerm_log_analytics_workspace.law.name}-azuremonitor-psc"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_log_analytics_workspace.law.id
    subresource_names              = ["azuremonitor"]
  }
}

resource "azurerm_private_endpoint" "kv_pep" {
  location            = var.location
  name                = "${azurerm_key_vault.kv.name}-vault-pep"
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.resource.id
  private_service_connection {
    name                           = "${azurerm_key_vault.kv.name}-vault-psc"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_key_vault.kv.id
    subresource_names              = ["vault"]
  }
}

resource "azurerm_private_endpoint" "st_pep" {
  for_each = ["blob", "file", "queue", "table"]

  location            = var.location
  name                = "${azurerm_storage_account.st.name}-${each.key}-pep"
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.resource.id
  private_service_connection {
    name                           = "${azurerm_storage_account.st.name}-${each.key}-psc"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_storage_account.st.id
    subresource_names              = [each.key]
  }
}

resource "azurerm_private_endpoint" "acr_pep" {
  location            = var.location
  name                = "${azurerm_container_registry.acr.name}-registry-pep"
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.resource.id

  private_service_connection {
    name                           = "${azurerm_container_registry.acr.name}-registry-psc"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_container_registry.acr.id
    subresource_names              = ["registry"]
  }
}

resource "azurerm_private_endpoint" "mlw_pep" {
  location            = var.location
  name                = "${azurerm_machine_learning_workspace.mlw.name}-amlworkspace-pep"
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.resource.id

  private_service_connection {
    name                           = "${azurerm_machine_learning_workspace.mlw.name}-amlworkspace-psc"
    is_manual_connection           = false
    private_connection_resource_id = azurerm_machine_learning_workspace.mlw.id
    subresource_names              = ["amlworkspace"]
  }
}

# resource "azurerm_monitor_diagnostic_setting" "kv_diagnostic_setting" {
#     name = "${azurerm_key_vault.kv.name}-diagnostic-setting"
#     target_resource_id = azurerm_key_vault.kv.id
#     log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
#     # ...
# }