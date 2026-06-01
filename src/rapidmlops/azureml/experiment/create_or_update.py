from azure.ai.ml import MLClient, load_job

from rapidmlops.core.utils import get_logger
from rapidmlops.core.models import GitOpsLineageTags
from rapidmlops.azureml.utils import get_ml_client

logger = get_logger(__name__)


def create_or_update_experiment(
    experiment_config_path: str,
    experiment_name: str = None,
    job_name: str = None,
    registered_model_name: str = None,
    commit_sha: str = None,
    pr_id: str = None,
    source_branch: str = None,
    environment: str = None,
    ml_client: MLClient = None,
):
    """Creates or updates an experiment (Job) using a YAML definition.

    Args:
        experiment_config_path (str): The configuration path.
        experiment_name (str, optional): The overridden experiment name.
        registered_model_name (str, optional): The standardized model name to inject.
        commit_sha (str, optional): Git Commit SHA.
        pr_id (str, optional): Pull Request ID.
        source_branch (str, optional): Source branch.
        ml_client (MLClient, optional): The MLClient instance.
    """

    if not ml_client:
        ml_client = get_ml_client(logger_name=__name__)

    overrides = []
    if experiment_name:
        overrides.append({"experiment_name": experiment_name})
    if job_name:
        overrides.append({"name": job_name})
        overrides.append({"display_name": job_name.replace("-", " ").title()})
    params_override = overrides if overrides else None

    logger.info(
        f"[INFO] Loading Experiment (Job) config from: {experiment_config_path}"
        f"[INFO] Override parameters: {params_override}"
        if params_override
        else ""
    )
    job = load_job(source=experiment_config_path, params_override=params_override)

    # Attempt to inject model naming constraint if the user defined the placeholder inside inputs
    if registered_model_name:
        try:
            if hasattr(job, "inputs"):
                # Depending on the SDK v2 node structure, assignment works transparently
                job.inputs["registered_model_name"] = registered_model_name
                logger.info(
                    f"[INFO] YAML Job 'registered_model_name' input overridden natively."
                )
        except Exception as e:
            logger.warning(
                f"Could not inject registered_model_name into YAML inputs. Ensure 'registered_model_name' exists in inputs block. Error: {e}"
            )

    tags = GitOpsLineageTags(
        git_commit_sha=commit_sha,
        pr_id=pr_id,
        source_branch=source_branch,
        environment=environment,
    )
    job.tags.update(tags.to_dict())

    created_job = ml_client.jobs.create_or_update(job)
    logger.info(
        f"[INFO] Experiment Job '{created_job.name}' submitted successfully in {ml_client.workspace_name}"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create or update an AzureML Job")
    parser.add_argument("--experiment_config_path", type=str, required=True)
    parser.add_argument("--experiment_name", type=str)
    parser.add_argument("--registered_model_name", type=str)
    parser.add_argument("--commit_sha", type=str)
    parser.add_argument("--pr_id", type=str)
    parser.add_argument("--source_branch", type=str)

    args = parser.parse_args()
    create_or_update_experiment(
        experiment_config_path=args.experiment_config_path,
        experiment_name=args.experiment_name,
        registered_model_name=args.registered_model_name,
        commit_sha=args.commit_sha,
        pr_id=args.pr_id,
        source_branch=args.source_branch,
    )
