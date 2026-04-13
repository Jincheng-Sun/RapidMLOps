import argparse
import re
import yaml

from rapidmlops.core.utils import get_logger, get_git_changes
from rapidmlops.azureml.component.create_or_update import create_or_update_component
from rapidmlops.azureml.component.archive import archive_component

logger = get_logger(__name__)


def handle_component_gitops(
    environment,
    commit_sha=None,
    pr_id=None,
    source_branch=None,
    component_folder="components",
    component_config_file="component.yaml",
):
    """Handles component changes based on git status with Two-Pass Topological sorting.

    Args:
        environment (str): The target environment (e.g., dev, prod).
        commit_sha (str, optional): Git Commit SHA.
        pr_id (str, optional): Pull Request ID.
        source_branch (str, optional): Source branch.
        component_folder (str, optional): Folder containing components.
        component_config_file (str, optional): Configuration filename.
    """
    changes = get_git_changes()

    # The pattern explicitly avoids matching the 'environment' in component paths
    # because components are typically shared across environments (workspace level isolation not required natively, 
    # but we can adhere strictly to the pattern if components are environment specific.
    
    # Matches either a global component OR an environment-specific component.
    # Ex 1: components/prep-raw-data/component.yaml  (Applies to ALL environments)
    # Ex 2: components/prep-raw-data/prod/component.yaml (Applies ONLY to prod environment)
    pattern = re.compile(rf"{component_folder}/([^/]+)/(?:{environment}/)?{component_config_file}$")

    command_creates = []
    pipeline_creates = []
    archives = []

    # Filter and categorize
    for file_path, status in changes.items():
        match = pattern.search(file_path)
        if not match:
            continue

        asset_name = match.group(1)

        if status in ["A", "M"]:
            # Peep the YAML to determine type for topological sorting
            comp_type = "command"
            try:
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f)
                    comp_type = data.get("type", "command")
            except Exception as e:
                logger.warning(f"Could not parse type for {file_path}, defaulting to command: {e}")

            if comp_type == "pipeline":
                pipeline_creates.append((file_path, asset_name))
            else:
                command_creates.append((file_path, asset_name))
                
        elif status == "D":
            archives.append(asset_name)

    processed_count = 0

    # Pass 1: Command Components (Foundation)
    for file_path, asset_name in command_creates:
        logger.info(f"Creating/Updating Command Component: {asset_name}")
        create_or_update_component(
            component_config_path=file_path,
            name=asset_name, # Overrides might not be needed if yaml natively defines it, but passed for consistency
            commit_sha=commit_sha,
            pr_id=pr_id,
            source_branch=source_branch,
            registry_name=registry_name,
        )
        processed_count += 1

    # Pass 2: Pipeline Components (Which depend on Commands)
    for file_path, asset_name in pipeline_creates:
        logger.info(f"Creating/Updating Pipeline Component: {asset_name}")
        create_or_update_component(
            component_config_path=file_path,
            name=asset_name,
            commit_sha=commit_sha,
            pr_id=pr_id,
            source_branch=source_branch,
            registry_name=registry_name,
        )
        processed_count += 1

    # Pass 3: Archiving
    for asset_name in archives:
        logger.info(f"Archiving Component: {asset_name} (Warning: default version archived)")
        archive_component(name=asset_name, version=None)
        processed_count += 1

    if processed_count == 0:
        logger.info(f"No Component changes detected for environment: {environment}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gitops Component Orchestrator")
    parser.add_argument("--environment", type=str, required=True)
    parser.add_argument("--commit_sha", type=str)
    parser.add_argument("--pr_id", type=str)
    parser.add_argument("--source_branch", type=str)
    parser.add_argument("--component_folder", type=str, default="components")
    parser.add_argument("--component_config_file", type=str, default="component.yaml")
    
    args = parser.parse_args()

    handle_component_gitops(
        environment=args.environment,
        commit_sha=args.commit_sha,
        pr_id=args.pr_id,
        source_branch=args.source_branch,
        component_folder=args.component_folder,
        component_config_file=args.component_config_file,
    )
