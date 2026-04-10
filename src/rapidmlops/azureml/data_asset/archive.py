from azure.ai.ml import MLClient

from rapidmlops.core.utils import get_logger
from rapidmlops.azureml.utils import get_ml_client

logger = get_logger(__name__)


def archive_data_asset(name: str, version: str = None, ml_client: MLClient = None):
    """Archives a data asset in Azure Machine Learning workspace.

    Args:
        name (str): The Data Asset name.
        version (str, optional): The Data Asset version, default is None (archive all versions).
        ml_client (MLClient, optional): The MLClient instance.
    """
    if not ml_client:
        ml_client = get_ml_client(logger_name=__name__)

    if version:
        ml_client.data.archive(name=name, version=version)
        logger.info(
            f"[INFO] Data Asset {name}:{version} archived successfully in {ml_client.workspace_name}"
        )
    else:
        ml_client.data.archive(name=name)
        logger.info(
            f"[INFO] Data Asset {name} (All versions) archived successfully in {ml_client.workspace_name}"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Archive a data asset in Azure Machine Learning workspace"
    )
    parser.add_argument("--name", type=str, help="The Data Asset name.")
    parser.add_argument("--version", type=str, help="The Data Asset version.")
    args = parser.parse_args()
    archive_data_asset(name=args.name, version=args.version)
