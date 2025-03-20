import sys
import time
import logging

from azure.identity import AzureCliCredential
from azure.ai.ml import MLClient


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a logger with the specified name and level. The logger will log to stdout.

    Args:
        name: str, The name of the logger.
        level: int, The logging level.

    Returns:
        logging.Logger: The logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def get_ml_client(logger_name: str, retry_times: int = 5, retry_interval: int = 10, workspace_info: dict = None):
    """Build a session with Azure Machine Learning workspace.

    Args:
        logger_name: str, The name of the logger.
        retry_times: int, The number of times to retry if the connection fails.
        retry_interval: int, The interval between retries.
        workspace_info: dict, The information of the Azure Machine Learning workspace, including subscription_id,
            resource_group, and workspace_name, if provided, the session will be created with this information.

    Raises:
        Exception: If the connection fails after retrying.

    Returns:
        MLClient: The session with Azure Machine Learning workspace.
    """
    logger = logging.getLogger(logger_name)

    for i in range(retry_times):
        try:
            credential = AzureCliCredential()
            if not workspace_info:
                ml_client = MLClient.from_config(credential=credential, path="config.json")
            else:
                ml_client = MLClient(credential=credential,
                                     subscription_id=workspace_info["subscription_id"],
                                     resource_group=workspace_info["resource_group"],
                                     workspace_name=workspace_info["workspace_name"]
                                     )
            ml_client.compute.list()
            logger.info(f"Successfully connected to {ml_client.workspace_name}")
            return ml_client
        except Exception as e:
            logger.error(f"Failed to create MLClient, retrying... {i + 1}/{retry_times}")
            logger.error(e)
            time.sleep(retry_interval)
