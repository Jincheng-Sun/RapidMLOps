import yaml

from azure.ai.ml.entities import Data

from scripts.azureml.utils import get_ml_client
from scripts.utils import get_logger

logger = get_logger(__name__)


def main(name: str,
         version: str,
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
    ml_client.data.archive(name=name, version=version)
    logger.info(f"[INFO] Data Asset {name}:{version} archived successfully "
                f"in {ml_client.workspace_name}"
                )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Archive a data asset in Azure Machine Learning workspace")
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
    main(name=args.name,
         version=args.version,
         subscription_id=args.subscription_id,
         resource_group=args.resource_group,
         workspace_name=args.workspace_name
         )
