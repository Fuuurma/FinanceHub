#!/bin/bash
#############################################
# FinanceHub - Cost Monitoring Script
# Author: KAREN (DevOps Engineer)
# Date: 2026-01-30
# Description: Monitor AWS costs and resource usage
#############################################

set -euo pipefail

# Configuration
COST_THRESHOLD_WARNING=${COST_THRESHOLD_WARNING:-100}  # USD
COST_THRESHOLD_CRITICAL=${COST_THRESHOLD_CRITICAL:-200}  # USD
REGION="${AWS_REGION:-us-east-1}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

#############################################
# Check AWS CLI
#############################################
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        error "AWS CLI not found"
        error "Install with: brew install awscli (macOS)"
        return 1
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        error "AWS credentials not configured"
        error "Run: aws configure"
        return 1
    fi

    log "✅ AWS CLI configured"
}

#############################################
# Get Current Month Cost
#############################################
get_current_month_cost() {
    log "💰 Calculating current month costs..."

    # Get cost for current month
    local start_date=$(date -u +"%Y-%m-01")
    local end_date=$(date -u +"%Y-%m-%d")

    local cost=$(aws ce get-cost-and-usage \
        --time-period Start="${start_date}",End="${end_date}" \
        --granularity MONTHLY \
        --metrics BlendedCost \
        --group-by Type=DIMENSION,Key=SERVICE \
        --query 'ResultsByTime[0].Groups[*].Metrics.BlendedCost.Amount' \
        --output text 2>/dev/null | awk '{sum+=$1} END {printf "%.2f", sum}')

    if [[ -n "${cost}" ]]; then
        echo "${cost}"
    else
        echo "0.00"
    fi
}

#############################################
# Get Cost by Service
#############################################
get_cost_by_service() {
    log "📊 Breaking down costs by service..."

    local start_date=$(date -u +"%Y-%m-01")
    local end_date=$(date -u +"%Y-%m-%d")

    aws ce get-cost-and-usage \
        --time-period Start="${start_date}",End="${end_date}" \
        --granularity MONTHLY \
        --metrics BlendedCost \
        --group-by Type=DIMENSION,Key=SERVICE \
        --query 'ResultsByTime[0].Groups[].{Service: Keys[0], Cost: Metrics.BlendedCost.Amount}' \
        --output table 2>/dev/null || warning "Failed to get cost breakdown"
}

#############################################
# Get EC2 Costs
#############################################
get_ec2_costs() {
    log "🖥️  EC2 Instance Costs"

    # List running instances
    local instances=$(aws ec2 describe-instances \
        --filters "Name=instance-state-name,Values=running" \
        --query 'Reservations[].Instances[].{Id: InstanceId, Type: InstanceType, Name: Tags[?Key==`Name`].Value | [0]}' \
        --output table 2>/dev/null || echo "")

    if [[ -n "${instances}" ]]; then
        echo "${instances}"
        log "💡 Tip: Use reserved instances or savings plans for lower costs"
    else
        info "No running EC2 instances found"
    fi
}

#############################################
# Get RDS Costs
#############################################
get_rds_costs() {
    log "🗄️  RDS Database Costs"

    local databases=$(aws rds describe-db-instances \
        --query 'DBInstances[].{ID: DBInstanceIdentifier, Class: DBInstanceClass, Storage: AllocatedStorage, Engine: Engine}' \
        --output table 2>/dev/null || echo "")

    if [[ -n "${databases}" ]]; then
        echo "${databases}"
        log "💡 Tip: Use reserved instances for production databases"
    else
        info "No RDS instances found"
    fi
}

#############################################
# Get ECS Costs
#############################################
get_ecs_costs() {
    log "🐋 ECS Task Costs"

    local clusters=$(aws ecs list-clusters \
        --query 'clusterArns' \
        --output text 2>/dev/null || echo "")

    if [[ -n "${clusters}" ]]; then
        log "ECS Clusters:"
        echo "${clusters}" | tr '\t' '\n' | nl

        # Get running tasks count
        for cluster in ${clusters}; do
            local cluster_name=$(basename "${cluster}")
            local tasks=$(aws ecs describe-clusters \
                --clusters "${cluster_name}" \
                --query 'clusters[0].runningTasksCount' \
                --output text 2>/dev/null || echo "0")
            info "  ${cluster_name}: ${tasks} running tasks"
        done
    else
        info "No ECS clusters found"
    fi
}

#############################################
# Get S3 Costs
#############################################
get_s3_costs() {
    log "📦 S3 Storage Costs"

    local buckets=$(aws s3 ls \
        --recursive \
        --summarize \
        --human-readable 2>/dev/null || echo "")

    if [[ -n "${buckets}" ]]; then
        echo "${buckets}"
        log "💡 Tip: Enable S3 lifecycle policies for cost optimization"
    else
        info "No S3 buckets or unable to list"
    fi
}

#############################################
# Get Lambda Costs
#############################################
get_lambda_costs() {
    log "⚡ Lambda Function Costs"

    local functions=$(aws lambda list-functions \
        --query 'Functions[].{Name: FunctionName, Runtime: Runtime, Memory: MemorySize}' \
        --output table 2>/dev/null || echo "")

    if [[ -n "${functions}" ]]; then
        echo "${functions}"
        info "Check CloudWatch for invocation metrics"
    else
        info "No Lambda functions found"
    fi
}

