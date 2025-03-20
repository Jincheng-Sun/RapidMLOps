import yaml
import argparse

from azure.ai.ml.entities import Data

from utils import get_logger, get_ml_client

logger = get_logger(__name__)


def main(data_config_path: str, subscription_id: str = None, resource_group: str = None, workspace_name: str = None):
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
    logger.info(f"[INFO] Load Data Asset configuration: {data_config}")
    data_asset = Data(type=data_config["type"],
                      name=data_config["name"],
                      version=data_config["version"],
                      description=data_config["description"],
                      path=data_config["path"]
                      )
    ml_client.data.create_or_update(data_asset)
    logger.info(f"[INFO] Data Asset {data_asset.name}:{data_asset.version} created successfully "
                f"in {ml_client.workspace_name}"
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a data asset in Azure Machine Learning workspace")
    parser.add_argument("--data_config_path", type=str, required=True, help="The path to the data asset configuration.")
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
         subscription_id=args.subscription_id,
         resource_group=args.resource_group,
         workspace_name=args.workspace_name
         )
