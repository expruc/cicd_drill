# CI/CD Pipeline with Docker + Lambda Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CI/CD pipeline that builds a Python app into a Docker image, pushes to ECR, and deploys to Lambda — triggered by git tags.

**Architecture:** Terraform provisions ECR + Lambda + IAM. GitHub Actions (triggered by `v*` tags) builds the image, pushes to ECR, and updates the Lambda function.

**Tech Stack:** Python 3.12, Docker, Terraform, AWS ECR/Lambda/IAM, GitHub Actions (OIDC auth)

---

### Task 1: Application Code

**Files:**
- Create: `hello_world.py`
- Create: `Dockerfile`
- Create: `.gitignore`

- [ ] **Step 1: Create hello_world.py**

```python
def lambda_handler(event, context):
    print("Hello from CI/CD!")
    return {
        "statusCode": 200,
        "body": "Hello from CI/CD!"
    }
```

- [ ] **Step 2: Create Dockerfile**

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

COPY hello_world.py .

CMD ["hello_world.lambda_handler"]
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
*.pyo
.env
.terraform/
terraform.tfstate
terraform.tfstate.backup
*.tfvars
```

- [ ] **Step 4: Commit**

```bash
git add hello_world.py Dockerfile .gitignore
git commit -m "feat: add hello_world Lambda app and Dockerfile"
```

---

### Task 2: Terraform Infrastructure

**Files:**
- Create: `terraform/main.tf`
- Create: `terraform/variables.tf`

- [ ] **Step 1: Create terraform/variables.tf**

```hcl
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name used for resource naming"
  type        = string
  default     = "hello-world-cicd"
}
```

- [ ] **Step 2: Create terraform/main.tf**

```hcl
provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

# ECR repository to store Docker images
resource "aws_ecr_repository" "app" {
  name         = var.app_name
  force_delete = true

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle_policy {
    policy = jsonencode({
      rules = [{
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = { type = "expire" }
      }]
    })
  }
}

# IAM role for Lambda execution
resource "aws_iam_role" "lambda" {
  name = "${var.app_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function (initial placeholder — image will be updated by CI/CD)
resource "aws_lambda_function" "app" {
  function_name = var.app_name
  role          = aws_iam_role.lambda.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.app.repository_url}:latest"
  timeout       = 30
  memory_size   = 128

  environment {
    variables = {
      VERSION = "0.0.0"
    }
  }
}

# Outputs for CI/CD
output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "lambda_function_name" {
  value = aws_lambda_function.app.function_name
}
```

- [ ] **Step 3: Commit**

```bash
git add terraform/
git commit -m "feat: add Terraform configs for ECR, Lambda, IAM"
```

---

### Task 3: GitHub Actions CI/CD Pipeline

**Files:**
- Create: `.github/workflows/deploy.yml`

- [ ] **Step 1: Create .github/workflows/deploy.yml**

```yaml
name: Deploy to Lambda

on:
  push:
    tags:
      - 'v*'

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: hello-world-cicd
  LAMBDA_FUNCTION_NAME: hello-world-cicd

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Extract version from git tag
        id: get-version
        run: echo "VERSION=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT

      - name: Build, tag, and push image to Amazon ECR
        id: build-image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ steps.get-version.outputs.VERSION }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
          echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

      - name: Update Lambda function
        run: |
          aws lambda update-function-code \
            --function-name ${{ env.LAMBDA_FUNCTION_NAME }} \
            --image-uri ${{ steps.build-image.outputs.image }}
```

**Versioning scheme:**
- Git tags use SemVer: `v<major>.<minor>.<patch>` (e.g., `v1.0.0`, `v1.2.3`, `v2.0.0`)
- The `get-version` step strips the `v` prefix to use as the Docker image tag
- Images are tagged with both the version and `latest`
- The Lambda function is updated with the specific versioned image URI
- Major bump (v2.0.0) = breaking change; Minor (v1.1.0) = new feature; Patch (v1.0.1) = bug fix

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "feat: add GitHub Actions CI/CD pipeline"
```

---

### Task 4: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# CI/CD Drill

Demo project: automated CI/CD pipeline for a Python Lambda function using Docker, ECR, and GitHub Actions.

## How It Works

1. **Infrastructure** (one-time): `terraform apply` provisions ECR repo, Lambda function, and IAM roles.
2. **Release**: create a git tag `v1.0.0` and push.
3. **Pipeline**: GitHub Actions builds the Docker image, pushes to ECR, and updates Lambda.

## Versioning

Git tags follow SemVer (`v<major>.<minor>.<patch>`):
- `v1.0.0` — initial release
- `v1.0.1` — patch fix
- `v1.1.0` — new feature
- `v2.0.0` — breaking change

Docker images are tagged with the version number (e.g., `1.0.0`) and `latest`.

## One-Time Setup

1. Create the infrastructure:
   ```bash
   cd terraform
   terraform init
   terraform apply
   ```
2. Create an OIDC identity provider in AWS for GitHub Actions:
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`
3. Create an IAM role for GitHub Actions with trust policy allowing the repo to assume it.
4. Add the role ARN as a GitHub secret: `AWS_ROLE_ARN`.
5. Push a tag to trigger the pipeline:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

## Project Structure

```
├── hello_world.py          # Lambda handler
├── Dockerfile              # Container image
├── terraform/              # Infrastructure as Code
│   ├── main.tf
│   └── variables.tf
└── .github/workflows/      # CI/CD pipeline
    └── deploy.yml
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```

---

### Task 5: Push to GitHub

- [ ] **Step 1: Push all commits to remote**

```bash
git push origin main
```
