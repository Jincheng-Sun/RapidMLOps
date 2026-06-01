import argparse
import json

import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


def classification_evaluation(
    test_predictions: str,
    result_save_path: str,
    registered_model_name: str,
    test_labels: str = None,
):
    test_predictions = pd.read_csv(test_predictions)
    if test_labels:
        test_labels = pd.read_csv(test_labels)

    accuracy = accuracy_score(test_labels, test_predictions)
    precision = precision_score(test_labels, test_predictions)
    recall = recall_score(test_labels, test_predictions)
    f1 = f1_score(test_labels, test_predictions)
    confusion_matrix = confusion_matrix(test_labels, test_predictions)
    classification_report = classification_report(test_labels, test_predictions)

    result = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": confusion_matrix,
        "classification_report": classification_report,
    }

    with open(f"{result_save_path}/{registered_model_name}_metrics.json", "w") as f:
        json.dump(result, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test_predictions", type=str, required=True)
    parser.add_argument("--test_labels", type=str, required=False)
    parser.add_argument("--result_save_path", type=str, required=True)
    args = parser.parse_args()
    classification_evaluation(
        args.test_predictions, args.result_save_path, args.test_labels
    )
