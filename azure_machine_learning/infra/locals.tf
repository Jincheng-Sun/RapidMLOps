locals {
  storage_required_args = {
    location                 = var.location
    name                     = var.default_storage.name
    resource_group_name      = azurerm_resource_group.rg.name
    tags                     = var.default_storage.tags
    account_tier             = var.default_storage.access_tier
    account_replication_type = var.default_storage.account_replication_type
  }
  storage_args = merge(local.storage_required_args, var.default_storage.optional_args)
}