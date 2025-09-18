#!/bin/bash

# FinClick.AI Deployment Script
# Comprehensive deployment automation for production, staging, and development environments

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/logs/deployment-$(date +%Y%m%d_%H%M%S).log"
ENVIRONMENTS=("development" "staging" "production")
DEFAULT_ENVIRONMENT="development"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${LOG_FILE}"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "${LOG_FILE}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "${LOG_FILE}"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "${LOG_FILE}"
}

# Help function
show_help() {
    cat << EOF
FinClick.AI Deployment Script

Usage: $0 [OPTIONS] [ENVIRONMENT]

ENVIRONMENTS:
    development    Deploy to development environment (default)
    staging        Deploy to staging environment
    production     Deploy to production environment

OPTIONS:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose output
    -n, --dry-run          Show what would be done without executing
    -f, --force            Force deployment without confirmation
    -b, --backup           Create backup before deployment
    -r, --rollback [TAG]   Rollback to previous version or specific tag
    -u, --update-only      Update existing services without recreation
    -c, --clean            Clean up unused images and volumes after deployment
    -s, --skip-tests       Skip running tests before deployment
    -m, --migrate          Run database migrations

EXAMPLES:
    $0 development
    $0 -f -b production
    $0 --rollback v1.2.0 production
    $0 --dry-run staging

EOF
}

