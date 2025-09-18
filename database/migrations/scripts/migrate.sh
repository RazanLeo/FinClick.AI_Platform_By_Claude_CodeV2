#!/bin/bash

# Database Migration Script for FinClick.AI Platform
# Supports PostgreSQL and MongoDB migrations with version control

set -e

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MIGRATIONS_DIR="$(dirname "$SCRIPT_DIR")"
POSTGRESQL_MIGRATIONS_DIR="$MIGRATIONS_DIR/postgresql"
MONGODB_MIGRATIONS_DIR="$MIGRATIONS_DIR/mongodb"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-finclick_ai_main}
DB_USER=${DB_USER:-finclick_app}
DB_PASSWORD=${DB_PASSWORD:-}

MONGO_HOST=${MONGO_HOST:-localhost}
MONGO_PORT=${MONGO_PORT:-27017}
MONGO_DB=${MONGO_DB:-finclick_ai}
MONGO_USER=${MONGO_USER:-finclick_app}
MONGO_PASSWORD=${MONGO_PASSWORD:-}

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[MIGRATION]${NC} $1"
}

# Show usage information
show_usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    init                Initialize migration system
    status              Show migration status
    migrate             Run all pending migrations
    migrate-postgres    Run PostgreSQL migrations only
    migrate-mongo       Run MongoDB migrations only
    rollback [VERSION]  Rollback to specific version
    create [NAME]       Create new migration file
    validate            Validate all migration files
    help                Show this help message

Options:
    --dry-run           Show what would be executed without running
    --force             Force execution (use with caution)
    --verbose           Show detailed output
    --env [ENV]         Use specific environment (dev, staging, prod)

Environment Variables:
    DB_HOST             PostgreSQL host (default: localhost)
    DB_PORT             PostgreSQL port (default: 5432)
    DB_NAME             PostgreSQL database name
    DB_USER             PostgreSQL username
    DB_PASSWORD         PostgreSQL password
    MONGO_HOST          MongoDB host (default: localhost)
    MONGO_PORT          MongoDB port (default: 27017)
    MONGO_DB            MongoDB database name
    MONGO_USER          MongoDB username
    MONGO_PASSWORD      MongoDB password

Examples:
    $0 init
    $0 status
    $0 migrate --dry-run
    $0 migrate-postgres --verbose
    $0 rollback 001
    $0 create add_user_preferences
EOF
}

# Load environment-specific configuration
load_env_config() {
    local env=${1:-dev}
    local env_file="$SCRIPT_DIR/.env.$env"

    if [[ -f "$env_file" ]]; then
        print_status "Loading configuration for environment: $env"
        source "$env_file"
    else
        print_warning "Environment file not found: $env_file"
    fi
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."

    # Check PostgreSQL client
    if ! command -v psql &> /dev/null; then
        print_error "PostgreSQL client (psql) is required but not installed"
        exit 1
    fi

    # Check MongoDB client
    if ! command -v mongosh &> /dev/null && ! command -v mongo &> /dev/null; then
        print_error "MongoDB client (mongosh or mongo) is required but not installed"
        exit 1
    fi

    print_status "All dependencies satisfied"
}

# Initialize migration system
init_migration_system() {
    print_header "Initializing migration system..."

    # Create PostgreSQL migration tracking table
    cat > /tmp/init_migrations.sql << 'EOF'
CREATE SCHEMA IF NOT EXISTS migrations;

CREATE TABLE IF NOT EXISTS migrations.migration_history (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('postgresql', 'mongodb')),
    checksum VARCHAR(64) NOT NULL,
    applied_by VARCHAR(100) NOT NULL DEFAULT current_user,
    applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    execution_time_ms INTEGER,
    success BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_migration_history_version ON migrations.migration_history(version);
CREATE INDEX IF NOT EXISTS idx_migration_history_type ON migrations.migration_history(type);
CREATE INDEX IF NOT EXISTS idx_migration_history_applied_at ON migrations.migration_history(applied_at);
EOF

    # Execute PostgreSQL initialization
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f /tmp/init_migrations.sql; then
        print_status "PostgreSQL migration system initialized"
    else
        print_error "Failed to initialize PostgreSQL migration system"
        exit 1
    fi

    # Initialize MongoDB migration tracking
    cat > /tmp/init_mongo_migrations.js << 'EOF'
db = db.getSiblingDB('finclick_ai');

db.createCollection('migration_history', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['version', 'name', 'type', 'checksum', 'appliedAt'],
      properties: {
        version: { bsonType: 'string' },
        name: { bsonType: 'string' },
        type: { bsonType: 'string', enum: ['mongodb', 'postgresql'] },
        checksum: { bsonType: 'string' },
        appliedBy: { bsonType: 'string' },
        appliedAt: { bsonType: 'date' },
        executionTimeMs: { bsonType: 'number' },
        success: { bsonType: 'bool' }
      }
    }
  }
});

