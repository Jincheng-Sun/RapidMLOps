terraform {
  required_version = ">=1.9.0"

  required_providers {
    azurerm = {
      source                = "hashicorp/azurerm"
      version               = ">3.60.0,<=4.15.0"
      configuration_aliases = [azurerm.uaa]
    }
    azapi = {
      source  = "azure/azapi"
      version = "2.4.0"
    }
  }
}
provider "azurerm" {
  alias = "uaa"
  features {}
  storage_use_azuread = true
  client_id           = var.uaa.client_id
  client_secret       = var.uaa.client_secret
}