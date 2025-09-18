#!/bin/bash

# Database Backup Script for FinClick.AI Platform
# Supports PostgreSQL, MongoDB, and Redis backups with compression and rotation

set -e

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=30
COMPRESSION_LEVEL=6
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database connection settings
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_DB=${POSTGRES_DB:-finclick_ai_main}
POSTGRES_USER=${POSTGRES_USER:-finclick_app}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-}

MONGODB_HOST=${MONGODB_HOST:-mongodb}
MONGODB_PORT=${MONGODB_PORT:-27017}
MONGODB_DB=${MONGODB_DB:-finclick_ai}
MONGODB_USER=${MONGODB_USER:-admin}
MONGODB_PASSWORD=${MONGODB_PASSWORD:-}

REDIS_HOST=${REDIS_HOST:-redis}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_PASSWORD=${REDIS_PASSWORD:-}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Create backup directories
create_backup_dirs() {
    mkdir -p "$BACKUP_DIR/postgresql"
    mkdir -p "$BACKUP_DIR/mongodb"
    mkdir -p "$BACKUP_DIR/redis"
    mkdir -p "$BACKUP_DIR/logs"
}

# PostgreSQL backup function
backup_postgresql() {
    log "Starting PostgreSQL backup..."

    local backup_file="$BACKUP_DIR/postgresql/postgres_backup_$TIMESTAMP.sql"
    local compressed_file="$backup_file.gz"

    # Create backup
    if PGPASSWORD="$POSTGRES_PASSWORD" pg_dump \
        -h "$POSTGRES_HOST" \
        -p "$POSTGRES_PORT" \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=custom \
        --compress=0 \
        > "$backup_file"; then

        # Compress backup
        if gzip -"$COMPRESSION_LEVEL" "$backup_file"; then
            log "PostgreSQL backup completed: $compressed_file"

            # Get backup size
            local backup_size=$(du -h "$compressed_file" | cut -f1)
            log_info "PostgreSQL backup size: $backup_size"

            # Create checksum
            sha256sum "$compressed_file" > "$compressed_file.sha256"
            log_info "PostgreSQL backup checksum created"

            # Test backup integrity
            if gzip -t "$compressed_file"; then
                log_info "PostgreSQL backup integrity verified"
                echo "$TIMESTAMP,postgresql,success,$backup_size" >> "$BACKUP_DIR/logs/backup_log.csv"
            else
                log_error "PostgreSQL backup integrity check failed"
                echo "$TIMESTAMP,postgresql,integrity_failed,$backup_size" >> "$BACKUP_DIR/logs/backup_log.csv"
                return 1
            fi
        else
            log_error "Failed to compress PostgreSQL backup"
            rm -f "$backup_file"
            echo "$TIMESTAMP,postgresql,compression_failed,0" >> "$BACKUP_DIR/logs/backup_log.csv"
            return 1
        fi
    else
        log_error "PostgreSQL backup failed"
        echo "$TIMESTAMP,postgresql,failed,0" >> "$BACKUP_DIR/logs/backup_log.csv"
        return 1
    fi
}

# MongoDB backup function
backup_mongodb() {
    log "Starting MongoDB backup..."

    local backup_dir="$BACKUP_DIR/mongodb/mongo_backup_$TIMESTAMP"
    local compressed_file="$backup_dir.tar.gz"

    # Create backup directory
    mkdir -p "$backup_dir"

    # Create backup
    if mongodump \
        --host "$MONGODB_HOST:$MONGODB_PORT" \
        --db "$MONGODB_DB" \
        --username "$MONGODB_USER" \
        --password "$MONGODB_PASSWORD" \
        --authenticationDatabase admin \
        --out "$backup_dir" \
        --gzip; then

        # Compress backup directory
        if tar -czf "$compressed_file" -C "$(dirname "$backup_dir")" "$(basename "$backup_dir")"; then
            log "MongoDB backup completed: $compressed_file"

            # Get backup size
            local backup_size=$(du -h "$compressed_file" | cut -f1)
            log_info "MongoDB backup size: $backup_size"

            # Create checksum
            sha256sum "$compressed_file" > "$compressed_file.sha256"
            log_info "MongoDB backup checksum created"

            # Clean up uncompressed directory
            rm -rf "$backup_dir"

            # Test backup integrity
            if tar -tzf "$compressed_file" >/dev/null; then
                log_info "MongoDB backup integrity verified"
                echo "$TIMESTAMP,mongodb,success,$backup_size" >> "$BACKUP_DIR/logs/backup_log.csv"
            else
                log_error "MongoDB backup integrity check failed"
                echo "$TIMESTAMP,mongodb,integrity_failed,$backup_size" >> "$BACKUP_DIR/logs/backup_log.csv"
                return 1
            fi
        else
            log_error "Failed to compress MongoDB backup"
            rm -rf "$backup_dir"
            echo "$TIMESTAMP,mongodb,compression_failed,0" >> "$BACKUP_DIR/logs/backup_log.csv"
            return 1
        fi
    else
        log_error "MongoDB backup failed"
        rm -rf "$backup_dir"
        echo "$TIMESTAMP,mongodb,failed,0" >> "$BACKUP_DIR/logs/backup_log.csv"
        return 1
    fi
}

