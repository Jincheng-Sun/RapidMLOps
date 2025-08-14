<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.9.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | >3.60.0,<4.15.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | >3.60.0,<4.15.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_resource_group.rg](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group) | resource |
| [azurerm_storage_account.sa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account) | resource |
| [azurerm_storage_container.sc](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_container) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_default_storage"></a> [default\_storage](#input\_default\_storage) | n/a | <pre>object({<br/>    name                     = string<br/>    account_tier             = optional(string, "Standard")<br/>    account_replication_type = optional(string, "LRS")<br/>    tags                     = optional(map(string), {})<br/>    # (Optional) Storage containers to create, the key will be the storage name and the value will be the metadata map of that container<br/>    storage_containers = optional(map(map(string)), {})<br/>  })</pre> | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | n/a | `string` | n/a | yes |
| <a name="input_resource_group"></a> [resource\_group](#input\_resource\_group) | n/a | <pre>object({<br/>    name = string<br/>    tags = optional(map(string), {})<br/>  })</pre> | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->