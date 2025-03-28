import yaml

from azure.ai.ml.entities import Data

from scripts.azureml.utils import get_ml_client
from scripts.utils import get_logger

logger = get_logger(__name__)


def main(data_config_path: str,
         name: str = None,
         version: str = None,
         subscription_id: str = None,
         resource_group: str = None,
         workspace_name: str = None
         ):
    if subscription_id and resource_group and workspace_name:
        workspace_info = {"subscription_id": subscription_id,
                          "resource_group": resource_group,
                          "workspace_name": workspace_name
                          }
    else:
        workspace_info = None
    ml_client = get_ml_client(logger_name=__name__, workspace_info=workspace_info)
    with open(data_config_path, "r") as f:
        data_config = yaml.safe_load(f)
    if name and name != data_config["name"] or version and version != data_config["version"]:
        raise ValueError(f"The name and version in the data asset config file "
                         f"should be consistent with the input name and version, "
                         f"but got input name: {name} and version: {version} "
                         f"and in the config file name: {data_config['name']} and version: {data_config['version']}"
                         )
    logger.info(f"[INFO] Load Data Asset configuration: {data_config}")
    data_asset = Data(type=data_config["type"],
                      name=data_config["name"],
                      version=data_config["version"],
                      description=data_config["description"],
                      path=data_config["path"]
                      )
    ml_client.data.create_or_update(data_asset)
    logger.info(f"[INFO] Data Asset {data_asset.name}:{data_asset.version} created/updated successfully "
                f"in {ml_client.workspace_name}"
                )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create or update a data asset in Azure Machine Learning workspace")
    parser.add_argument("--data_config_path", type=str, required=True, help="The path to the data asset configuration.")
    parser.add_argument("--name",
                        type=str,
                        help="The Data Asset name."
                        )
    parser.add_argument("--version",
                        type=str,
                        help="The Data Asset version."
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
    parser.add_argument("--workspace_name",
                        type=str,
                        default=None,
                        help="The name of the Azure Machine Learning workspace."
                        )
    args = parser.parse_args()
    main(data_config_path=args.data_config_path,
         name=args.name,
         version=args.version,
         subscription_id=args.subscription_id,
         resource_group=args.resource_group,
         workspace_name=args.workspace_name
         )
