import argparse
import subprocess
import re
from rapidmlops.utils import get_logger
from rapidmlops.azureml.data_asset.create_or_update import main as create_or_update
from rapidmlops.azureml.data_asset.archive import main as archive

logger = get_logger(__name__)


def get_git_changes():
    """
    Executes git diff to find added, modified, and deleted files.
    Returns a dictionary of {file_path: 'A'/'M'/'D'}
    """
    try:
        # We use HEAD~1 to check against the previous commit. 
        # In a squashed PR merge, this gets the difference since the last merge baseline.
        result = subprocess.run(
            ["git", "diff", "--name-status", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Git diff failed. Ensure fetchDepth: 0 is set. Error: {e.stderr}")
        return {}

    changes = {}
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0][0]  # Get A, M, or D (handles cases like R100 rename)
            file_path = parts[-1]
            changes[file_path] = status
            
    return changes


def main(environment, name_override, commit_sha, pr_id, source_branch):
    changes = get_git_changes()
    
    # Kustomize path format: path/to/data/<asset_name>/<environment>/data.yaml
    pattern = re.compile(rf"data/([^/]+)/{environment}/.*\.yaml$")
    
    processed_count = 0
    for file_path, status in changes.items():
        match = pattern.search(file_path)
        if not match:
            continue
            
        asset_name = name_override if name_override else match.group(1)
        logger.info(f"Detected change in '{file_path}' for asset '{asset_name}' with git status '{status}'")
        
        if status in ['A', 'M', 'R', 'C']:
            logger.info(f"Creating/Updating Data Asset: {asset_name}")
            create_or_update(
                data_config_path=file_path,
                name=asset_name,
                commit_sha=commit_sha,
                pr_id=pr_id,
                source_branch=source_branch
            )
            processed_count += 1
        elif status == 'D':
            logger.info(f"Archiving Data Asset: {asset_name} (Warning: default version archived)")
            # In a real scenario, you'd archive all versions or a specific deleted version.
            archive(
                name=asset_name,
                version=None
            )
            processed_count += 1
            
    if processed_count == 0:
        logger.info(f"No Data Asset changes detected for environment: {environment}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gitops Data Asset Orchestrator")
    parser.add_argument("--environment", type=str, required=True, help="Target Environment (e.g., dev, prod)")
    parser.add_argument("--name", type=str, help="Optional name override")
    parser.add_argument("--commit_sha", type=str, help="Git commit sha")
    parser.add_argument("--pr_id", type=str, help="Pull Request ID")
    parser.add_argument("--source_branch", type=str, help="Source Branch")
    args = parser.parse_args()
    
    main(
        environment=args.environment, 
        name_override=args.name,
        commit_sha=args.commit_sha,
        pr_id=args.pr_id,
        source_branch=args.source_branch
    )