#############################################
# Check Cost Anomalies
#############################################
check_cost_anomalies() {
    log "🔍 Checking for cost anomalies..."

    local current_cost=$(get_current_month_cost)
    local days_in_month=$(cal -u | awk 'NF {DAYS = $NF}; END {print DAYS}')
    local current_day=$(date -u +"%d")
    local projected_cost=$(echo "${current_cost} * ${days_in_month} / ${current_day}" | bc)

    log "Current Month: \$${current_cost}"
    log "Projected EOM: \$${projected_cost}"

    # Check thresholds
    if (( $(echo "${current_cost} > ${COST_THRESHOLD_CRITICAL}" | bc -l) )); then
        error "❌ CRITICAL: Current cost (\$${current_cost}) exceeds threshold (\$${COST_THRESHOLD_CRITICAL})"
        return 2
    elif (( $(echo "${current_cost} > ${COST_THRESHOLD_WARNING}" | bc -l) )); then
        warning "⚠️  WARNING: Current cost (\$${current_cost}) exceeds threshold (\$${COST_THRESHOLD_WARNING})"
        return 1
    else
        log "✅ Costs are within normal range"
        return 0
    fi
}

#############################################
# Cost Optimization Recommendations
#############################################
show_recommendations() {
    log "💡 Cost Optimization Recommendations"
    log "====================================="

    cat << 'EOF'
1. EC2 Instances:
   • Use reserved instances for baseline workloads (save up to 75%)
   • Use spot instances for fault-tolerant workloads (save up to 90%)
   • Right-size instances to match actual usage
   • Stop unused development instances

2. RDS Databases:
   • Use reserved instances for production (save up to 55%)
   • Enable multi-AZ only when needed
   • Use Aurora for better cost-performance ratio
   • Delete unused test databases

3. S3 Storage:
   • Use lifecycle policies to move old data to Glacier
   • Use appropriate storage class (Intelligent Tiering)
   • Enable S3 versioning only when needed
   • Clean up incomplete multipart uploads

4. ECS/Fargate:
   • Use Fargate Spot for non-critical tasks (save up to 70%)
   • Right-size task CPU and memory
   • Use Auto Scaling for variable workloads

5. Lambda:
   • Optimize memory setting (affects CPU and cost)
   • Use Lambda Reserved Concurrency for critical functions
   • Implement dead-letter queues to avoid retries

6. General:
   • Enable AWS Budgets for proactive alerts
   • Use Cost Explorer to analyze trends
   • Review and delete unused resources
   • Implement tagging for cost allocation

EOF
}

#############################################
# Generate Cost Report
#############################################
generate_report() {
    local report_file="${1:-cost-report-$(date +%Y%m%d).txt}"

    log "📄 Generating cost report: ${report_file}"

    {
        echo "╔════════════════════════════════════════════════════════════════╗"
        echo "║           FinanceHub AWS Cost Report                           ║"
        echo "║           Generated: $(date +'%Y-%m-%d %H:%M:%S')                   ║"
        echo "╚════════════════════════════════════════════════════════════════╝"
        echo ""
        echo "COST SUMMARY"
        echo "====================================="
        check_cost_anomalies || true
        echo ""
        echo ""
        echo "COST BREAKDOWN BY SERVICE"
        echo "====================================="
        get_cost_by_service
        echo ""
        echo ""
        echo "RESOURCE DETAILS"
        echo "====================================="
        get_ec2_costs
        echo ""
        get_rds_costs
        echo ""
        get_ecs_costs
        echo ""
        get_s3_costs
        echo ""
        get_lambda_costs
        echo ""
        echo ""
        echo "OPTIMIZATION RECOMMENDATIONS"
        echo "====================================="
        show_recommendations
    } > "${report_file}"

    log "✅ Report saved to: ${report_file}"
}

#############################################
# Main
#############################################
main() {
    local command="${1:-all}"
    shift || true

    log "🚀 FinanceHub Cost Monitoring"
    log "================================"

    check_aws_cli || exit 1

    case "${command}" in
        all)
            check_cost_anomalies
            echo ""
            get_cost_by_service
            echo ""
            get_ec2_costs
            echo ""
            get_rds_costs
            echo ""
            get_ecs_costs
            echo ""
            show_recommendations
            ;;
        summary)
            check_cost_anomalies
            ;;
        services)
            get_cost_by_service
            ;;
        ec2)
            get_ec2_costs
            ;;
        rds)
            get_rds_costs
            ;;
        ecs)
            get_ecs_costs
            ;;
        s3)
            get_s3_costs
            ;;
        lambda)
            get_lambda_costs
            ;;
        recommendations)
            show_recommendations
            ;;
        report)
            generate_report "$@"
            ;;
        help|--help|-h)
            cat << EOF
FinanceHub Cost Monitoring Script

Usage: $0 <command> [options]

Commands:
  all                    Show all cost information (default)
  summary                Show cost summary only
  services               Show cost breakdown by service
  ec2                    Show EC2 instance costs
  rds                    Show RDS database costs
  ecs                    Show ECS task costs
  s3                     Show S3 storage costs
  lambda                 Show Lambda function costs
  recommendations        Show cost optimization tips
  report [file]          Generate cost report to file

Environment Variables:
  AWS_REGION             AWS region (default: us-east-1)
  COST_THRESHOLD_WARNING Warning threshold in USD (default: 100)
  COST_THRESHOLD_CRITICAL Critical threshold in USD (default: 200)

Examples:
  $0 all
  $0 summary
  $0 ec2
  $0 report monthly-cost.txt

Author: KAREN (DevOps Engineer)
Date: 2026-01-30
EOF
            ;;
        *)
            error "Unknown command: ${command}"
            exit 1
            ;;
    esac
}

main "$@"
