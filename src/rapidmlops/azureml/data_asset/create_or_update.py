from azure.ai.ml import MLClient, load_data

from rapidmlops.core.utils import get_logger
from rapidmlops.azureml.utils import get_ml_client


logger = get_logger(__name__)


def create_or_update_data_asset(
    data_config_path: str,
    name: str = None,
    commit_sha: str = None,
    pr_id: str = None,
    source_branch: str = None,
    ml_client: MLClient = None,
):
    """Creates or updates a data asset in Azure Machine Learning workspace.

    Args:
        data_config_path (str): The path to the data asset configuration.
        name (str, optional): The Data Asset name, default is None (use the name from the data config file).
        commit_sha (str, optional): The Git Commit SHA (determines Asset Version).
        pr_id (str, optional): The Pull Request ID for lineage.
        source_branch (str, optional): The branch name serving as secondary lineage.
        ml_client (MLClient, optional): The MLClient instance.
    """

    if not ml_client:
        ml_client = get_ml_client(logger_name=__name__)

    overrides = []
    if name:
        overrides.append({"name": name})
    if commit_sha:
        overrides.append({"version": commit_sha})

    tags = {}
    if commit_sha:
        tags["git_commit_sha"] = commit_sha
    if pr_id:
        tags["pr_id"] = pr_id
    if source_branch:
        tags["source_branch"] = source_branch

    if tags:
        overrides.append({"tags": tags})

    params_override = overrides if overrides else None

    logger.info(f"[INFO] Loading Data Asset configuration from: {data_config_path}")
    data_asset = load_data(source=data_config_path, params_override=params_override)

    ml_client.data.create_or_update(data_asset)
    logger.info(
        f"[INFO] Data Asset {data_asset.name}:{data_asset.version} created/updated successfully "
        f"in {ml_client.workspace_name}"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create or update a data asset in Azure Machine Learning workspace"
    )
    parser.add_argument(
        "--data_config_path",
        type=str,
        required=True,
        help="The path to the data asset configuration.",
    )
    parser.add_argument(
        "--name", type=str, help="The Data Asset name (optional override)."
    )
    parser.add_argument(
        "--commit_sha", type=str, help="The Git Commit SHA (determines Asset Version)."
    )
    parser.add_argument("--pr_id", type=str, help="The Pull Request ID for lineage.")
    parser.add_argument(
        "--source_branch",
        type=str,
        help="The branch name serving as secondary lineage.",
    )
    args = parser.parse_args()
    create_or_update_data_asset(
        data_config_path=args.data_config_path,
        name=args.name,
        commit_sha=args.commit_sha,
        pr_id=args.pr_id,
        source_branch=args.source_branch,
    )
