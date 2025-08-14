variable "location" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "public_network_access_enabled" {
  description = "enable public network access for the Azure resources"
  type        = bool
  default     = false
}

variable "resource_group" {
  type = object({
    name = string
    tags = optional(map(string), {})
  })
}

variable "azure_monitor" {
  type = object({
    appi = object({
      name             = string
      application_type = optional(string, "other")
      tags             = optional(map(string), {})
    })
    law = object({
      name = string
      tags = optional(map(string), {})
    })
  })
}

variable "key_vault" {
  type = object({
    name                       = string
    sku_name                   = optional(string, "standard")
    tags                       = optional(map(string), {})
    soft_delete_retention_days = optional(number, 30)
  })
}

variable "storage_account" {
  type = object({
    name                              = string
    account_tier                      = optional(string, "Standard")
    account_replication_type          = optional(string, "LRS")
    tags                              = optional(map(string), {})
    account_kind                      = optional(string, "StorageV2")
    is_hns_enabled                    = optional(bool, true)
    infrastructure_encryption_enabled = optional(bool, true)
    # example: {"container1": {"container_access_type": "private", "metadata": {"key1": "value1"}}}
    storage_containers = optional(map(object({
      container_access_type = optional(string, "private")
      metadata              = optional(map(string), {})
    })), {})
  })
}

variable "container_registry" {
  type = object({
    name = string
    sku  = optional(string, "Premium")
    tags = optional(map(string), {})
  })
}

variable "managed_identity" {
  type = object({
    name = string
    tags = optional(map(string), {})
  })
}

variable "ml_workspace" {
  type = object({
    name                 = string
    tags                 = optional(map(string), {})
    high_business_impact = optional(bool, true)
    image_build_compute_cluster = optional(object({
      vm_priority                          = optional(string, "LowPriority")
      vm_size                              = optional(string, "Standard_DS3_v2")
      min_node_count                       = optional(number, 0)
      max_node_count                       = optional(number, 1)
      scale_down_nodes_after_idle_duration = optional(string, "PT5M")
      tags                                 = optional(map(string), {})
      })
    )
    job_run_compute_cluster = optional(object({
      vm_priority                          = optional(string, "LowPriority")
      vm_size                              = optional(string, "Standard_DS3_v2")
      min_node_count                       = optional(number, 0)
      max_node_count                       = optional(number, 1)
      scale_down_nodes_after_idle_duration = optional(string, "PT5M")
      tags                                 = optional(map(string), {})
      })
    )
    personal_compute_instances = optional(map(object({
      vm_size                              = optional(string, "STANDARD_DS3_v2")
      scale_down_nodes_after_idle_duration = optional(string, "PT30M")
      tags                                 = optional(map(string), {})
      assigned_user = optional(object({
        object_id = string
        tenant_id = optional(string, null)
      }))
    })))
  })
}

variable "virtual_network" {
  type = object({
    name          = string
    tags          = optional(map(string), {})
    address_space = optional(list(string), ["10.0.0.0/16"])
    dns_servers   = optional(list(string), ["10.0.0.4", "10.0.0.5"])
    # TODO: change to dictionary for multiple subnets
    resource_subnet_address_prefixes = optional(list(string), ["10.0.1.0/24"])
  })
}

variable "uaa" {
  type = object({
    client_id     = optional(string, "")
    client_secret = optional(string, "")
  })
}