# Redis backup function
backup_redis() {
    log "Starting Redis backup..."

    local backup_file="$BACKUP_DIR/redis/redis_backup_$TIMESTAMP.rdb"
    local compressed_file="$backup_file.gz"

    # Trigger Redis save
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" --no-auth-warning BGSAVE; then
        log_info "Redis background save initiated"

        # Wait for save to complete
        local save_in_progress=1
        local timeout=300  # 5 minutes timeout
        local elapsed=0

        while [ $save_in_progress -eq 1 ] && [ $elapsed -lt $timeout ]; do
            sleep 5
            elapsed=$((elapsed + 5))

            # Check if BGSAVE is complete
            local last_save=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" --no-auth-warning LASTSAVE)
            local current_time=$(date +%s)

            # If LASTSAVE timestamp is recent (within last 60 seconds), BGSAVE is complete
            if [ $((current_time - last_save)) -le 60 ]; then
                save_in_progress=0
            fi
        done

        if [ $save_in_progress -eq 1 ]; then
            log_warning "Redis BGSAVE timeout, proceeding anyway"
        fi

        # Copy RDB file (this approach works in containerized environments)
        if docker exec finclick-redis redis-cli --rdb /tmp/dump.rdb -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" --no-auth-warning; then
            # Copy the RDB file from container
            if docker cp finclick-redis:/tmp/dump.rdb "$backup_file"; then
                # Compress backup
                if gzip -"$COMPRESSION_LEVEL" "$backup_file"; then
                    log "Redis backup completed: $compressed_file"

                    # Get backup size
                    local backup_size=$(du -h "$compressed_file" | cut -f1)
                    log_info "Redis backup size: $backup_size"

                    # Create checksum
                    sha256sum "$compressed_file" > "$compressed_file.sha256"
                    log_info "Redis backup checksum created"

                    # Test backup integrity
                    if gzip -t "$compressed_file"; then
                        log_info "Redis backup integrity verified"
                        echo "$TIMESTAMP,redis,success,$backup_size" >> "$BACKUP_DIR/logs/backup_log.csv"
                    else
                        log_error "Redis backup integrity check failed"
                        echo "$TIMESTAMP,redis,integrity_failed,$backup_size" >> "$BACKUP_DIR/logs/backup_log.csv"
                        return 1
                    fi

                    # Clean up temporary file
                    docker exec finclick-redis rm -f /tmp/dump.rdb
                else
                    log_error "Failed to compress Redis backup"
                    rm -f "$backup_file"
                    echo "$TIMESTAMP,redis,compression_failed,0" >> "$BACKUP_DIR/logs/backup_log.csv"
                    return 1
                fi
            else
                log_error "Failed to copy Redis RDB file"
                echo "$TIMESTAMP,redis,copy_failed,0" >> "$BACKUP_DIR/logs/backup_log.csv"
                return 1
            fi
        else
            log_error "Failed to create Redis RDB dump"
            echo "$TIMESTAMP,redis,rdb_failed,0" >> "$BACKUP_DIR/logs/backup_log.csv"
            return 1
        fi
    else
        log_error "Redis backup failed to initiate"
        echo "$TIMESTAMP,redis,failed,0" >> "$BACKUP_DIR/logs/backup_log.csv"
        return 1
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."

    # PostgreSQL backups
    find "$BACKUP_DIR/postgresql" -name "*.gz" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/postgresql" -name "*.sha256" -type f -mtime +$RETENTION_DAYS -delete

    # MongoDB backups
    find "$BACKUP_DIR/mongodb" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/mongodb" -name "*.sha256" -type f -mtime +$RETENTION_DAYS -delete

    # Redis backups
    find "$BACKUP_DIR/redis" -name "*.gz" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR/redis" -name "*.sha256" -type f -mtime +$RETENTION_DAYS -delete

    log_info "Old backup cleanup completed"
}

