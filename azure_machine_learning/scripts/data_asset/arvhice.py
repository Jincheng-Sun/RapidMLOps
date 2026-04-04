from azure_machine_learning.scripts.utils import get_logger
from azure_machine_learning.scripts.azureml_utils import get_ml_client

logger = get_logger(__name__)


def main(name: str,
         version: str,
         workspace_name: str = None,
         registry_name: str = None,
         subscription_id: str = None,
         resource_group: str = None,
         ):
    """Archive a Data Asset in Azure Machine Learning workspace or registry.

    Args:
        name: str, name of the Data Asset to archive.
        version: str, version of the Data Asset to archive.
        workspace_name: str, default to None, name of AML workspace to archive the Data Asset to.
        registry_name: str, default to None, name of AML registry to archive the Data Asset to, this will
            be ignored if the workspace name is provided.
        subscription_id: str, default to None, workspace/registry's subscription id.
        resource_group: str, default to None, workspace/registry's resource group name.
    """
    if workspace_name:
        workspace_info = {"subscription_id": subscription_id,
                          "resource_group": resource_group,
                          "workspace_name": workspace_name,
                          }
    elif registry_name:
        workspace_info = {"subscription_id": subscription_id,
                          "resource_group": resource_group,
                          "registry_name": registry_name,
                          }
    else:
        workspace_info = None
    ml_client = get_ml_client(workspace_info=workspace_info, logger=logger)
    ml_client.data.archive(name=name, version=version)
    logger.info(f"[INFO] Data Asset {name}:{version} archived successfully in {ml_client.workspace_name}")
    del ml_client


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Archive a Data Asset in Azure Machine Learning workspace/registry")
    parser.add_argument("--name",
                        type=str,
                        required=True,
                        help="Name of the Data Asset to archive."
                        )
    parser.add_argument("--version",
                        type=str,
                        required=True,
                        help="Version of the Data Asset to archive."
                        )
    parser.add_argument("--workspace_name",
                        type=str,
                        default=None,
                        help="Name of the Azure Machine Learning workspace."
                        )
    parser.add_argument("--registry_name",
                        type=str,
                        default=None,
                        help="Name of the Azure Machine Learning registry, "
                             "if workspace_name is provided, this will be ignored"
                        )
    parser.add_argument("--subscription_id",
                        type=str,
                        default=None,
                        help="The subscription id of the Azure Machine Learning workspace."
                        )
    parser.add_argument("--resource_group",
                        type=str,
                        default=None,
                        help="The resource group of the Azure Machine Learning workspace."
                        )
    args = parser.parse_args()
    main(name=args.name,
         version=args.version,
         workspace_name=args.workspace_name,
         registry_name=args.registry_name,
         subscription_id=args.subscription_id,
         resource_group=args.resource_group,
         )
