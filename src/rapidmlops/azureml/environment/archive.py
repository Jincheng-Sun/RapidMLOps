from azure.ai.ml import MLClient

from rapidmlops.core.utils import get_logger
from rapidmlops.azureml.utils import get_ml_client

logger = get_logger(__name__)


def archive_environment(name: str, version: str = None, ml_client: MLClient = None):
    """Archives a environment in Azure Machine Learning workspace.

    Args:
        name (str): The Environment name.
        version (str, optional): The Environment version, default is None (archive all versions).
        ml_client (MLClient, optional): The MLClient instance.
    """
    if not ml_client:
        ml_client = get_ml_client(logger_name=__name__)

    if version:
        ml_client.environments.archive(name=name, version=version)
        logger.info(
            f"[INFO] Environment {name}:{version} archived successfully in {ml_client.workspace_name}"
        )
    else:
        ml_client.environments.archive(name=name)
        logger.info(
            f"[INFO] Environment {name} (All versions) archived successfully in {ml_client.workspace_name}"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Archive a environment in Azure Machine Learning workspace"
    )
    parser.add_argument("--name", type=str, help="The Environment name.")
    parser.add_argument("--version", type=str, help="The Environment version.")
    args = parser.parse_args()
    archive_environment(name=args.name, version=args.version)
