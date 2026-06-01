import os
import argparse
import re
import subprocess

from rapidmlops.core.utils import get_logger, get_git_changes
from rapidmlops.azureml.experiment.create_or_update import create_or_update_experiment
from rapidmlops.azureml.experiment.archive import archive_experiment

logger = get_logger(__name__)


def handle_experiment_gitops(
    environment,
    commit_sha=None,
    pr_id=None,
    source_branch=None,
    compute_name=None,
    experiment_folder="experiments",
):
    """Handles experiment changes using a File-Type Logic Gate.
    Routes to native SDK for YAMLs, or Subprocess BASH for Custom Python execution.

    Args:
        environment (str): The target environment (e.g., dev, prod).
        commit_sha (str, optional): Git Commit SHA.
        pr_id (str, optional): Pull Request ID.
        source_branch (str, optional): Source branch.
        compute_name (str, optional): The target cluster for compute.
        experiment_folder (str, optional): Folder containing experiments.
    """
    changes = get_git_changes()

    # Match either `experiment.yaml` or `run_pipeline.py`.
    # Capture Group 1: Asset Name
    # Capture Group 2: File Name (The Logic Switch)
    pattern = re.compile(
        rf"{experiment_folder}/([^/]+)/(?:{environment}/)?(\.?experiment\.yaml|\.?run_pipeline\.py)$"
    )

    processed_count = 0
    for file_path, status in changes.items():
        match = pattern.search(file_path)
        if not match:
            continue

        # Asset name is the parent folder name.
        # e.g. experiments/credit-risk/prod/experiment.yaml -> asset_name = credit-risk
        asset_name = match.group(1)
        file_name = match.group(2)
        logger.info(
            f"Detected change in '{file_path}' for asset '{asset_name}' with git status '{status}'"
        )

        # Global experiment pattern
        # TODO: make this a configurable pattern
        global_experiment_pattern = os.environ.get(
            "GLOBAL_EXPERIMENT_PATTERN", f"{environment}-{{}}-{{}}"
        )
        global_registered_model_pattern = os.environ.get(
            "GLOBAL_REGISTERED_MODEL_PATTERN", f"{environment}-{{}}-{{}}"
        )
        global_experiment_name = global_experiment_pattern.format(
            asset_name, commit_sha
        )
        global_registered_model_name = global_registered_model_pattern.format(
            asset_name, commit_sha
        )

        if status in ["A", "M"]:
            if file_name in ["experiment.yaml", ".experiment.yaml"]:
                logger.info(
                    f"Loading job definition YAML file for experiment {asset_name}"
                )
                create_or_update_experiment(
                    experiment_config_path=file_path,
                    experiment_name=global_experiment_name,
                    registered_model_name=global_registered_model_name,
                    commit_sha=commit_sha,
                    pr_id=pr_id,
                    source_branch=source_branch,
                )
                processed_count += 1

            elif file_name in ["run_pipeline.py", ".run_pipeline.py"]:
                logger.info(
                    f"Executing custom python script for experiment {asset_name}"
                )
                cmd = [
                    "python",
                    file_path,
                    "--environment",
                    environment,
                    "--experiment_name",
                    global_experiment_name,
                    "--registered_model_name",
                    global_registered_model_name,
                ]
                if compute_name:
                    cmd.extend(["--compute_name", compute_name])
                if commit_sha:
                    cmd.extend(["--commit_sha", commit_sha])
                if pr_id:
                    cmd.extend(["--pr_id", pr_id])
                if source_branch:
                    cmd.extend(["--source_branch", source_branch])

                logger.info(f"Invoking Subprocess: {' '.join(cmd)}")
                subprocess.run(cmd, check=True)
                processed_count += 1

        elif status == "D":
            # Just log archival conceptually, pipeline jobs usually aren't archived by string trigger.
            logger.info(f"Archiving Experiment: {global_experiment_name}")
            archive_experiment(name=global_experiment_name)
            processed_count += 1

    if processed_count == 0:
        logger.info(f"No Experiment changes detected for environment: {environment}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gitops Experiment Orchestrator")
    parser.add_argument("--environment", type=str, required=True)
    parser.add_argument("--commit_sha", type=str)
    parser.add_argument("--pr_id", type=str)
    parser.add_argument("--source_branch", type=str)
    parser.add_argument("--compute_name", type=str)
    parser.add_argument("--experiment_folder", type=str, default="experiments")

    args = parser.parse_args()

    handle_experiment_gitops(
        environment=args.environment,
        commit_sha=args.commit_sha,
        pr_id=args.pr_id,
        source_branch=args.source_branch,
        compute_name=args.compute_name,
        experiment_folder=args.experiment_folder,
    )
