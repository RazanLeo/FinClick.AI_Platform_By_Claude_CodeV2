#!/bin/bash

# FinClick.AI Backup Script
# Comprehensive backup solution for databases, volumes, and configurations

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BACKUP_DIR="${PROJECT_ROOT}/backups"
LOG_FILE="${BACKUP_DIR}/backup-$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Default settings
DEFAULT_ENVIRONMENT="production"
DEFAULT_BACKUP_TYPE="full"
RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
FinClick.AI Backup Script

Usage: $0 [OPTIONS]

OPTIONS:
    -h, --help                  Show this help message
    -e, --environment ENV       Environment to backup (production, staging, development)
    -t, --type TYPE            Backup type (full, database, volumes, config)
    -d, --destination DIR      Backup destination directory
    -c, --compress             Compress backup files
    -r, --retention DAYS       Retention period in days (default: 30)
    -s, --s3-upload           Upload backup to S3
    -n, --dry-run             Show what would be done without executing
    -v, --verbose             Enable verbose output
    -f, --force               Force backup without confirmation

BACKUP TYPES:
    full                      Complete system backup (databases + volumes + config)
    database                  Database backup only (PostgreSQL + MongoDB + Redis)
    volumes                   Docker volumes backup only
    config                   Configuration files backup only

EXAMPLES:
    $0 --environment production --type full --s3-upload
    $0 -e staging -t database -c
    $0 --dry-run --environment production

EOF
}

