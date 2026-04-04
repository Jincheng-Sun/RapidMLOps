import argparse
import logging
from rapidmlops.azureml.utils import get_ml_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=str, required=False, help="Path to training data")
    args = parser.parse_args()

    # RapidMLOps utility is used seamlessly as an imported package!
    ml_client = get_ml_client("fraud_detection_logger")
    
    logger.info(f"Connected to Workspace: {ml_client.workspace_name}")
    logger.info("Starting fraud detection model training...")
    # Training logic goes here...

if __name__ == "__main__":
    main()
