import os
import argparse
import logging
from datetime import datetime

import mlflow
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    mean_squared_error,
    f1_score,
    precision_score,
    recall_score,
)

from azureml.fsspec import AzureMachineLearningFileSystem

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def train_linear_regression(
    training_data: str,
    test_data: str,
    registered_model_name: str,
    test_predictions: str,
    k_fold: int = 5,
    random_state: int = 42,
):
    training_data = pd.read_csv(training_data)
    reference_data = training_data.copy()
    test_data = pd.read_csv(test_data)
    X_train = training_data.drop("Class", axis=1)
    y_train = training_data["Class"]
    if "Class" in test_data.columns:
        y_test = test_data["Class"]
        X_test = test_data.drop("Class", axis=1)
    else:
        X_test = test_data
        y_test = None
    # Cross validation
    kfold = StratifiedKFold(n_splits=k_fold, shuffle=True, random_state=random_state)

    best_model = None
    best_score = -float("inf")

    for fold, (train_index, val_index) in enumerate(kfold.split(X_train, y_train)):
        X_train_fold, X_val_fold = X_train.iloc[train_index], X_train.iloc[val_index]
        y_train_fold, y_val_fold = y_train.iloc[train_index], y_train.iloc[val_index]
        model = LogisticRegression(
            penalty="l2",
            solver="liblinear",
            C=1.0,
            max_iter=1000,
            random_state=random_state,
        )
        with mlflow.start_run(run_name=f"fold_{fold}") as run:
            model.fit(X_train_fold, y_train_fold)
            y_pred = model.predict(X_val_fold)
            y_pred_proba = model.predict_proba(X_val_fold)[:, 1]

            accuracy = accuracy_score(y_val_fold, y_pred)
            roc_auc = roc_auc_score(y_val_fold, y_pred_proba)
            f1 = f1_score(y_val_fold, y_pred)
            precision = precision_score(y_val_fold, y_pred)
            recall = recall_score(y_val_fold, y_pred)

            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("roc_auc", roc_auc)
            mlflow.log_metric("f1", f1)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("fold", fold)

            if roc_auc > best_score:
                best_model = model
                best_auc = roc_auc
                best_f1 = f1
                best_precision = precision
                best_recall = recall
                best_accuracy = accuracy
                best_run_id = run.info.run_id

    logger.info(f"Best model found with ROC AUC: {best_auc}")
    logger.info(f"Best model found with F1: {best_f1}")
    logger.info(f"Best model found with Precision: {best_precision}")
    logger.info(f"Best model found with Recall: {best_recall}")
    logger.info(f"Best model found with Accuracy: {best_accuracy}")
    logger.info(f"Best model found with Run ID: {best_run_id}")

    # Log the best model
    with mlflow.start_run(run_name=f"best_model") as run:
        mlflow.sklearn.log_model(
            sk_model=best_model,
            artifact_path="model",
            registered_model_name=registered_model_name,
        )
        mlflow.log_metric("auc", best_auc)
        mlflow.log_metric("f1", best_f1)
        mlflow.log_metric("precision", best_precision)
        mlflow.log_metric("recall", best_recall)
        mlflow.log_metric("accuracy", best_accuracy)
        mlflow.log_metric("run_id", best_run_id)
        mlflow.log_params(
            {
                "k_fold": k_fold,
                "penalty": "l2",
                "solver": "liblinear",
                "C": 1.0,
                "max_iter": 1000,
                "random_state": random_state,
            }
        )

    # Save reference data
    reference_data["prediction"] = best_model.predict(
        reference_data.drop("Class", axis=1)
    )
    reference_data["probability"] = best_model.predict_proba(
        reference_data.drop("Class", axis=1)
    )[:, 1]
    reference_data_path = (
        f"reference_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    reference_data.to_csv(reference_data_path, index=False)
    subscription_id = os.getenv("AZUREML_ARM_SUBSCRIPTION")
    resource_group = os.getenv("AZUREML_ARM_RESOURCEGROUP")
    workspace_name = os.getenv("AZUREML_ARM_WORKSPACE_NAME")
    datastore_name = os.getenv("DATASTORE_NAME", "workspaceblobstore")
    upload_path = (
        f"azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/"
        f"workspaces/{workspace_name}/datastores/{datastore_name}/paths/"
    )
    fs = AzureMachineLearningFileSystem(upload_path)
    fs.upload(
        lpath=reference_data_path,
        rpath="/reference_data",
        overwrite="MERGE_WITH_OVERWRITE",
        recursive=False,
    )

    # Save test predictions
    test_data["prediction"] = best_model.predict(X_test)
    test_data["probability"] = best_model.predict_proba(X_test)[:, 1]
    test_data.to_csv(f"{test_predictions}/test_predictions.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--training_data", type=str, help="Training data folder")
    parser.add_argument("--test_data", type=str, help="Test data folder")
    parser.add_argument(
        "--registered_model_name", type=str, help="Registered model name"
    )
    parser.add_argument("--test_predictions", type=str, help="Test predictions folder")
    args = parser.parse_args()
    train_linear_regression(
        args.training_data,
        args.test_data,
        args.registered_model_name,
        args.test_predictions,
    )
