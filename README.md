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