# Check prerequisites
check_prerequisites() {
    local missing_tools=()

    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_tools+=("docker-compose")
    command -v git >/dev/null 2>&1 || missing_tools+=("git")
    command -v curl >/dev/null 2>&1 || missing_tools+=("curl")
    command -v jq >/dev/null 2>&1 || missing_tools+=("jq")

    if [ ${#missing_tools[@]} -ne 0 ]; then
        error "Missing required tools: ${missing_tools[*]}"
        error "Please install them before running this script"
        exit 1
    fi

    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        error "Docker daemon is not running"
        exit 1
    fi

    # Check if we're in the right directory
    if [ ! -f "${PROJECT_ROOT}/docker-compose.yml" ]; then
        error "docker-compose.yml not found in project root"
        exit 1
    fi
}

# Load environment variables
load_environment() {
    local env=$1
    local env_file="${PROJECT_ROOT}/.env.${env}"

    if [ ! -f "${env_file}" ]; then
        error "Environment file ${env_file} not found"
        exit 1
    fi

    log "Loading environment variables from ${env_file}"
    set -a
    source "${env_file}"
    set +a
}

# Validate environment
validate_environment() {
    local env=$1

    if [[ ! " ${ENVIRONMENTS[@]} " =~ " ${env} " ]]; then
        error "Invalid environment: ${env}"
        error "Valid environments: ${ENVIRONMENTS[*]}"
        exit 1
    fi
}

# Create backup
create_backup() {
    local env=$1
    log "Creating backup for ${env} environment..."

    local backup_script="${SCRIPT_DIR}/../backup/backup.sh"
    if [ -f "${backup_script}" ]; then
        bash "${backup_script}" --environment "${env}" --type full
    else
        warn "Backup script not found, skipping backup"
    fi
}

# Run tests
run_tests() {
    local env=$1
    log "Running tests for ${env} environment..."

    # Run unit tests
    if [ -f "${PROJECT_ROOT}/package.json" ]; then
        info "Running unit tests..."
        npm test || (error "Unit tests failed" && exit 1)
    fi

    # Run integration tests
    if [ -f "${PROJECT_ROOT}/tests/integration/run.sh" ]; then
        info "Running integration tests..."
        bash "${PROJECT_ROOT}/tests/integration/run.sh" || (error "Integration tests failed" && exit 1)
    fi

    # Run security scans
    if command -v trivy >/dev/null 2>&1; then
        info "Running security scans..."
        trivy fs "${PROJECT_ROOT}" --exit-code 1 --severity HIGH,CRITICAL || warn "Security issues found"
    fi
}

# Build images
build_images() {
    local env=$1
    log "Building Docker images for ${env} environment..."

    local compose_file="docker-compose.${env}.yml"
    if [ "${env}" = "development" ]; then
        compose_file="docker-compose.dev.yml"
    elif [ "${env}" = "production" ]; then
        compose_file="docker-compose.production.yml"
    fi

    if [ ! -f "${PROJECT_ROOT}/${compose_file}" ]; then
        error "Compose file ${compose_file} not found"
        exit 1
    fi

    docker-compose -f "${compose_file}" build --parallel
}

# Deploy services
deploy_services() {
    local env=$1
    local update_only=$2

    log "Deploying services for ${env} environment..."

    local compose_file="docker-compose.${env}.yml"
    if [ "${env}" = "development" ]; then
        compose_file="docker-compose.dev.yml"
    elif [ "${env}" = "production" ]; then
        compose_file="docker-compose.production.yml"
    fi

    cd "${PROJECT_ROOT}"

    if [ "${update_only}" = true ]; then
        docker-compose -f "${compose_file}" up -d --no-recreate
    else
        docker-compose -f "${compose_file}" up -d --remove-orphans
    fi
}

# Run database migrations
run_migrations() {
    local env=$1
    log "Running database migrations for ${env} environment..."

    # PostgreSQL migrations
    local migration_script="${PROJECT_ROOT}/database/migrations/run.sh"
    if [ -f "${migration_script}" ]; then
        bash "${migration_script}" --environment "${env}"
    fi

    # MongoDB migrations
    local mongo_migration_script="${PROJECT_ROOT}/database/mongo/migrations/run.sh"
    if [ -f "${mongo_migration_script}" ]; then
        bash "${mongo_migration_script}" --environment "${env}"
    fi
}

# Health checks
perform_health_checks() {
    local env=$1
    log "Performing health checks for ${env} environment..."

    local services=("nginx" "api-gateway" "auth-service" "user-service" "analysis-service")
    local max_attempts=30
    local attempt=1

    for service in "${services[@]}"; do
        info "Checking health of ${service}..."

        while [ $attempt -le $max_attempts ]; do
            if docker-compose ps "${service}" | grep -q "Up (healthy)"; then
                log "${service} is healthy"
                break
            elif [ $attempt -eq $max_attempts ]; then
                error "${service} failed health check after ${max_attempts} attempts"
                return 1
            else
                info "Attempt ${attempt}/${max_attempts}: ${service} not ready yet, waiting..."
                sleep 10
                ((attempt++))
            fi
        done
        attempt=1
    done

    # Additional application-specific health checks
    local health_check_script="${PROJECT_ROOT}/scripts/monitoring/health-check.sh"
    if [ -f "${health_check_script}" ]; then
        bash "${health_check_script}" --environment "${env}"
    fi
}

# Cleanup resources
cleanup_resources() {
    log "Cleaning up unused Docker resources..."

    # Remove unused images
    docker image prune -f

    # Remove unused volumes (be careful in production)
    if [ "${ENVIRONMENT}" != "production" ]; then
        docker volume prune -f
    fi

    # Remove unused networks
    docker network prune -f
}

# Rollback function
rollback() {
    local env=$1
    local tag=$2

    log "Rolling back ${env} environment to ${tag}..."

    # Stop current services
    docker-compose -f "docker-compose.${env}.yml" down

    # Restore from backup if available
    local restore_script="${SCRIPT_DIR}/../backup/restore.sh"
    if [ -f "${restore_script}" ]; then
        bash "${restore_script}" --environment "${env}" --tag "${tag}"
    fi

    # Redeploy with specified tag
    export IMAGE_TAG="${tag}"
    deploy_services "${env}" false
}

# Send deployment notifications
send_notifications() {
    local env=$1
    local status=$2

    # Slack notification
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        local color="good"
        if [ "${status}" != "success" ]; then
            color="danger"
        fi

        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"${color}\",\"text\":\"FinClick.AI ${env} deployment ${status}\"}]}" \
            "${SLACK_WEBHOOK_URL}"
    fi

    # Email notification (if configured)
    if [ -n "${NOTIFICATION_EMAIL:-}" ]; then
        echo "FinClick.AI ${env} deployment ${status}" | \
        mail -s "FinClick.AI Deployment ${status^}" "${NOTIFICATION_EMAIL}"
    fi
}

# Main deployment function
main() {
    local environment="${DEFAULT_ENVIRONMENT}"
    local verbose=false
    local dry_run=false
    local force=false
    local backup=false
    local update_only=false
    local clean=false
    local skip_tests=false
    local migrate=false
    local rollback_tag=""

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                set -x
                shift
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -b|--backup)
                backup=true
                shift
                ;;
            -r|--rollback)
                rollback_tag="$2"
                shift 2
                ;;
            -u|--update-only)
                update_only=true
                shift
                ;;
            -c|--clean)
                clean=true
                shift
                ;;
            -s|--skip-tests)
                skip_tests=true
                shift
                ;;
            -m|--migrate)
                migrate=true
                shift
                ;;
            development|staging|production)
                environment="$1"
                shift
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Validate environment
    validate_environment "${environment}"

    # Set global environment variable
    export ENVIRONMENT="${environment}"

    # Create log directory
    mkdir -p "$(dirname "${LOG_FILE}")"

    log "Starting FinClick.AI deployment to ${environment} environment"
    log "Deployment options: verbose=${verbose}, dry-run=${dry_run}, force=${force}, backup=${backup}"

    # Dry run mode
    if [ "${dry_run}" = true ]; then
        info "DRY RUN MODE - No actual changes will be made"
        info "Would deploy to: ${environment}"
        info "Would run backup: ${backup}"
        info "Would run tests: $(!${skip_tests})"
        info "Would run migrations: ${migrate}"
        exit 0
    fi

    # Confirmation for production
    if [ "${environment}" = "production" ] && [ "${force}" = false ]; then
        read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log "Deployment cancelled by user"
            exit 0
        fi
    fi

    # Check prerequisites
    check_prerequisites

    # Load environment variables
    load_environment "${environment}"

    # Handle rollback
    if [ -n "${rollback_tag}" ]; then
        rollback "${environment}" "${rollback_tag}"
        log "Rollback completed successfully"
        send_notifications "${environment}" "rollback_success"
        exit 0
    fi

    # Create backup if requested
    if [ "${backup}" = true ]; then
        create_backup "${environment}"
    fi

    # Run tests unless skipped
    if [ "${skip_tests}" = false ]; then
        run_tests "${environment}"
    fi

    # Build images
    build_images "${environment}"

    # Deploy services
    deploy_services "${environment}" "${update_only}"

    # Run migrations if requested
    if [ "${migrate}" = true ]; then
        run_migrations "${environment}"
    fi

    # Perform health checks
    if ! perform_health_checks "${environment}"; then
        error "Health checks failed"
        send_notifications "${environment}" "failure"
        exit 1
    fi

    # Cleanup if requested
    if [ "${clean}" = true ]; then
        cleanup_resources
    fi

    log "Deployment to ${environment} completed successfully!"
    send_notifications "${environment}" "success"
}

# Trap errors and send failure notifications
trap 'error "Deployment failed"; send_notifications "${ENVIRONMENT:-unknown}" "failure"; exit 1' ERR

# Run main function
main "$@"