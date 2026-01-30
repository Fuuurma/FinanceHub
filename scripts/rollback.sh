#!/bin/bash

# Rollback script for FinanceHub deployment
# Reverts to previous Docker image

set -e

# Configuration
ENVIRONMENT="${1:-staging}"
CLUSTER=""

if [ "$ENVIRONMENT" = "staging" ]; then
    CLUSTER="finance-hub-staging"
elif [ "$ENVIRONMENT" = "production" ]; then
    CLUSTER="finance-hub-production"
else
    echo "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

echo "=== Rollback for ${ENVIRONMENT} ==="
echo ""

# Get current task definition
SERVICE_NAME="finance-hub-api"
CURRENT_TASK_DEF=$(aws ecs describe-services \
    --cluster "$CLUSTER" \
    --services "$SERVICE_NAME" \
    --query 'services[0].taskDefinition' \
    --output text)

echo "Current task definition: $CURRENT_TASK_DEF"

# Get previous task definition (assuming one before current)
PREVIOUS_TASK_DEF=$(aws ecs list-task-definitions \
    --family-prefix "$SERVICE_NAME" \
    --sort DESC \
    --max-items 2 \
    --query 'taskDefinitionArns[1]' \
    --output text)

echo "Previous task definition: $PREVIOUS_TASK_DEF"
echo ""

# Confirm rollback
read -p "Rollback to $PREVIOUS_TASK_DEF? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Rollback cancelled"
    exit 0
fi

# Perform rollback
echo "Rolling back..."
aws ecs update-service \
    --cluster "$CLUSTER" \
    --service "$SERVICE_NAME" \
    --task-definition "$PREVIOUS_TASK_DEF" \
    --force-new-deployment

echo "Rollback initiated"
echo "Monitor with: aws ecs describe-services --cluster $CLUSTER --services $SERVICE_NAME"
