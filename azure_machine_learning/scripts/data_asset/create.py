import yaml

from azure.ai.ml import load_data

from azure_machine_learning.scripts.utils import get_logger
from azure_machine_learning.scripts.azureml_utils import get_ml_client

logger = get_logger(__name__)


def main(data_config_path: str,
         name: str = None,
         version: str = None,
         workspace_name: str = None,
         subscription_id: str = None,
         resource_group: str = None,
         ):
    """Create a Data Asset in a given workspace/registry according to the input Data Asset configuration, if
    workspace/registry information is not provided, assuming there exists a session configuration file 'config.json'
    in the execution environment.

    Args:
        data_config_path: str, path to the data configuration file, the schema
            should follow https://azuremlschemas.azureedge.net/latest/data.schema.json
        name: str, default to None, name of the Data Asset to register, input to validate with the configuration file.
        version: str, default to None, version of the Data Asset to register, input to validate with
            the configuration file.
        workspace_name: str, default to None, name of AML workspace to create the Data Asset to.
        subscription_id: str, default to None, workspace/registry's subscription id.
        resource_group: str, default to None, workspace/registry's resource group name.
    """
    if workspace_name:
        workspace_info = {"subscription_id": subscription_id,
                          "resource_group": resource_group,
                          "workspace_name": workspace_name,
                          }
    else:
        workspace_info = None
    ml_client = get_ml_client(workspace_info=workspace_info, logger=logger)
    with open(data_config_path, "r") as f:
        data_config = yaml.safe_load(f)
    if name and name != data_config["name"] or version and version != data_config["version"]:
        error_message = f"The name and version in the Data Asset configuration file should be consistent with the " \
                        f"input name and version, getting name: {data_config['name']} and version: " \
                        f"{data_config['version']} in the configuration file, and input name: " \
                        f"{name} and version: {version}."
        logger.error(f"[ERROR] {error_message}")
        raise ValueError(error_message)
    logger.info(f"[INFO] Load Data Asset configuration: {data_config}")
    data_asset = load_data(data_config)
    ml_client.data.create_or_update(data_asset)
    logger.info(f"[INFO] Data Asset {data_asset.name}:{data_asset.version} created successfully "
                f"in {ml_client.workspace_name}"
                )
    del ml_client


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create a Data Asset in Azure Machine Learning workspace/registry")
    parser.add_argument("--data_config_path", type=str, required=True, help="Path to the Data Asset configuration.")
    parser.add_argument("--workspace_name",
                        type=str,
                        default=None,
                        help="Name of the Azure Machine Learning workspace."
                        )
    parser.add_argument("--name",
                        type=str,
                        default=None,
                        help="Name of the Data Asset to create."
                        )
    parser.add_argument("--version",
                        type=str,
                        default=None,
                        help="Version of the Data Asset to create."
                        )
    parser.add_argument("--subscription_id",
                        type=str,
                        default=None,
                        help="Subscription id of the Azure Machine Learning workspace."
                        )
    parser.add_argument("--resource_group",
                        type=str,
                        default=None,
                        help="Resource group of the Azure Machine Learning workspace."
                        )
    args = parser.parse_args()
    main(data_config_path=args.data_config_path,
         name=args.name,
         version=args.version,
         workspace_name=args.workspace_name,
         subscription_id=args.subscription_id,
         resource_group=args.resource_group,
         )
