import time
import logging

from azure.identity import AzureCliCredential
from azure.ai.ml import MLClient


def get_ml_client(
    logger_name: str = "RapidMLOps",
    retry_times: int = 5,
    retry_interval: int = 30,
    subscription_id: str = None,
    resource_group: str = None,
    workspace_name: str = None,
    registry_name: str = None,
    config_path: str = "config.json",
):
    """Build a session with Azure Machine Learning workspace.

    Args:
        logger_name: str, the name of the logger.
        retry_times: int, the number of times to retry if the connection fails.
        retry_interval: int, the interval between retries.
        subscription_id: str, optional, the subscription id of the Azure Machine Learning workspace.
        resource_group: str, optional, the resource group of the Azure Machine Learning workspace.
        workspace_name: str, optional, the name of the Azure Machine Learning workspace.
        registry_name: str, optional, the name of the Azure Machine Learning registry.
        config_path: str, optional, the path to the Azure Machine Learning workspace configuration file.

    Raises:
        Exception: If the connection fails after retrying.

    Returns:
        MLClient: The session with Azure Machine Learning workspace.
    """
    logger = logging.getLogger(logger_name)

    for i in range(retry_times):
        try:
            credential = AzureCliCredential()
            if subscription_id and resource_group and workspace_name:
                ml_client = MLClient(
                    credential=credential,
                    subscription_id=subscription_id,
                    resource_group=resource_group,
                    workspace_name=workspace_name,
                )
                ml_client.compute.list()
                logger.info(
                    f"Successfully connected to workspace {ml_client.workspace_name}"
                )
                return ml_client
            elif subscription_id and resource_group and registry_name:
                ml_client = MLClient(
                    credential=credential,
                    subscription_id=subscription_id,
                    resource_group=resource_group,
                    registry_name=registry_name,
                )
                ml_client.compute.list()
                logger.info(
                    f"Successfully connected to registry {ml_client.registry_name}"
                )
                return ml_client
            else:
                ml_client = MLClient.from_config(
                    credential=credential, path=config_path
                )
                ml_client.compute.list()
                logger.info(
                    f"No workspace or registry information provided, using config file at {config_path}"
                )
                return ml_client
        except Exception as e:
            logger.error(
                f"[ERROR] Failed to create MLClient, retrying... {i + 1}/{retry_times}, {e}"
            )
            time.sleep(retry_interval)
    raise Exception("Failed to create MLClient after retrying")