# Check prerequisites
check_prerequisites() {
    local missing_tools=()

    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_tools+=("docker-compose")
    command -v pg_dump >/dev/null 2>&1 || missing_tools+=("pg_dump")
    command -v mongodump >/dev/null 2>&1 || missing_tools+=("mongodump")
    command -v tar >/dev/null 2>&1 || missing_tools+=("tar")

    if [ ${#missing_tools[@]} -ne 0 ]; then
        error "Missing required tools: ${missing_tools[*]}"
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

# Create backup directory structure
create_backup_structure() {
    local backup_path=$1

    mkdir -p "${backup_path}"/{databases,volumes,config,logs}
    log "Created backup directory structure at ${backup_path}"
}

# Backup PostgreSQL database
backup_postgresql() {
    local backup_path=$1
    local container_name="${2:-finclick-postgres-master}"

    log "Starting PostgreSQL backup..."

    local pg_backup_file="${backup_path}/databases/postgresql_${TIMESTAMP}.sql"

    if docker ps --format "table {{.Names}}" | grep -q "${container_name}"; then
        docker exec "${container_name}" pg_dumpall -U "${POSTGRES_USER}" > "${pg_backup_file}"

        if [ -f "${pg_backup_file}" ] && [ -s "${pg_backup_file}" ]; then
            log "PostgreSQL backup completed: ${pg_backup_file}"

            # Create schema-only backup
            local schema_backup="${backup_path}/databases/postgresql_schema_${TIMESTAMP}.sql"
            docker exec "${container_name}" pg_dumpall -U "${POSTGRES_USER}" --schema-only > "${schema_backup}"

            # Get database size information
            docker exec "${container_name}" psql -U "${POSTGRES_USER}" -c "
                SELECT
                    datname as database_name,
                    pg_size_pretty(pg_database_size(datname)) as size
                FROM pg_database
                WHERE datistemplate = false;
            " > "${backup_path}/databases/postgresql_info_${TIMESTAMP}.txt"

        else
            error "PostgreSQL backup failed or file is empty"
            return 1
        fi
    else
        warn "PostgreSQL container ${container_name} not running, skipping backup"
    fi
}

# Backup MongoDB database
backup_mongodb() {
    local backup_path=$1
    local container_name="${2:-finclick-mongo-primary}"

    log "Starting MongoDB backup..."

    local mongo_backup_dir="${backup_path}/databases/mongodb_${TIMESTAMP}"

    if docker ps --format "table {{.Names}}" | grep -q "${container_name}"; then
        # Create backup directory
        mkdir -p "${mongo_backup_dir}"

        # Run mongodump inside container
        docker exec "${container_name}" mongodump \
            --host localhost:27017 \
            --username "${MONGO_ROOT_USER}" \
            --password "${MONGO_ROOT_PASSWORD}" \
            --authenticationDatabase admin \
            --out /tmp/backup

        # Copy backup from container
        docker cp "${container_name}:/tmp/backup" "${mongo_backup_dir}/"

        if [ -d "${mongo_backup_dir}/backup" ]; then
            log "MongoDB backup completed: ${mongo_backup_dir}"

            # Get collection statistics
            docker exec "${container_name}" mongo \
                --username "${MONGO_ROOT_USER}" \
                --password "${MONGO_ROOT_PASSWORD}" \
                --authenticationDatabase admin \
                --eval "
                    db.adminCommand('listCollections').cursor.firstBatch.forEach(
                        function(collection) {
                            print(collection.name + ': ' + db[collection.name].count() + ' documents');
                        }
                    )
                " > "${backup_path}/databases/mongodb_info_${TIMESTAMP}.txt"
        else
            error "MongoDB backup failed"
            return 1
        fi

        # Cleanup container backup
        docker exec "${container_name}" rm -rf /tmp/backup
    else
        warn "MongoDB container ${container_name} not running, skipping backup"
    fi
}

# Backup Redis database
backup_redis() {
    local backup_path=$1
    local container_name="${2:-finclick-redis-master}"

    log "Starting Redis backup..."

    if docker ps --format "table {{.Names}}" | grep -q "${container_name}"; then
        # Force Redis to save current state
        docker exec "${container_name}" redis-cli BGSAVE

        # Wait for background save to complete
        while [ "$(docker exec "${container_name}" redis-cli LASTSAVE)" = "$(docker exec "${container_name}" redis-cli LASTSAVE)" ]; do
            sleep 1
        done

        # Copy dump file
        docker cp "${container_name}:/data/dump.rdb" "${backup_path}/databases/redis_${TIMESTAMP}.rdb"

        if [ -f "${backup_path}/databases/redis_${TIMESTAMP}.rdb" ]; then
            log "Redis backup completed: ${backup_path}/databases/redis_${TIMESTAMP}.rdb"

            # Get Redis info
            docker exec "${container_name}" redis-cli INFO > "${backup_path}/databases/redis_info_${TIMESTAMP}.txt"
        else
            error "Redis backup failed"
            return 1
        fi
    else
        warn "Redis container ${container_name} not running, skipping backup"
    fi
}

# Backup Docker volumes
backup_volumes() {
    local backup_path=$1
    local environment=$2

    log "Starting Docker volumes backup..."

    local volumes_backup_dir="${backup_path}/volumes"
    mkdir -p "${volumes_backup_dir}"

    # Get list of volumes for the environment
    local volumes=$(docker volume ls --format "{{.Name}}" | grep "finclick" || true)

    if [ -z "${volumes}" ]; then
        warn "No FinClick.AI volumes found"
        return 0
    fi

    for volume in ${volumes}; do
        info "Backing up volume: ${volume}"

        local volume_backup="${volumes_backup_dir}/${volume}_${TIMESTAMP}.tar"

        # Create temporary container to backup volume
        docker run --rm \
            -v "${volume}:/data:ro" \
            -v "${volumes_backup_dir}:/backup" \
            alpine:latest \
            tar -czf "/backup/${volume}_${TIMESTAMP}.tar.gz" -C /data .

        if [ -f "${volume_backup}.gz" ]; then
            log "Volume backup completed: ${volume_backup}.gz"
        else
            error "Volume backup failed for: ${volume}"
        fi
    done
}

# Backup configuration files
backup_config() {
    local backup_path=$1

    log "Starting configuration backup..."

    local config_backup_dir="${backup_path}/config"
    mkdir -p "${config_backup_dir}"

    # Backup docker-compose files
    cp "${PROJECT_ROOT}"/docker-compose*.yml "${config_backup_dir}/" 2>/dev/null || true

    # Backup environment files
    cp "${PROJECT_ROOT}"/.env* "${config_backup_dir}/" 2>/dev/null || true

    # Backup nginx configuration
    if [ -d "${PROJECT_ROOT}/nginx" ]; then
        cp -r "${PROJECT_ROOT}/nginx" "${config_backup_dir}/"
    fi

    # Backup monitoring configuration
    if [ -d "${PROJECT_ROOT}/monitoring" ]; then
        cp -r "${PROJECT_ROOT}/monitoring" "${config_backup_dir}/"
    fi

    # Backup scripts
    if [ -d "${PROJECT_ROOT}/scripts" ]; then
        cp -r "${PROJECT_ROOT}/scripts" "${config_backup_dir}/"
    fi

    # Create configuration manifest
    cat > "${config_backup_dir}/manifest.txt" << EOF
FinClick.AI Configuration Backup
Timestamp: ${TIMESTAMP}
Environment: ${ENVIRONMENT}
Git Commit: $(cd "${PROJECT_ROOT}" && git rev-parse HEAD 2>/dev/null || echo "unknown")
Git Branch: $(cd "${PROJECT_ROOT}" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
Backup Host: $(hostname)
Files Included:
$(find "${config_backup_dir}" -type f | sed 's|'"${config_backup_dir}"'||')
EOF

    log "Configuration backup completed: ${config_backup_dir}"
}

# Compress backup files
compress_backup() {
    local backup_path=$1

    log "Compressing backup files..."

    local compressed_file="${backup_path}_compressed.tar.gz"

    tar -czf "${compressed_file}" -C "$(dirname "${backup_path}")" "$(basename "${backup_path}")"

    if [ -f "${compressed_file}" ]; then
        local original_size=$(du -sh "${backup_path}" | cut -f1)
        local compressed_size=$(du -sh "${compressed_file}" | cut -f1)

        log "Backup compressed successfully:"
        info "  Original size: ${original_size}"
        info "  Compressed size: ${compressed_size}"
        info "  Compressed file: ${compressed_file}"

        # Remove original backup directory
        rm -rf "${backup_path}"

        echo "${compressed_file}"
    else
        error "Backup compression failed"
        return 1
    fi
}

# Upload to S3
upload_to_s3() {
    local backup_file=$1
    local s3_bucket="${AWS_S3_BACKUP_BUCKET:-finclick-backups}"
    local s3_key="finclick/${ENVIRONMENT}/$(basename "${backup_file}")"

    if [ -z "${AWS_ACCESS_KEY_ID:-}" ] || [ -z "${AWS_SECRET_ACCESS_KEY:-}" ]; then
        warn "AWS credentials not configured, skipping S3 upload"
        return 0
    fi

    log "Uploading backup to S3: s3://${s3_bucket}/${s3_key}"

    if command -v aws >/dev/null 2>&1; then
        aws s3 cp "${backup_file}" "s3://${s3_bucket}/${s3_key}" \
            --storage-class STANDARD_IA \
            --metadata "environment=${ENVIRONMENT},timestamp=${TIMESTAMP}"

        log "Backup uploaded to S3 successfully"

        # Set lifecycle policy if not exists
        aws s3api put-bucket-lifecycle-configuration \
            --bucket "${s3_bucket}" \
            --lifecycle-configuration file://"${SCRIPT_DIR}/s3-lifecycle-policy.json" \
            2>/dev/null || true
    else
        warn "AWS CLI not installed, skipping S3 upload"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    local retention_days=$1

    log "Cleaning up backups older than ${retention_days} days..."

    # Local cleanup
    find "${BACKUP_DIR}" -name "backup_*" -type d -mtime +${retention_days} -exec rm -rf {} \; 2>/dev/null || true
    find "${BACKUP_DIR}" -name "backup_*.tar.gz" -type f -mtime +${retention_days} -delete 2>/dev/null || true

    # S3 cleanup (handled by lifecycle policy)
    log "Local backup cleanup completed"
}

# Generate backup report
generate_report() {
    local backup_path=$1
    local backup_type=$2

    local report_file="${BACKUP_DIR}/backup_report_${TIMESTAMP}.txt"

    cat > "${report_file}" << EOF
FinClick.AI Backup Report
========================

Backup Information:
  Timestamp: ${TIMESTAMP}
  Environment: ${ENVIRONMENT}
  Backup Type: ${backup_type}
  Backup Path: ${backup_path}

System Information:
  Hostname: $(hostname)
  OS: $(uname -s)
  Kernel: $(uname -r)
  Docker Version: $(docker --version)

Backup Contents:
$(if [ -d "${backup_path}" ]; then
    find "${backup_path}" -type f -exec ls -lh {} \; | awk '{print "  " $9 " (" $5 ")"}'
elif [ -f "${backup_path}" ]; then
    ls -lh "${backup_path}" | awk '{print "  " $9 " (" $5 ")"}'
fi)

Database Information:
$([ -f "${backup_path}/databases/postgresql_info_${TIMESTAMP}.txt" ] && echo "PostgreSQL:" && cat "${backup_path}/databases/postgresql_info_${TIMESTAMP}.txt" | sed 's/^/  /')
$([ -f "${backup_path}/databases/mongodb_info_${TIMESTAMP}.txt" ] && echo "MongoDB:" && cat "${backup_path}/databases/mongodb_info_${TIMESTAMP}.txt" | sed 's/^/  /')
$([ -f "${backup_path}/databases/redis_info_${TIMESTAMP}.txt" ] && echo "Redis:" && cat "${backup_path}/databases/redis_info_${TIMESTAMP}.txt" | sed 's/^/  /')

Total Backup Size: $(du -sh "${backup_path}" 2>/dev/null | cut -f1 || echo "Unknown")

Backup completed at: $(date)
EOF

    log "Backup report generated: ${report_file}"
}

# Main backup function
main() {
    local environment="${DEFAULT_ENVIRONMENT}"
    local backup_type="${DEFAULT_BACKUP_TYPE}"
    local destination="${BACKUP_DIR}"
    local compress=false
    local retention_days=${RETENTION_DAYS}
    local s3_upload=false
    local dry_run=false
    local verbose=false
    local force=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -e|--environment)
                environment="$2"
                shift 2
                ;;
            -t|--type)
                backup_type="$2"
                shift 2
                ;;
            -d|--destination)
                destination="$2"
                shift 2
                ;;
            -c|--compress)
                compress=true
                shift
                ;;
            -r|--retention)
                retention_days="$2"
                shift 2
                ;;
            -s|--s3-upload)
                s3_upload=true
                shift
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                set -x
                shift
                ;;
            -f|--force)
                force=true
                shift
                ;;
            *)
                error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Set global environment variable
    export ENVIRONMENT="${environment}"

    # Create log directory
    mkdir -p "$(dirname "${LOG_FILE}")"

    log "Starting FinClick.AI backup for ${environment} environment"
    log "Backup type: ${backup_type}"

    # Dry run mode
    if [ "${dry_run}" = true ]; then
        info "DRY RUN MODE - No actual backup will be created"
        info "Would backup environment: ${environment}"
        info "Would backup type: ${backup_type}"
        info "Would backup to: ${destination}"
        exit 0
    fi

    # Check prerequisites
    check_prerequisites

    # Load environment variables
    load_environment "${environment}"

    # Create backup directory
    local backup_path="${destination}/backup_${environment}_${backup_type}_${TIMESTAMP}"
    create_backup_structure "${backup_path}"

    # Perform backup based on type
    case ${backup_type} in
        full)
            backup_postgresql "${backup_path}"
            backup_mongodb "${backup_path}"
            backup_redis "${backup_path}"
            backup_volumes "${backup_path}" "${environment}"
            backup_config "${backup_path}"
            ;;
        database)
            backup_postgresql "${backup_path}"
            backup_mongodb "${backup_path}"
            backup_redis "${backup_path}"
            ;;
        volumes)
            backup_volumes "${backup_path}" "${environment}"
            ;;
        config)
            backup_config "${backup_path}"
            ;;
        *)
            error "Invalid backup type: ${backup_type}"
            exit 1
            ;;
    esac

    # Generate backup report
    generate_report "${backup_path}" "${backup_type}"

    # Compress backup if requested
    if [ "${compress}" = true ]; then
        backup_path=$(compress_backup "${backup_path}")
    fi

    # Upload to S3 if requested
    if [ "${s3_upload}" = true ]; then
        upload_to_s3 "${backup_path}"
    fi

    # Cleanup old backups
    cleanup_old_backups "${retention_days}"

    log "Backup completed successfully: ${backup_path}"
}

# Trap errors
trap 'error "Backup failed"; exit 1' ERR

# Run main function
main "$@"