db.migration_history.createIndex({ version: 1 }, { unique: true });
db.migration_history.createIndex({ type: 1 });
db.migration_history.createIndex({ appliedAt: -1 });

print('MongoDB migration system initialized');
EOF

    # Execute MongoDB initialization
    if command -v mongosh &> /dev/null; then
        MONGO_CLIENT="mongosh"
    else
        MONGO_CLIENT="mongo"
    fi

    local mongo_conn=""
    if [[ -n "$MONGO_USER" && -n "$MONGO_PASSWORD" ]]; then
        mongo_conn="mongodb://$MONGO_USER:$MONGO_PASSWORD@$MONGO_HOST:$MONGO_PORT/$MONGO_DB"
    else
        mongo_conn="mongodb://$MONGO_HOST:$MONGO_PORT/$MONGO_DB"
    fi

    if $MONGO_CLIENT "$mongo_conn" /tmp/init_mongo_migrations.js; then
        print_status "MongoDB migration system initialized"
    else
        print_error "Failed to initialize MongoDB migration system"
        exit 1
    fi

    rm -f /tmp/init_migrations.sql /tmp/init_mongo_migrations.js
    print_status "Migration system initialization completed"
}

# Get migration status
get_migration_status() {
    print_header "Migration Status"

    # PostgreSQL migrations
    print_status "PostgreSQL Migrations:"
    if [[ -d "$POSTGRESQL_MIGRATIONS_DIR" ]]; then
        local applied_migrations
        applied_migrations=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version FROM migrations.migration_history WHERE type = 'postgresql' ORDER BY version;" 2>/dev/null | tr -d ' ')

        for migration_file in "$POSTGRESQL_MIGRATIONS_DIR"/*.sql; do
            if [[ -f "$migration_file" ]]; then
                local version=$(basename "$migration_file" .sql)
                if echo "$applied_migrations" | grep -q "^$version$"; then
                    echo -e "  ✓ $version ${GREEN}(applied)${NC}"
                else
                    echo -e "  ✗ $version ${YELLOW}(pending)${NC}"
                fi
            fi
        done
    else
        print_warning "PostgreSQL migrations directory not found"
    fi

    echo ""

    # MongoDB migrations
    print_status "MongoDB Migrations:"
    if [[ -d "$MONGODB_MIGRATIONS_DIR" ]]; then
        local mongo_conn=""
        if [[ -n "$MONGO_USER" && -n "$MONGO_PASSWORD" ]]; then
            mongo_conn="mongodb://$MONGO_USER:$MONGO_PASSWORD@$MONGO_HOST:$MONGO_PORT/$MONGO_DB"
        else
            mongo_conn="mongodb://$MONGO_HOST:$MONGO_PORT/$MONGO_DB"
        fi

        local applied_migrations
        if command -v mongosh &> /dev/null; then
            applied_migrations=$(mongosh "$mongo_conn" --quiet --eval "db.migration_history.find({type: 'mongodb'}).map(doc => doc.version).join('\n')" 2>/dev/null)
        else
            applied_migrations=$(mongo "$mongo_conn" --quiet --eval "db.migration_history.find({type: 'mongodb'}).map(doc => doc.version).join('\n')" 2>/dev/null)
        fi

        for migration_file in "$MONGODB_MIGRATIONS_DIR"/*.js; do
            if [[ -f "$migration_file" ]]; then
                local version=$(basename "$migration_file" .js)
                if echo "$applied_migrations" | grep -q "^$version$"; then
                    echo -e "  ✓ $version ${GREEN}(applied)${NC}"
                else
                    echo -e "  ✗ $version ${YELLOW}(pending)${NC}"
                fi
            fi
        done
    else
        print_warning "MongoDB migrations directory not found"
    fi
}

# Calculate file checksum
calculate_checksum() {
    local file=$1
    if command -v sha256sum &> /dev/null; then
        sha256sum "$file" | cut -d' ' -f1
    elif command -v shasum &> /dev/null; then
        shasum -a 256 "$file" | cut -d' ' -f1
    else
        print_error "No checksum utility found (sha256sum or shasum required)"
        exit 1
    fi
}

# Run PostgreSQL migrations
run_postgresql_migrations() {
    local dry_run=${1:-false}

    print_header "Running PostgreSQL migrations..."

    if [[ ! -d "$POSTGRESQL_MIGRATIONS_DIR" ]]; then
        print_warning "PostgreSQL migrations directory not found"
        return 0
    fi

    local applied_migrations
    applied_migrations=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version FROM migrations.migration_history WHERE type = 'postgresql' ORDER BY version;" 2>/dev/null | tr -d ' ')

    for migration_file in $(ls "$POSTGRESQL_MIGRATIONS_DIR"/*.sql 2>/dev/null | sort); do
        local version=$(basename "$migration_file" .sql)
        local name=$(echo "$version" | sed 's/^[0-9]*_//')

        if echo "$applied_migrations" | grep -q "^$version$"; then
            print_status "Skipping already applied migration: $version"
            continue
        fi

        print_status "Applying migration: $version - $name"

        if [[ "$dry_run" == "true" ]]; then
            print_warning "DRY RUN: Would execute $migration_file"
            continue
        fi

        local start_time=$(date +%s%3N)
        local checksum=$(calculate_checksum "$migration_file")

        if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file"; then
            local end_time=$(date +%s%3N)
            local execution_time=$((end_time - start_time))

            # Record successful migration
            PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
                INSERT INTO migrations.migration_history (version, name, type, checksum, execution_time_ms, success)
                VALUES ('$version', '$name', 'postgresql', '$checksum', $execution_time, true);"

            print_status "Migration $version completed successfully (${execution_time}ms)"
        else
            print_error "Migration $version failed"
            exit 1
        fi
    done
}

# Run MongoDB migrations
run_mongodb_migrations() {
    local dry_run=${1:-false}

    print_header "Running MongoDB migrations..."

    if [[ ! -d "$MONGODB_MIGRATIONS_DIR" ]]; then
        print_warning "MongoDB migrations directory not found"
        return 0
    fi

    local mongo_conn=""
    if [[ -n "$MONGO_USER" && -n "$MONGO_PASSWORD" ]]; then
        mongo_conn="mongodb://$MONGO_USER:$MONGO_PASSWORD@$MONGO_HOST:$MONGO_PORT/$MONGO_DB"
    else
        mongo_conn="mongodb://$MONGO_HOST:$MONGO_PORT/$MONGO_DB"
    fi

    local mongo_client=""
    if command -v mongosh &> /dev/null; then
        mongo_client="mongosh"
    else
        mongo_client="mongo"
    fi

    local applied_migrations
    applied_migrations=$($mongo_client "$mongo_conn" --quiet --eval "db.migration_history.find({type: 'mongodb'}).map(doc => doc.version).join('\n')" 2>/dev/null)

    for migration_file in $(ls "$MONGODB_MIGRATIONS_DIR"/*.js 2>/dev/null | sort); do
        local version=$(basename "$migration_file" .js)
        local name=$(echo "$version" | sed 's/^[0-9]*_//')

        if echo "$applied_migrations" | grep -q "^$version$"; then
            print_status "Skipping already applied migration: $version"
            continue
        fi

        print_status "Applying migration: $version - $name"

        if [[ "$dry_run" == "true" ]]; then
            print_warning "DRY RUN: Would execute $migration_file"
            continue
        fi

        local start_time=$(date +%s%3N)
        local checksum=$(calculate_checksum "$migration_file")

        # Create wrapper script to track execution
        cat > /tmp/mongo_migration_wrapper.js << EOF
var startTime = new Date();
try {
    load('$migration_file');
    var endTime = new Date();
    var executionTime = endTime - startTime;

    db.migration_history.insertOne({
        version: '$version',
        name: '$name',
        type: 'mongodb',
        checksum: '$checksum',
        appliedBy: 'migration_script',
        appliedAt: new Date(),
        executionTimeMs: executionTime,
        success: true
    });

    print('Migration $version completed successfully (' + executionTime + 'ms)');
} catch (error) {
    print('Migration $version failed: ' + error.message);
    quit(1);
}
EOF

        if $mongo_client "$mongo_conn" /tmp/mongo_migration_wrapper.js; then
            print_status "Migration $version completed successfully"
        else
            print_error "Migration $version failed"
            rm -f /tmp/mongo_migration_wrapper.js
            exit 1
        fi

        rm -f /tmp/mongo_migration_wrapper.js
    done
}

# Create new migration file
create_migration() {
    local name=$1
    local timestamp=$(date +%Y%m%d%H%M%S)
    local version="${timestamp}_${name}"

    if [[ -z "$name" ]]; then
        print_error "Migration name is required"
        show_usage
        exit 1
    fi

    print_header "Creating new migration: $version"

    # Create PostgreSQL migration file
    local pg_file="$POSTGRESQL_MIGRATIONS_DIR/${version}.sql"
    cat > "$pg_file" << EOF
-- Migration: $name
-- Created: $(date)
-- Version: $version

-- Add your PostgreSQL migration code here

BEGIN;

-- Example:
-- CREATE TABLE example_table (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- Remember to test your migration before applying to production!

COMMIT;
EOF

    # Create MongoDB migration file
    local mongo_file="$MONGODB_MIGRATIONS_DIR/${version}.js"
    cat > "$mongo_file" << EOF
// Migration: $name
// Created: $(date)
// Version: $version

// Switch to the FinClick.AI database
db = db.getSiblingDB('finclick_ai');

print('Running migration: $name');

try {
    // Add your MongoDB migration code here

    // Example:
    // db.createCollection('example_collection', {
    //     validator: {
    //         \$jsonSchema: {
    //             bsonType: 'object',
    //             required: ['name'],
    //             properties: {
    //                 name: { bsonType: 'string' }
    //             }
    //         }
    //     }
    // });

    // db.example_collection.createIndex({ name: 1 });

    print('Migration $name completed successfully');
} catch (error) {
    print('Migration $name failed: ' + error.message);
    throw error;
}
EOF

    print_status "Created PostgreSQL migration: $pg_file"
    print_status "Created MongoDB migration: $mongo_file"
    print_warning "Remember to add your migration code and test before applying!"
}

# Validate migration files
validate_migrations() {
    print_header "Validating migration files..."

    local errors=0

    # Validate PostgreSQL migrations
    if [[ -d "$POSTGRESQL_MIGRATIONS_DIR" ]]; then
        for migration_file in "$POSTGRESQL_MIGRATIONS_DIR"/*.sql; do
            if [[ -f "$migration_file" ]]; then
                local version=$(basename "$migration_file" .sql)
                print_status "Validating PostgreSQL migration: $version"

                # Basic syntax check (dry run)
                if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --single-transaction --set ON_ERROR_STOP=on --quiet -f "$migration_file" --dry-run 2>/dev/null; then
                    print_error "PostgreSQL migration $version has syntax errors"
                    ((errors++))
                fi
            fi
        done
    fi

    # Validate MongoDB migrations
    if [[ -d "$MONGODB_MIGRATIONS_DIR" ]]; then
        for migration_file in "$MONGODB_MIGRATIONS_DIR"/*.js; do
            if [[ -f "$migration_file" ]]; then
                local version=$(basename "$migration_file" .js)
                print_status "Validating MongoDB migration: $version"

                # Basic syntax check
                if ! node -c "$migration_file" 2>/dev/null; then
                    print_error "MongoDB migration $version has syntax errors"
                    ((errors++))
                fi
            fi
        done
    fi

    if [[ $errors -eq 0 ]]; then
        print_status "All migrations are valid"
    else
        print_error "Found $errors validation errors"
        exit 1
    fi
}

# Main script logic
main() {
    local command=${1:-help}
    local dry_run=false
    local force=false
    local verbose=false
    local env="dev"

    # Parse arguments
    shift
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                dry_run=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            --env)
                env="$2"
                shift 2
                ;;
            *)
                # Handle positional arguments for specific commands
                case $command in
                    create)
                        migration_name="$1"
                        shift
                        ;;
                    rollback)
                        rollback_version="$1"
                        shift
                        ;;
                    *)
                        print_error "Unknown option: $1"
                        show_usage
                        exit 1
                        ;;
                esac
                ;;
        esac
    done

    # Load environment configuration
    load_env_config "$env"

    # Execute command
    case $command in
        init)
            check_dependencies
            init_migration_system
            ;;
        status)
            get_migration_status
            ;;
        migrate)
            check_dependencies
            run_postgresql_migrations "$dry_run"
            run_mongodb_migrations "$dry_run"
            ;;
        migrate-postgres)
            check_dependencies
            run_postgresql_migrations "$dry_run"
            ;;
        migrate-mongo)
            check_dependencies
            run_mongodb_migrations "$dry_run"
            ;;
        create)
            create_migration "$migration_name"
            ;;
        validate)
            check_dependencies
            validate_migrations
            ;;
        rollback)
            print_error "Rollback functionality not implemented yet"
            exit 1
            ;;
        help)
            show_usage
            ;;
        *)
            print_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"