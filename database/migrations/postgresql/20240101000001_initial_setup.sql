-- Migration: Initial Database Setup
-- Created: 2024-01-01
-- Version: 20240101000001_initial_setup
-- Description: Creates the initial database structure with all schemas and core tables

BEGIN;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create custom schemas
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS financial;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS notifications;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create audit function for tracking changes
CREATE OR REPLACE FUNCTION audit.audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit.audit_log (
            table_name,
            operation,
            old_data,
            changed_by,
            changed_at
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            row_to_json(OLD),
            current_user,
            NOW()
        );
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit.audit_log (
            table_name,
            operation,
            old_data,
            new_data,
            changed_by,
            changed_at
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            row_to_json(OLD),
            row_to_json(NEW),
            current_user,
            NOW()
        );
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit.audit_log (
            table_name,
            operation,
            new_data,
            changed_by,
            changed_at
        ) VALUES (
            TG_TABLE_NAME,
            TG_OP,
            row_to_json(NEW),
            current_user,
            NOW()
        );
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION auth.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Grant schema permissions to application user
GRANT USAGE ON SCHEMA auth TO finclick_app;
GRANT USAGE ON SCHEMA financial TO finclick_app;
GRANT USAGE ON SCHEMA analytics TO finclick_app;
GRANT USAGE ON SCHEMA notifications TO finclick_app;
GRANT USAGE ON SCHEMA audit TO finclick_app;

GRANT CREATE ON SCHEMA auth TO finclick_app;
GRANT CREATE ON SCHEMA financial TO finclick_app;
GRANT CREATE ON SCHEMA analytics TO finclick_app;
GRANT CREATE ON SCHEMA notifications TO finclick_app;
GRANT CREATE ON SCHEMA audit TO finclick_app;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO finclick_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA financial GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO finclick_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO finclick_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA notifications GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO finclick_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT SELECT, INSERT ON TABLES TO finclick_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth GRANT USAGE ON SEQUENCES TO finclick_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA financial GRANT USAGE ON SEQUENCES TO finclick_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT USAGE ON SEQUENCES TO finclick_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA notifications GRANT USAGE ON SEQUENCES TO finclick_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT USAGE ON SEQUENCES TO finclick_app;

COMMIT;