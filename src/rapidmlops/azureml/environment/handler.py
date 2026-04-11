import argparse
import re

from rapidmlops.core.utils import get_logger, get_git_changes
from rapidmlops.azureml.environment.create_or_update import create_or_update_environment
from rapidmlops.azureml.environment.archive import archive_environment

logger = get_logger(__name__)


def handle_environment_gitops(
    environment,
    commit_sha=None,
    pr_id=None,
    source_branch=None,
    environment_folder="environments",
    environment_config_file="environment.yaml",
):
    """Handles environment changes based on git status.

    Args:
        environment (str): The target environment (e.g., dev, prod).
        commit_sha (str, optional): The Git Commit SHA (determines Environment Version).
        pr_id (str, optional): The Pull Request ID for lineage.
        source_branch (str, optional): The branch name serving as secondary lineage.
        environment_folder (str, optional): The folder containing environment configurations, default is "environments".
        environment_config_file (str, optional): The path to the environment configuration file, default is "environment.yaml".
    """

    changes = get_git_changes()

    pattern = re.compile(
        rf"{environment_folder}/([^/]+)/{environment}/{environment_config_file}$"
    )

    processed_count = 0
    for file_path, status in changes.items():
        match = pattern.search(file_path)
        if not match:
            continue

        asset_name = match.group(1)
        logger.info(
            f"Detected change in '{file_path}' for asset '{asset_name}' with git status '{status}'"
        )

        if status in ["A", "M"]:
            logger.info(f"Creating/Updating Environment: {asset_name}")
            create_or_update_environment(
                environment_config_path=file_path,
                name=asset_name,
                commit_sha=commit_sha,
                pr_id=pr_id,
                source_branch=source_branch,
            )
            processed_count += 1
        elif status == "D":
            logger.info(
                f"Archiving Environment: {asset_name} (Warning: default version archived)"
            )
            # In a real scenario, you'd archive all versions or a specific deleted version.
            archive_environment(name=asset_name, version=None)
            processed_count += 1

    if processed_count == 0:
        logger.info(f"No Environment changes detected for environment: {environment}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gitops Environment Orchestrator")
    parser.add_argument(
        "--environment",
        type=str,
        required=True,
        help="Target Environment (e.g., dev, prod)",
    )
    parser.add_argument("--commit_sha", type=str, help="Git commit sha")
    parser.add_argument("--pr_id", type=str, help="Pull Request ID")
    parser.add_argument("--source_branch", type=str, help="Remote branch name")
    parser.add_argument("--environment_folder", type=str, default="environments")
    parser.add_argument(
        "--environment_config_file", type=str, default="environment.yaml"
    )
    args = parser.parse_args()

    handle_environment_gitops(
        environment=args.environment,
        commit_sha=args.commit_sha,
        pr_id=args.pr_id,
        source_branch=args.source_branch,
        environment_folder=args.environment_folder,
        environment_config_file=args.environment_config_file,
    )
