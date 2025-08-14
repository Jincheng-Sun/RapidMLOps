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
}

resource "azurerm_application_insights" "appi" {
  location            = var.location
  name                = var.azure_monitor.appi.name
  resource_group_name = azurerm_resource_group.rg.name
  workspace_id        = azurerm_log_analytics_workspace.law.id
  application_type    = var.azure_monitor.appi.application_type
  tags                = var.azure_monitor.appi.tags
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
  public_network_access_enabled = var.public_network_access_enabled
  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }
  # TODO: azurerm_monitor_diagnostic_setting log and metric
}

resource "azurerm_storage_account" "st" {
  location                          = var.location
  name                              = var.storage_account.name
  resource_group_name               = azurerm_resource_group.rg.name
  account_tier                      = var.storage_account.account_tier
  account_replication_type          = var.storage_account.account_replication_type
  tags                              = var.storage_account.tags
  account_kind                      = var.storage_account.account_kind
  https_traffic_only_enabled        = false
  allow_nested_items_to_be_public   = false
  public_network_access_enabled     = var.public_network_access_enabled
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
  public_network_access_enabled = var.public_network_access_enabled
}

resource "azurerm_user_assigned_identity" "uami" {
  location            = var.location
  name                = var.managed_identity.name
  resource_group_name = azurerm_resource_group.rg.name
  tags                = var.managed_identity.tags
}

resource "azurerm_machine_learning_workspace" "mlw" {
  location                = var.location
  name                    = var.ml_workspace.name
  resource_group_name     = azurerm_resource_group.rg.name
  application_insights_id = azurerm_application_insights.appi.id
  key_vault_id            = azurerm_key_vault.kv.id
  storage_account_id      = azurerm_storage_account.st.id
  identity {
    type         = "SystemAssigned, UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.uami.id]
  }
  tags                          = var.ml_workspace.tags
  container_registry_id         = azurerm_container_registry.acr.id
  public_network_access_enabled = var.public_network_access_enabled
  high_business_impact          = var.ml_workspace.high_business_impact
}

resource "azurerm_machine_learning_compute_cluster" "image_build" {
  count = var.public_network_access_enabled ? 0 : 1

  location                      = var.location
  name                          = "${azurerm_machine_learning_workspace.mlw.name}-image-build-compute-cluster"
  machine_learning_workspace_id = azurerm_machine_learning_workspace.mlw.id
  vm_priority                   = var.ml_workspace.image_build_compute_cluster.vm_priority
  vm_size                       = var.ml_workspace.image_build_compute_cluster.vm_size
  scale_settings {
    min_node_count                       = var.ml_workspace.image_build_compute_cluster.min_node_count
    max_node_count                       = var.ml_workspace.image_build_compute_cluster.max_node_count
    scale_down_nodes_after_idle_duration = var.ml_workspace.image_build_compute_cluster.scale_down_nodes_after_idle_duration
  }
  tags = var.ml_workspace.image_build_compute_cluster.tags
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.uami.id]
  }
  local_auth_enabled     = false
  node_public_ip_enabled = false
  subnet_resource_id     = azurerm_subnet.resource.id

  depends_on = [azurerm_private_endpoint.mlw_pep]
}

resource "azurerm_machine_learning_compute_cluster" "job_run" {
  location                      = var.location
  name                          = "${azurerm_machine_learning_workspace.mlw.name}-job-run-compute-cluster"
  machine_learning_workspace_id = azurerm_machine_learning_workspace.mlw.id
  vm_priority                   = var.ml_workspace.job_run_compute_cluster.vm_priority
  vm_size                       = var.ml_workspace.job_run_compute_cluster.vm_size
  scale_settings {
    min_node_count                       = var.ml_workspace.job_run_compute_cluster.min_node_count
    max_node_count                       = var.ml_workspace.job_run_compute_cluster.max_node_count
    scale_down_nodes_after_idle_duration = var.ml_workspace.job_run_compute_cluster.scale_down_nodes_after_idle_duration
  }
  tags = var.ml_workspace.job_run_compute_cluster.tags
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.uami.id]
  }
  local_auth_enabled     = false
  node_public_ip_enabled = false
  subnet_resource_id     = azurerm_subnet.resource.id

  depends_on = [azurerm_private_endpoint.mlw_pep]
}

