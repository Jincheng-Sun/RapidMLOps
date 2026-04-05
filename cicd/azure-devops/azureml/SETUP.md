# Azure DevOps Pipeline Infrastructure & Setup Guide

This document outlines the manual steps necessary to connect your Azure DevOps CI/CD pipelines to your Azure Machine Learning (AzureML) workspaces securely.

---

## 1. Pipeline Agent Matrix (Networking)

Before running a pipeline, you must determine what compute agent has network access to your AzureML Workspace.

| AzureML Workspace Networking | Required Pipeline Agent Pool | Setup Required |
| :--- | :--- | :--- |
| **Publicly Accessible** | Microsoft-Hosted Agents (e.g., `ubuntu-latest`) | **None**. The free-tier agents will work out-of-the-box. |
| **Private Link / VNet (Enterprise)** | Self-Hosted Agents | **Manual Setup**. You must provision a VM inside the VNet that peers with the AzureML workspace, install the Azure DevOps agent software on it, and register it to your Azure DevOps Agent Pools. |

*In `azure-pipelines.yaml`, you configure this via the `agentPool` variable.*

---

## 2. Identity and Permissions (Authentication)

Pipelines start as anonymous computers. To authorize them to interact with AzureML, you must create a Service Principal and link it to Azure DevOps via a **Service Connection**.

### Step 2.1: Create the Identity (Azure Portal)
1. Navigate to **Microsoft Entra ID (Azure AD)** -> **App Registrations**.
2. Click **New Registration**, name it (e.g., `sp-mlops-dev-pipeline`).
3. Note the **Application (client) ID** and the **Directory (tenant) ID**.

### Step 2.2: Assign Permissions (Azure Portal)
1. Navigate to the **Resource Group** containing your AzureML Workspace.
2. Go to **Access Control (IAM)** -> **Add role assignment**.
3. Select the **AzureML Data Scientist** (or `Contributor`) role.
4. Assign access to the Service Principal you created in Step 2.1.

### Step 2.3: Link to Azure DevOps (Azure DevOps)
Azure DevOps provides two ways to leverage this Service Principal. **Workload Identity Federation (OIDC)** is highly recommended as it eliminates the need to manage secret passwords.

#### Method A: Workload Identity Federation (Recommended - Zero Secrets)
1. Go to Azure DevOps -> **Project Settings** -> **Service connections**.
2. Create a new **Azure Resource Manager** connection.
3. Select **Workload Identity federation (manual)**.
4. Fill in your Subscription ID, Tenant ID, and Service Principal Client ID.
5. Azure DevOps will output an **Issuer URL** and **Subject Identifier**.
6. Go back to your App Registration in the Azure Portal -> **Certificates & secrets** -> **Federated credentials**. Add a credential using the Issuer and Subject provided by Azure DevOps.

#### Method B: Legacy Client Secret
1. In the Azure Portal, go to your App Registration -> **Certificates & secrets** -> Generate a New Client Secret. Save the string.
2. In Azure DevOps -> **Pipelines** -> **Library** -> **Variable groups**.
3. Create a variable group and add three variables (store the secret as a hidden secure value):
   - `AZURE_CLIENT_ID`
   - `AZURE_TENANT_ID`
   - `AZURE_CLIENT_SECRET`
*(Note: Our pipeline templates are wired to automatically pick up these environment variables!).*

---

## 3. Configuring Your Pipeline Variables

Once the networking and identities are solved, the user simply maps these values into their consuming `azure-pipelines.yaml`.

```yaml
variables:
  # The Identity Configuration
  - name: SUBSCRIPTION_ID
    value: '1234abcd-1234-5678...'
  - name: RESOURCE_GROUP
    value: 'rg-mlops-dev'
  - name: WORKSPACE_NAME
    value: 'mlw-dev-01'
    
  # The Networking Configuration
  - name: agentPool
    value: 'ubuntu-latest' # Or 'My-Private-VNet-Pool' if using private links
```

---

## 4. Securing Environments (Preventing Jailbreaks)

If a developer arbitrarily modifies their personal pipeline `.yaml` to point to the `org.subscription.prod` Service Connection, they could maliciously execute code against Production from their feature branch. 

To prevent this, you **MUST** apply Azure DevOps Zero-Trust security rules on both your **Service Connections** and **Agent Pools**.

### Step 4.1: Branch Control
You must lock down production configurations so they physically reject requests originating from non-approved branches:
1. In Azure DevOps, go to **Project Settings** -> **Service connections** (or **Agent pools**).
2. Select your Production Service Connection -> click the **More options (3 dots)** menu -> **Approvals and checks**.
3. Add a **Branch control** check.
4. Set the allowed branches to `refs/heads/main` or `refs/tags/*`. 
*Result: If a pipeline on `feature/evil` attempts to use the Prod Service Connection, ADO instantly terminates the pipeline before it runs.*

### Step 4.2: Required Templates
You must lock the endpoint so it is only allowed to execute if it is enveloped by your official platform templates:
1. Inside **Approvals and checks**, add a **Required template** check.
2. Specify the repository `RapidMLOps` and the exact template path `cicd/azure-devops/azureml/templates/e2e-mlops-pipeline-template.yaml`.
*Result: If a user writes an arbitrary pipeline bypassing your unit tests and stages, Azure DevOps will block their access to the Service Connection or Agent Pool.*

### Step 4.3: Agent Pool Isolation (Cross-Team Security)
If `Team A` and `Team B` share the same local agent pipeline pool (e.g. `shared-prod-agents`), the scripts running on the VM could potentially intercept environment variables or workspaces. 
**Best Practice**: Create dedicated Agent Pools per team per environment (e.g., `fraud-team-prod-pool` and `recommendation-team-prod-pool`). Use Workload Identity Federation (OIDC) bound strictly to that specific pool so the compute engine can never impersonate a different deployment!
