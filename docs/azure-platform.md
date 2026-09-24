# Azure platform track

The Azure DevOps pipeline is [.azuredevops/pipelines/azure-platform.yml](../.azuredevops/pipelines/azure-platform.yml).
It validates the two implemented Python services, compiles their application
packages, and builds an image only when the corresponding Dockerfile exists.
The frontend is included in the same conditional container-build step.

## Validation

Run locally from the repository root:

```bash
python -m compileall -q apps/services/ai-orchestration-service/app apps/services/risk-service/app
(cd apps/services/ai-orchestration-service && PYTHONPATH=.:../../.. python -m pytest -q tests)
(cd apps/services/risk-service && PYTHONPATH=. python -m pytest -q tests)
```

The hosted pipeline installs each service's `requirements.txt` before running
these checks, including the geospatial service tests and compilation.

## Deployment preparation

Deployment stages are deliberately disabled by default. To enable them, supply
an Azure Resource Manager service connection and the names of an **existing**
ACR, AKS resource group, and AKS cluster as pipeline parameters. The service
connection supplies authentication; no subscription ID, token, registry
password, or application secret is stored in this repository.

The ACR stage builds the AI orchestration image with `az acr build`. The AKS
stage obtains cluster credentials and invokes
`deploy/kubernetes/deploy-aks.sh`, which substitutes runtime values into the
manifest template. The template currently deploys only the AI orchestration
service and assumes its `/health` endpoint is available. Review probes,
resource limits, identity, network policy, ingress, and secret references for
the target cluster before enabling deployment.

This repository does not contain enough Azure context to claim a deploy is
executable: subscription, resource group, cluster, registry, permissions, and
provider configuration remain deployment-time decisions.

## Azure Blob Storage and AI configuration

The repository supports configuration through environment variables. Do not
commit connection strings, account keys, API keys, or endpoint credentials.
Use a local `.env` file that is ignored by Git for development, and Azure Key
Vault or secret variables in Azure DevOps for hosted environments.

### Blob Storage

The available Blob Storage values map as follows:

| Azure value | Application setting | Required use |
| --- | --- | --- |
| Storage account connection string | `BLOB_CONNECTION_STRING` | Preferred credential for the current Blob adapter |
| Blob container name | `BLOB_CONTAINER` | Container used by the service |
| Storage account name | `AZURE_STORAGE_ACCOUNT_NAME` | Deployment metadata or identity-based clients |
| Storage account key | `AZURE_STORAGE_ACCOUNT_KEY` | Secret; do not commit or expose in logs |
| Endpoint suffix | `AZURE_STORAGE_ENDPOINT_SUFFIX` | Usually `core.windows.net` |

The current service configuration directly consumes
`BLOB_CONNECTION_STRING` and `BLOB_CONTAINER`. The account name, account key,
and endpoint suffix are not currently required by the existing
connection-string adapter. If identity-based authentication is introduced,
prefer managed identity and the account name over distributing account keys.

Example local configuration with placeholders only:

```dotenv
BLOB_CONNECTION_STRING=<store-in-a-local-secret-file>
BLOB_CONTAINER=infraiq
AZURE_STORAGE_ACCOUNT_NAME=<storage-account-name>
AZURE_STORAGE_ACCOUNT_KEY=<storage-account-key>
AZURE_STORAGE_ENDPOINT_SUFFIX=core.windows.net
```

### Microsoft Foundry and Azure OpenAI

Keep the Foundry project endpoint and Azure OpenAI deployment endpoint
distinct. They can represent different Azure resources and have different
client/API-version requirements.

| Azure value | Application setting |
| --- | --- |
| Microsoft Foundry project endpoint | `FOUNDRY_ENDPOINT` |
| Microsoft Foundry API key, if key authentication is enabled | `FOUNDRY_API_KEY` |
| Azure OpenAI resource endpoint | `AZURE_OPENAI_ENDPOINT` |
| Azure OpenAI API key | `AZURE_OPENAI_API_KEY` |
| Azure OpenAI API version | `AZURE_OPENAI_API_VERSION` |
| Azure OpenAI model deployment name | `AZURE_OPENAI_DEPLOYMENT` |

Example:

```dotenv
FOUNDRY_ENDPOINT=<foundry-project-endpoint>
FOUNDRY_API_KEY=<stored-as-a-secret>
AZURE_OPENAI_ENDPOINT=<azure-openai-resource-endpoint>
AZURE_OPENAI_API_KEY=<stored-as-a-secret>
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
MODEL_PROVIDER=microsoft-foundry
```

The exact provider setting depends on the adapter being used. A Foundry
project endpoint must not be assumed to be interchangeable with an Azure
OpenAI resource endpoint. Confirm the selected model deployment, API version,
authentication method, region, and network access before enabling the provider.

### Secret handling rules

- Never paste the actual connection string, account key, API key, or token into
  source files, issues, pull requests, chat, or documentation.
- Store local secrets in an ignored `.env` file or a developer secret store.
- Store Azure DevOps secrets as secret variable-group or variable values.
- Prefer workload identity or managed identity for Azure-hosted services.
- Rotate any credential exposed outside its intended secret store.
- Redact credentials from exception messages, request logs, telemetry, and
  support bundles.
- Grant Blob access at the narrowest required scope; prefer identity or a
  container-scoped SAS policy over an account key where practical.