resource "azapi_update_resource" "mlw_update" {
  count = var.public_network_access_enabled ? 0 : 1

  type        = "Microsoft.MachineLearningServices/workspaces@2023-04-01"
  resource_id = azurerm_machine_learning_workspace.mlw.id

  body = jsonencode({
    properties = {
      imageBuildCompute = azurerm_machine_learning_compute_cluster.image_build[0].name
    }
  })
}

resource "azapi_resource" "personal_compute_instances" {
  for_each = var.ml_workspace.personal_compute_instances

  location  = var.location
  name      = each.key
  type      = "Microsoft.MachineLearningServices/workspaces/computes@2024-10-01"
  parent_id = azurerm_machine_learning_workspace.mlw.id
  tags      = each.value.tags
  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.uami.id]
  }

  body = jsonencode({
    properties = {
      computeLocation  = var.location
      computeType      = "ComputeInstance"
      disableLocalAuth = true
      properties = {
        vmSize                           = each.value.vm_size
        computeInstanceAuthorizationType = "personal"
        enableNodePublicIp               = false
        enableRootAccess                 = false
        idleTimeBeforeShutdown           = "PT30M"
        personalComputeInstanceSettings = {
          assignedUser = {
            objectId = each.value.assigned_user.object_id
            tenantId = each.value.assigned_user.tenant_id != null ? each.value.assigned_user.tenant_id : var.tenant_id
          }
        }
        # TODO: compute setup & startup scripts
        # setupScripts = {
        #   scripts = {
        #     creationScript = {
        #       scriptSource = "inline"
        #       scriptData   = base64encode("#!/bin/bash\n# Custom setup script for personal compute instance\n")
        #       timeout      = "15m"
        #     }
        #     startupScript = {
        #         scriptSource = "inline"
        #       scriptData   = base64encode("#!/bin/bash\n# Custom setup script for personal compute instance\n")
        #       timeout      = "15m"
        #     }
        #   }
        # }
        subnet = {
          id = azurerm_subnet.resource.id
        }
      }
    }
  })

  depends_on = [azurerm_private_endpoint.mlw_pep]
}

#region Networking
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

# TODO: make PEPs optional when public_network_access_enabled is set to false
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
  for_each = toset(["blob", "file", "queue", "table"])

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
#endregion Networking

#region Azure Monitor Diagnostic Settings
# resource "azurerm_monitor_diagnostic_setting" "kv_diagnostic_setting" {
#     name = "${azurerm_key_vault.kv.name}-diagnostic-setting"
#     target_resource_id = azurerm_key_vault.kv.id
#     log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id
#     # ...
# }
#endregion Azure Monitor Diagnostic Settings

#region RBACs
# resource "azurerm_role_assignment" "st_data_reader_uai" {
#   scope                = azurerm_storage_account.st.id
#   role_definition_name = "Storage Blob Data Reader"
#   principal_id         = azurerm_user_assigned_identity.uami.principal_id
#   provider             = azurerm.uaa
# }

resource "azurerm_role_assignment" "rg_reader_uai" {
  scope                = azurerm_resource_group.rg.id
  role_definition_name = "Reader"
  principal_id         = azurerm_user_assigned_identity.uami.principal_id
}

resource "azurerm_role_assignment" "appi_monitoring_reader_uai" {
  scope                = azurerm_application_insights.appi.id
  role_definition_name = "Monitoring Reader"
  principal_id         = azurerm_user_assigned_identity.uami.principal_id
}
#endregion RBACs