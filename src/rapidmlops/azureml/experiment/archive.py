from azure.ai.ml import MLClient

from rapidmlops.core.utils import get_logger
from rapidmlops.azureml.utils import get_ml_client

logger = get_logger(__name__)


def archive_experiment(name: str, ml_client: MLClient = None):
    """Archives an experiment/job in Azure Machine Learning workspace.

    Args:
        name (str): The Job name.
        version (str, optional): The version. Jobs normally don't use typical versioning
                                 but the SDK requires name mapping.
        ml_client (MLClient, optional): The MLClient instance.
    """
    if not ml_client:
        ml_client = get_ml_client(logger_name=__name__)

    try:
        # Jobs are typically archived by name (which acts as the run ID)
        ml_client.jobs.archive(name=name)
        logger.info(
            f"[INFO] Job {name} archived successfully in {ml_client.workspace_name}"
        )
    except Exception as e:
        logger.warning(f"[WARNING] Could not archive Job {name}: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Archive a job in Azure ML workspace")
    parser.add_argument("--name", type=str, help="The Job name.")
    args = parser.parse_args()
    archive_experiment(name=args.name)
