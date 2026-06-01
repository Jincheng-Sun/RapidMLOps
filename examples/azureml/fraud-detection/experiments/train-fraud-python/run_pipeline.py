import os

from azure.ai.ml import MLClient, Input, Output, load_component, command
from azure.ai.ml.constants import AssetTypes
from azure.identity import AzureCliCredential
from azure.ai.ml.dsl import pipeline


def main(
    experiment_name: str,
    compute_name: str,
    registered_model_name: str,
    commit_sha: str,
    pr_id: str,
    source_branch: str,
    subscription_id: str = None,
    resource_group: str = None,
    workspace_name: str = None,
):
    credential = AzureCliCredential()
    if subscription_id:
        subscription_id = os.getenv("SUBSCRIPTION_ID", subscription_id)
    if resource_group:
        resource_group = os.getenv("RESOURCE_GROUP", resource_group)
    if workspace_name:
        workspace_name = os.getenv("AZUREML_WORKSPACE_NAME", workspace_name)
    ml_client = MLClient(credential, subscription_id, resource_group, workspace_name)

    print(f"Executing programmatic Py-Pipeline in {experiment_name}...")

    # Load or construct job definition
    # Approach 1: Load from the workspace registry
    e2e_pipeline_comp = ml_client.components.get(
        name="end-to-end-pipeline", label="latest"
    )

    # Approach 2: Load from a local YAML file
    # e2e_pipeline_comp = load_component(source="./optional_pipeline.yaml")
    # Approach 3: Construct with AzureML SDK v2
    # prep_raw_data = command(
    #     name="prep-raw-data",
    #     display_name="Prep Raw Data",
    #     code="<path to code>",
    #     command="python <path_to_script>",
    #     environment="<environment name>",
    #     inputs=[
    #         Input(name="raw_data", type=AssetTypes.URI_FOLDER, optional=False),
    #     ],
    #     outputs=[
    #         Output(name="prepared_data", type=AssetTypes.URI_FOLDER, optional=False),
    #     ],
    #     )
    # train_linear_regression = command(
    #     name="train-linear-regression",
    #     display_name="Train Linear Regression",
    #     code="<path to code>",
    #     command="python <path_to_script>",
    #     environment="<environment name>",
    #     inputs=[
    #         Input(name="training_data", type=AssetTypes.URI_FOLDER, optional=False),
    #         Input(name="test_data", type=AssetTypes.URI_FOLDER, optional=False),
    #         Input(name="test_labels", type=AssetTypes.URI_FOLDER, optional=False),
    #     ],
    #     outputs=[
    #         Output(name="test_predictions", type=AssetTypes.URI_FOLDER, optional=False),
    #     ],
    #     )
    # @pipeline(
    #     default_compute=compute_name, default_datastore="azureml:workspaceblobstore"
    # )
    # def e2e_pipeline_comp(
    #     training_data, test_data, test_labels, registered_model_name
    # ):
    #     prep_train_data = prep_raw_data(raw_data=training_data)
    #     prep_test_data = prep_raw_data(raw_data=test_data)
    #     train_linear_regression = train_linear_regression(
    #         training_data=prep_train_data.outputs.prepared_data,
    #         test_data=prep_test_data.outputs.prepared_data,
    #         registered_model_name=registered_model_name,
    #     )

    pipeline_job = e2e_pipeline_comp(
        training_data=Input(
            type=AssetTypes.URI_FOLDER, path="azureml:fraud-train-data@latest"
        ),
        test_data=Input(
            type=AssetTypes.URI_FOLDER, path="azureml:fraud-test-data@latest"
        ),
        test_labels=Input(
            type=AssetTypes.URI_FOLDER, path="azureml:fraud-test-labels@latest"
        ),
        registered_model_name=registered_model_name,
    )

    pipeline_job.settings.default_compute = compute_name

    pipeline_job.experiment_name = experiment_name

    tags = {}
    if commit_sha:
        tags["git_commit_sha"] = commit_sha
    if pr_id:
        tags["pr_id"] = pr_id
    if source_branch:
        tags["source_branch"] = source_branch
    if tags:
        pipeline_job.tags = tags

    # 5. Fire off the job
    print(f"Submitting job to {pipeline_job.experiment_name}...")
    created_job = ml_client.jobs.create_or_update(pipeline_job)
    print(f"Job successfully submitted! Studio URL: {created_job.studio_url}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--environment", type=str, required=True, help="Target Environment"
    )
    parser.add_argument(
        "--experiment_name", type=str, required=True, help="Dictated Experiment Name"
    )
    parser.add_argument(
        "--compute_name", type=str, required=True, help="Dictated Compute Cluster"
    )
    parser.add_argument(
        "--registered_model_name", type=str, required=True, help="Dictated Model Name"
    )
    parser.add_argument("--commit_sha", type=str, required=False, help="Git Lineage")
    parser.add_argument("--pr_id", type=str, required=False)
    parser.add_argument("--source_branch", type=str, required=False)
    args = parser.parse_args()
    main(
        experiment_name=args.experiment_name,
        compute_name=args.compute_name,
        registered_model_name=args.registered_model_name,
        commit_sha=args.commit_sha,
        pr_id=args.pr_id,
        source_branch=args.source_branch,
    )
