import time
import logging

from azure.identity import AzureCliCredential
from azure.ai.ml import MLClient


def get_ml_client(retry_times: int = 5,
                  retry_interval: int = 10,
                  workspace_info: dict = None,
                  logger: logging.Logger = None
                  ):
    """Build a session with Azure Machine Learning workspace.

    Args:
        retry_times: int, default to 5, the number of times to retry if the connection fails.
        retry_interval: int, default to 10, the interval between retries.
        workspace_info: dict, default to None, the information of the Azure Machine Learning workspace, equivalent to
            the input parameters of azure.ai.ml.MLClient except for the credential, e.g. subscription_id,
            resource_group, and workspace_name, if provided, the session will be created with this information,
            else, assuming there is a session config file 'config.json' in the execution environment.
        logger: logging.Logger, default to None, the logger instance passed in from the caller module.

    Raises:
        Any exception: If the connection still fails after retrying certain times, raise any exception that
            azure package throws.

    Returns:
        MLClient: The session with Azure Machine Learning workspace.
    """
    if not logger:
        logger = logging.getLogger(__name__)

    for i in range(retry_times):
        try:
            credential = AzureCliCredential()
            if not workspace_info:
                ml_client = MLClient.from_config(credential=credential, path="config.json")
            else:
                ml_client = MLClient(credential=credential, **workspace_info)
            # Since MLClient uses a lazy execution style with the session, try listing out to compute(s) to
            # validate the connection
            ml_client.compute.list()
            logger.info(f"Successfully connected to {ml_client.workspace_name}")
            return ml_client
        except Exception as e:
            logger.error(f"Failed to create MLClient, retrying... {i + 1}/{retry_times}")
            logger.error(e)
            time.sleep(retry_interval)