# Generate backup report
generate_backup_report() {
    log "Generating backup report..."

    local report_file="$BACKUP_DIR/logs/backup_report_$TIMESTAMP.txt"

    cat > "$report_file" << EOF
FinClick.AI Database Backup Report
Generated: $(date)
=================================

BACKUP SUMMARY:
EOF

    # Count files and sizes
    local pg_count=$(find "$BACKUP_DIR/postgresql" -name "*.gz" -type f | wc -l)
    local pg_size=$(du -sh "$BACKUP_DIR/postgresql" 2>/dev/null | cut -f1 || echo "0")

    local mongo_count=$(find "$BACKUP_DIR/mongodb" -name "*.tar.gz" -type f | wc -l)
    local mongo_size=$(du -sh "$BACKUP_DIR/mongodb" 2>/dev/null | cut -f1 || echo "0")

    local redis_count=$(find "$BACKUP_DIR/redis" -name "*.gz" -type f | wc -l)
    local redis_size=$(du -sh "$BACKUP_DIR/redis" 2>/dev/null | cut -f1 || echo "0")

    cat >> "$report_file" << EOF

PostgreSQL Backups: $pg_count files, $pg_size total
MongoDB Backups: $mongo_count files, $mongo_size total
Redis Backups: $redis_count files, $redis_size total

LATEST BACKUP STATUS:
EOF

    # Show latest backup status from log
    if [ -f "$BACKUP_DIR/logs/backup_log.csv" ]; then
        tail -3 "$BACKUP_DIR/logs/backup_log.csv" >> "$report_file"
    fi

    cat >> "$report_file" << EOF

DISK USAGE:
$(df -h "$BACKUP_DIR")

RECENT BACKUP FILES:
EOF

    # List recent backup files
    find "$BACKUP_DIR" -name "*.gz" -o -name "*.tar.gz" | sort -r | head -10 >> "$report_file"

    log_info "Backup report generated: $report_file"
}

# Health check function
health_check() {
    log "Performing database health checks..."

    local all_healthy=true

    # PostgreSQL health check
    if PGPASSWORD="$POSTGRES_PASSWORD" pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; then
        log_info "PostgreSQL is healthy"
    else
        log_error "PostgreSQL health check failed"
        all_healthy=false
    fi

    # MongoDB health check
    if mongosh --host "$MONGODB_HOST:$MONGODB_PORT" --username "$MONGODB_USER" --password "$MONGODB_PASSWORD" --authenticationDatabase admin --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
        log_info "MongoDB is healthy"
    else
        log_error "MongoDB health check failed"
        all_healthy=false
    fi

    # Redis health check
    if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" --no-auth-warning ping >/dev/null 2>&1; then
        log_info "Redis is healthy"
    else
        log_error "Redis health check failed"
        all_healthy=false
    fi

    if [ "$all_healthy" = true ]; then
        log "All databases are healthy"
        return 0
    else
        log_error "Some databases failed health checks"
        return 1
    fi
}

# Main backup function
main() {
    log "Starting FinClick.AI database backup process..."

    # Initialize CSV log if it doesn't exist
    if [ ! -f "$BACKUP_DIR/logs/backup_log.csv" ]; then
        echo "timestamp,database,status,size" > "$BACKUP_DIR/logs/backup_log.csv"
    fi

    create_backup_dirs

    # Perform health checks first
    if ! health_check; then
        log_warning "Some health checks failed, but continuing with backup..."
    fi

    local backup_success=true

    # Perform backups
    if ! backup_postgresql; then
        backup_success=false
    fi

    if ! backup_mongodb; then
        backup_success=false
    fi

    if ! backup_redis; then
        backup_success=false
    fi

    # Cleanup old backups
    cleanup_old_backups

    # Generate report
    generate_backup_report

    if [ "$backup_success" = true ]; then
        log "All database backups completed successfully"
        exit 0
    else
        log_error "Some backups failed. Check logs for details."
        exit 1
    fi
}

# Handle script arguments
case "${1:-backup}" in
    "backup")
        main
        ;;
    "health")
        health_check
        ;;
    "cleanup")
        cleanup_old_backups
        ;;
    "report")
        generate_backup_report
        ;;
    *)
        echo "Usage: $0 {backup|health|cleanup|report}"
        echo "  backup  - Perform full backup of all databases (default)"
        echo "  health  - Check database health"
        echo "  cleanup - Clean up old backup files"
        echo "  report  - Generate backup report"
        exit 1
        ;;
esac