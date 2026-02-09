#!/usr/bin/env bash
set -euo pipefail
# ═══════════════════════════════════════════════════════════════════════════════
# Newton Supercomputer — AWS Deployment Script
# Uses AWS SAM CLI to build and deploy to Lambda + API Gateway (free tier)
#
# Prerequisites:
#   brew install aws-sam-cli   (or pip install aws-sam-cli)
#   aws configure              (set up your AWS credentials)
#   docker                     (for container builds)
#
# Usage:
#   ./deploy.sh                # Deploy to prod (default)
#   ./deploy.sh staging        # Deploy to staging
#   ./deploy.sh dev            # Deploy to dev
# ═══════════════════════════════════════════════════════════════════════════════

STAGE="${1:-prod}"
STACK_NAME="newton-api-${STAGE}"
REGION="${AWS_REGION:-us-east-1}"

echo "═══════════════════════════════════════════"
echo "  NEWTON SUPERCOMPUTER — AWS Deploy"
echo "  Stage:  ${STAGE}"
echo "  Stack:  ${STACK_NAME}"
echo "  Region: ${REGION}"
echo "═══════════════════════════════════════════"

# Check prerequisites
for cmd in sam docker aws; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "ERROR: '$cmd' is required but not installed."
        exit 1
    fi
done

# Build the container image
echo ""
echo "→ Building Lambda container..."
sam build --use-container

# Deploy (guided on first run, then uses samconfig.toml)
echo ""
echo "→ Deploying to AWS..."
sam deploy \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --resolve-s3 \
    --resolve-image-repos \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        "StageName=${STAGE}" \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

# Print the API URL
echo ""
echo "═══════════════════════════════════════════"
echo "  Deployment complete!"
echo ""
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text 2>/dev/null && true
echo "═══════════════════════════════════════════"
