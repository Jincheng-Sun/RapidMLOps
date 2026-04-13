from azure.ai.ml import MLClient, load_component

from rapidmlops.core.utils import get_logger
from rapidmlops.azureml.utils import get_ml_client


logger = get_logger(__name__)


def create_or_update_component(
    component_config_path: str,
    name: str = None,
    commit_sha: str = None,
    pr_id: str = None,
    source_branch: str = None,
    ml_client: MLClient = None,
):
    """Creates or updates a component in Azure Machine Learning workspace.

    Args:
        component_config_path (str): The path to the component configuration.
        name (str, optional): The Component name, default is None.
        commit_sha (str, optional): The Git Commit SHA (determines Version).
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
    params_override = overrides if overrides else None

    logger.info(f"[INFO] Loading Component configuration from: {component_config_path}")
    component = load_component(
        source=component_config_path, params_override=params_override
    )

    tags = component.tags if component.tags else {}
    if commit_sha:
        tags["git_commit_sha"] = commit_sha
    if pr_id:
        tags["pr_id"] = pr_id
    if source_branch:
        tags["source_branch"] = source_branch

    if tags:
        component.tags = tags

    ml_client.components.create_or_update(component)
    logger.info(
        f"[INFO] Component {component.name}:{component.version} created/updated successfully "
        f"in {ml_client.workspace_name}"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Create or update a component in Azure Machine Learning workspace"
    )
    parser.add_argument(
        "--component_config_path",
        type=str,
        required=True,
        help="The path to the component configuration.",
    )
    parser.add_argument("--name", type=str, help="Optional name override.")
    parser.add_argument("--commit_sha", type=str, help="Commit SHA.")
    parser.add_argument("--pr_id", type=str, help="Pull Request ID.")
    parser.add_argument("--source_branch", type=str, help="Source Branch.")

    args = parser.parse_args()
    create_or_update_component(
        component_config_path=args.component_config_path,
        name=args.name,
        commit_sha=args.commit_sha,
        pr_id=args.pr_id,
        source_branch=args.source_branch,
    )
