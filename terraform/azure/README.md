<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.9.0 |
| <a name="requirement_azapi"></a> [azapi](#requirement\_azapi) | 2.4.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | >3.60.0,<=4.15.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azapi"></a> [azapi](#provider\_azapi) | 2.4.0 |
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 4.15.0 |
| <a name="provider_azurerm.uaa"></a> [azurerm.uaa](#provider\_azurerm.uaa) | 4.15.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azapi_resource.personal_compute_instances](https://registry.terraform.io/providers/azure/azapi/2.4.0/docs/resources/resource) | resource |
| [azapi_update_resource.mlw_update](https://registry.terraform.io/providers/azure/azapi/2.4.0/docs/resources/update_resource) | resource |
| [azurerm_application_insights.appi](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/application_insights) | resource |
| [azurerm_container_registry.acr](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/container_registry) | resource |
| [azurerm_key_vault.kv](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault) | resource |
| [azurerm_log_analytics_workspace.law](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/log_analytics_workspace) | resource |
| [azurerm_machine_learning_compute_cluster.image_build](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/machine_learning_compute_cluster) | resource |
| [azurerm_machine_learning_compute_cluster.job_run](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/machine_learning_compute_cluster) | resource |
| [azurerm_machine_learning_workspace.mlw](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/machine_learning_workspace) | resource |
| [azurerm_private_endpoint.acr_pep](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_private_endpoint.kv_pep](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_private_endpoint.law_pep](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_private_endpoint.mlw_pep](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_private_endpoint.st_pep](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/private_endpoint) | resource |
| [azurerm_resource_group.rg](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_role_assignment.appi_monitoring_reader_uai](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.rg_reader_uai](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_storage_account.st](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account) | resource |
| [azurerm_storage_container.sc](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_container) | resource |
| [azurerm_subnet.resource](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subnet) | resource |
| [azurerm_user_assigned_identity.uami](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/user_assigned_identity) | resource |
| [azurerm_virtual_network.vnet](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/virtual_network) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_azure_monitor"></a> [azure\_monitor](#input\_azure\_monitor) | n/a | <pre>object({<br/>    appi = object({<br/>      name             = string<br/>      application_type = optional(string, "other")<br/>      tags             = optional(map(string), {})<br/>    })<br/>    law = object({<br/>      name = string<br/>      tags = optional(map(string), {})<br/>    })<br/>  })</pre> | n/a | yes |
| <a name="input_container_registry"></a> [container\_registry](#input\_container\_registry) | n/a | <pre>object({<br/>    name = string<br/>    sku  = optional(string, "Premium")<br/>    tags = optional(map(string), {})<br/>  })</pre> | n/a | yes |
| <a name="input_key_vault"></a> [key\_vault](#input\_key\_vault) | n/a | <pre>object({<br/>    name                       = string<br/>    sku_name                   = optional(string, "standard")<br/>    tags                       = optional(map(string), {})<br/>    soft_delete_retention_days = optional(number, 30)<br/>  })</pre> | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | n/a | `string` | n/a | yes |
| <a name="input_managed_identity"></a> [managed\_identity](#input\_managed\_identity) | n/a | <pre>object({<br/>    name = string<br/>    tags = optional(map(string), {})<br/>  })</pre> | n/a | yes |
| <a name="input_ml_workspace"></a> [ml\_workspace](#input\_ml\_workspace) | n/a | <pre>object({<br/>    name                 = string<br/>    tags                 = optional(map(string), {})<br/>    high_business_impact = optional(bool, true)<br/>    image_build_compute_cluster = optional(object({<br/>      vm_priority                          = optional(string, "LowPriority")<br/>      vm_size                              = optional(string, "Standard_DS3_v2")<br/>      min_node_count                       = optional(number, 0)<br/>      max_node_count                       = optional(number, 1)<br/>      scale_down_nodes_after_idle_duration = optional(string, "PT5M")<br/>      tags                                 = optional(map(string), {})<br/>      })<br/>    )<br/>    job_run_compute_cluster = optional(object({<br/>      vm_priority                          = optional(string, "LowPriority")<br/>      vm_size                              = optional(string, "Standard_DS3_v2")<br/>      min_node_count                       = optional(number, 0)<br/>      max_node_count                       = optional(number, 1)<br/>      scale_down_nodes_after_idle_duration = optional(string, "PT5M")<br/>      tags                                 = optional(map(string), {})<br/>      })<br/>    )<br/>    personal_compute_instances = optional(map(object({<br/>      vm_size                              = optional(string, "STANDARD_DS3_v2")<br/>      scale_down_nodes_after_idle_duration = optional(string, "PT30M")<br/>      tags                                 = optional(map(string), {})<br/>      assigned_user = optional(object({<br/>        object_id = string<br/>        tenant_id = optional(string, null)<br/>      }))<br/>    })))<br/>  })</pre> | n/a | yes |
| <a name="input_public_network_access_enabled"></a> [public\_network\_access\_enabled](#input\_public\_network\_access\_enabled) | enable public network access for the Azure resources | `bool` | `false` | no |
| <a name="input_resource_group"></a> [resource\_group](#input\_resource\_group) | n/a | <pre>object({<br/>    name = string<br/>    tags = optional(map(string), {})<br/>  })</pre> | n/a | yes |
| <a name="input_storage_account"></a> [storage\_account](#input\_storage\_account) | n/a | <pre>object({<br/>    name                              = string<br/>    account_tier                      = optional(string, "Standard")<br/>    account_replication_type          = optional(string, "LRS")<br/>    tags                              = optional(map(string), {})<br/>    account_kind                      = optional(string, "StorageV2")<br/>    is_hns_enabled                    = optional(bool, true)<br/>    infrastructure_encryption_enabled = optional(bool, true)<br/>    # example: {"container1": {"container_access_type": "private", "metadata": {"key1": "value1"}}}<br/>    storage_containers = optional(map(object({<br/>      container_access_type = optional(string, "private")<br/>      metadata              = optional(map(string), {})<br/>    })), {})<br/>  })</pre> | n/a | yes |
| <a name="input_tenant_id"></a> [tenant\_id](#input\_tenant\_id) | n/a | `string` | n/a | yes |
| <a name="input_uaa"></a> [uaa](#input\_uaa) | n/a | <pre>object({<br/>    client_id     = optional(string, "")<br/>    client_secret = optional(string, "")<br/>  })</pre> | n/a | yes |
| <a name="input_virtual_network"></a> [virtual\_network](#input\_virtual\_network) | n/a | <pre>object({<br/>    name          = string<br/>    tags          = optional(map(string), {})<br/>    address_space = optional(list(string), ["10.0.0.0/16"])<br/>    dns_servers   = optional(list(string), ["10.0.0.4", "10.0.0.5"])<br/>    # TODO: change to dictionary for multiple subnets<br/>    resource_subnet_address_prefixes = optional(list(string), ["10.0.1.0/24"])<br/>  })</pre> | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->