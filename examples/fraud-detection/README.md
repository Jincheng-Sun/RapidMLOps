# Fraud Detection Model (Example Project)

This directory serves as a **reference implementation** demonstrating how a Data Scientist or ML Engineer should structure their own independent project repository and consume the `RapidMLOps` platform tools.

## How it works

As a user, you should NOT write code inside the `RapidMLOps` repository. Instead, treat this `fraud-detection` folder as if it is its own Git repository in Azure DevOps.

1. **Python Dependencies**: Notice that `requirements.txt` installs `rapidmlops`. The core MLOps functions are imported as library calls (e.g., `from rapidmlops.azureml.utils import get_ml_client`).
2. **CI/CD Integration**: Open `azure-pipelines.yaml` to see how you can dynamically consume CI/CD templates from the MLOps Platform repository without copy-pasting them!
3. **Your Source Code**: Your actual model training code goes securely into `src/`.
