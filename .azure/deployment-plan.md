# Azure Deployment Plan

Status: Approved - awaiting Azure context

## Scope
Prepare the existing InfraIQ AI orchestration service for Azure-hosted deployment with Microsoft Foundry, AKS, container images, Azure Managed Redis, and Azure Blob Storage.

## Application
- Service: `apps/services/ai-orchestration-service`
- Runtime: Python 3.12, FastAPI, Uvicorn
- Container: existing service Dockerfile
- AI contract: provider interface with proposal-only outputs and provenance metadata

## Proposed Architecture
- Azure Kubernetes Service (AKS): run the AI orchestration container
- Azure Container Registry (ACR): store and pull the service image
- Microsoft Foundry: model/provider backend behind the provider adapter
- Azure Managed Redis: cache and short-lived orchestration state
- Azure Blob Storage: evidence, source artifacts, and proposal artifacts
- Microsoft Entra Workload Identity: passwordless access from AKS to Azure services
- Azure Key Vault + Secrets Store CSI Driver: secrets and certificates where needed
- Log Analytics/Application Insights: application and container telemetry

## Day-0 Decisions Pending
- Azure subscription: pending because Azure CLI is not installed
- Resource group: pending
- Existing AKS cluster: pending
- Azure region: Central India
- Environment: Development
- AKS target: Existing cluster
- AKS Automatic versus Standard: existing cluster decision pending
- Public versus private AKS API server: existing cluster decision pending
- VNet and IP ranges: existing cluster decision pending
- Expected scale and cost target: pending
- Foundry project/model deployment to use: pending

## Security Rules
- No connection strings, keys, or tokens committed to the repository
- Use managed identity and Entra authentication where supported
- AI provider credentials remain inside infrastructure/provider adapters
- AI responses remain non-authoritative proposals
- Application/domain services remain responsible for validation and persistence

## Planned Repository Changes After Approval
- Azure settings and managed-identity configuration
- Provider adapter configuration for Microsoft Foundry
- Blob and Redis infrastructure adapters
- Kubernetes manifests/Helm values for deployment
- ACR build/deploy configuration
- Health/readiness probes and telemetry configuration
- Azure deployment documentation

## Validation and Deployment
- Run local service and contract tests
- Validate container build and Kubernetes manifests
- Run Azure pre-deployment validation
- Deployment is not authorized by this draft plan

## Current Blocker
Install Azure CLI and Azure Developer CLI, then provide or select the existing
subscription, resource group, AKS cluster, and Microsoft Foundry project/model.
