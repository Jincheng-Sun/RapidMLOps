from azure.ai.ml import MLClient

from rapidmlops.core.utils import get_logger
from rapidmlops.azureml.utils import get_ml_client

logger = get_logger(__name__)


def archive_component(name: str, version: str = None, ml_client: MLClient = None):
    """Archives a component in Azure Machine Learning workspace.

    Args:
        name (str): The Component name.
        version (str, optional): The Component version, default is None (archive all versions).
        ml_client (MLClient, optional): The MLClient instance.
    """
    if not ml_client:
        ml_client = get_ml_client(logger_name=__name__)

    if version:
        ml_client.components.archive(name=name, version=version)
        logger.info(
            f"[INFO] Component {name}:{version} archived successfully in {ml_client.workspace_name}"
        )
    else:
        ml_client.components.archive(name=name)
        logger.info(
            f"[INFO] Component {name} (All versions) archived successfully in {ml_client.workspace_name}"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Archive a component in Azure ML workspace"
    )
    parser.add_argument("--name", type=str, help="The Component name.")
    parser.add_argument("--version", type=str, help="The Component version.")
    args = parser.parse_args()
    archive_component(name=args.name, version=args.version)
