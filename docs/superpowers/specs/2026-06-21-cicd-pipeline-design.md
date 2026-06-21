# CI/CD Pipeline with Docker + Lambda on AWS

## Overview

Automated CI/CD pipeline for a Python application (`hello_world.py`) that builds a Docker image, pushes it to Amazon ECR, and deploys it to AWS Lambda. Triggered by git tags following SemVer. Infrastructure provisioned via Terraform.

## Architecture

```
Git Tag (v1.0.0)
     │
     ▼
GitHub Actions ──► Build Docker Image ──► Push to ECR ──► Update Lambda
     │
     ▼
Terraform: ECR repo, Lambda function, IAM roles
```

## Components

### 1. Application Code
- `hello_world.py` — prints "Hello from CI/CD!" to stdout
- `Dockerfile` — uses `python:3.12-slim` base, copies app, sets ENTRYPOINT

### 2. Terraform (infrastructure provisioning)
- **Provider:** AWS (region configurable via variables)
- **Resources:**
  - ECR repository (with lifecycle policy to retain last 10 images)
  - IAM role for Lambda execution (with basic execution + ECR pull permissions)
  - Lambda function (container image sourced from ECR)
- **State:** stored locally (`terraform.tfstate`)

### 3. GitHub Actions (CI/CD pipeline)
- **Trigger:** push of tags matching `v*` (e.g., `v1.0.0`, `v2.1.3`)
- **Steps:**
  1. Checkout code
  2. Configure AWS credentials via OpenID Connect (OIDC)
  3. Extract version from tag (strip `v` prefix)
  4. Log in to ECR
  5. Build Docker image with version and `latest` tags
  6. Push image to ECR
  7. Update Lambda function to use the new image

### 4. Versioning Strategy
- Git tags follow SemVer: `v<major>.<minor>.<patch>`
  - Major: breaking changes
  - Minor: new features (backward-compatible)
  - Patch: bug fixes
- Docker images tagged with: `<version>` (e.g., `1.0.0`) and `latest`
- Lambda function pointed at the specific version tag

## Deployment Target

- **ECR:** stores container images
- **Lambda:** runs the containerized application
- Lambda function is updated on each release to use the new image URI

## File Structure

```
cicd_drill/
├── hello_world.py
├── Dockerfile
├── .gitignore
├── README.md
├── terraform/
│   ├── main.tf
│   └── variables.tf
└── .github/
    └── workflows/
        └── deploy.yml
```

## Security

- GitHub Actions authenticates to AWS via OIDC (no long-lived keys)
- Lambda execution role follows least-privilege (ECR pull + CloudWatch logs)
- ECR lifecycle policy prevents unbounded image accumulation

## One-Time Setup

1. `cd terraform && terraform init && terraform apply`
2. Configure GitHub OIDC provider in AWS (IAM identity provider)
3. Push a git tag to trigger the pipeline

## Pipeline Flow (Detailed)

```
User: git tag v1.0.0 && git push origin v1.0.0

GitHub Actions:
  1. on: push tags matching 'v*'
  2. Configure AWS credentials (OIDC)
  3. Set IMAGE_TAG = 1.0.0 (strip v)
  4. Build: docker build -t $ECR_REPO:$IMAGE_TAG -t $ECR_REPO:latest .
  5. Push: docker push $ECR_REPO:$IMAGE_TAG && docker push $ECR_REPO:latest
  6. Deploy: aws lambda update-function-code --function-name hello-world \
       --image-uri $ECR_REPO:$IMAGE_TAG
```
