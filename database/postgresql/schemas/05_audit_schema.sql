-- Audit and Logging Schema
-- Contains audit trails, system logs, and compliance tracking

-- Main audit log table
CREATE TABLE audit.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_id UUID,
    source_application VARCHAR(50)
);

-- System activity logs
CREATE TABLE audit.system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    log_level VARCHAR(10) NOT NULL CHECK (log_level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')),
    service_name VARCHAR(50) NOT NULL,
    component VARCHAR(100),
    message TEXT NOT NULL,
    error_code VARCHAR(50),
    stack_trace TEXT,
    metadata JSONB DEFAULT '{}',
    user_id UUID REFERENCES auth.users(id),
    session_id UUID,
    request_id UUID,
    ip_address INET,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API access logs
CREATE TABLE audit.api_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    api_key_id UUID REFERENCES auth.api_keys(id),
    method VARCHAR(10) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    request_headers JSONB,
    request_body JSONB,
    response_status INTEGER NOT NULL,
    response_headers JSONB,
    response_body JSONB,
    response_time_ms INTEGER,
    ip_address INET,
    user_agent TEXT,
    request_id UUID,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User activity tracking
CREATE TABLE audit.user_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    activity_description TEXT,
    entity_type VARCHAR(50),
    entity_id UUID,
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Login/logout audit
CREATE TABLE audit.authentication_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    email VARCHAR(255),
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('login_attempt', 'login_success', 'login_failure', 'logout', 'password_reset', 'account_locked', 'account_unlocked')),
    method VARCHAR(20) CHECK (method IN ('password', 'oauth', 'two_factor', 'api_key')),
    ip_address INET,
    user_agent TEXT,
    device_info JSONB,
    location_data JSONB,
    failure_reason VARCHAR(100),
    session_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial data access audit
CREATE TABLE audit.financial_access_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    accessed_user_id UUID REFERENCES auth.users(id),
    access_type VARCHAR(30) NOT NULL CHECK (access_type IN ('view', 'export', 'modify', 'delete')),
    resource_type VARCHAR(50) NOT NULL CHECK (resource_type IN ('account', 'transaction', 'budget', 'goal', 'portfolio', 'report')),
    resource_id UUID,
    data_sensitivity VARCHAR(20) DEFAULT 'normal' CHECK (data_sensitivity IN ('low', 'normal', 'high', 'critical')),
    access_reason TEXT,
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data export tracking
CREATE TABLE audit.data_exports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    export_type VARCHAR(30) NOT NULL CHECK (export_type IN ('full_account', 'transactions', 'budgets', 'reports', 'analytics')),
    format VARCHAR(10) NOT NULL CHECK (format IN ('csv', 'excel', 'pdf', 'json')),
    date_range_start DATE,
    date_range_end DATE,
    filters JSONB DEFAULT '{}',
    record_count INTEGER,
    file_size_bytes BIGINT,
    file_path TEXT,
    download_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance tracking
CREATE TABLE audit.compliance_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    regulation VARCHAR(20) NOT NULL CHECK (regulation IN ('GDPR', 'CCPA', 'SOX', 'PCI_DSS', 'PSD2', 'FISMA')),
    user_id UUID REFERENCES auth.users(id),
    affected_data_types TEXT[],
    event_description TEXT NOT NULL,
    compliance_status VARCHAR(20) DEFAULT 'compliant' CHECK (compliance_status IN ('compliant', 'violation', 'review_required')),
    automated_response BOOLEAN DEFAULT FALSE,
    response_actions JSONB DEFAULT '{}',
    officer_notified BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data retention policies
CREATE TABLE audit.data_retention_policies (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    retention_period INTERVAL NOT NULL,
    archival_required BOOLEAN DEFAULT FALSE,
    deletion_criteria JSONB,
    compliance_requirements TEXT[],
    last_cleanup_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Data cleanup logs
CREATE TABLE audit.data_cleanup_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_id INTEGER REFERENCES audit.data_retention_policies(id),
    table_name VARCHAR(100) NOT NULL,
    cleanup_type VARCHAR(20) NOT NULL CHECK (cleanup_type IN ('archive', 'delete', 'anonymize')),
    records_processed INTEGER NOT NULL,
    records_affected INTEGER NOT NULL,
    cleanup_criteria JSONB,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    error_message TEXT,
    initiated_by VARCHAR(100) NOT NULL
);

-- Security incidents
CREATE TABLE audit.security_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    affected_users UUID[],
    affected_systems TEXT[],
    source_ip INET,
    attack_vector VARCHAR(100),
    indicators_of_compromise JSONB DEFAULT '{}',
    mitigation_actions JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'contained', 'resolved', 'closed')),
    assigned_to UUID REFERENCES auth.users(id),
    reported_by UUID REFERENCES auth.users(id),
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics
CREATE TABLE audit.performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    unit VARCHAR(20),
    service_name VARCHAR(50),
    endpoint VARCHAR(255),
    user_id UUID REFERENCES auth.users(id),
    session_id UUID,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default data retention policies
INSERT INTO audit.data_retention_policies (table_name, retention_period, archival_required, compliance_requirements) VALUES
('audit_log', '7 years', true, ARRAY['SOX', 'FISMA']),
('system_logs', '2 years', true, ARRAY['FISMA']),
('api_logs', '1 year', false, ARRAY['GDPR']),
('user_activities', '3 years', true, ARRAY['GDPR', 'CCPA']),
('authentication_logs', '5 years', true, ARRAY['SOX', 'FISMA']),
('financial_access_logs', '7 years', true, ARRAY['SOX', 'PCI_DSS']),
('performance_metrics', '6 months', false, ARRAY[]::TEXT[]);

-- Performance indexes
CREATE INDEX idx_audit_log_table_name ON audit.audit_log(table_name);
CREATE INDEX idx_audit_log_changed_by ON audit.audit_log(changed_by);
CREATE INDEX idx_audit_log_changed_at ON audit.audit_log(changed_at);
CREATE INDEX idx_audit_log_operation ON audit.audit_log(operation);

CREATE INDEX idx_system_logs_level ON audit.system_logs(log_level);
CREATE INDEX idx_system_logs_service ON audit.system_logs(service_name);
CREATE INDEX idx_system_logs_timestamp ON audit.system_logs(timestamp);
CREATE INDEX idx_system_logs_user_id ON audit.system_logs(user_id);

CREATE INDEX idx_api_logs_user_id ON audit.api_logs(user_id);
CREATE INDEX idx_api_logs_endpoint ON audit.api_logs(endpoint);
CREATE INDEX idx_api_logs_status ON audit.api_logs(response_status);
CREATE INDEX idx_api_logs_created_at ON audit.api_logs(created_at);

CREATE INDEX idx_user_activities_user_id ON audit.user_activities(user_id);
CREATE INDEX idx_user_activities_type ON audit.user_activities(activity_type);
CREATE INDEX idx_user_activities_timestamp ON audit.user_activities(timestamp);

CREATE INDEX idx_auth_logs_user_id ON audit.authentication_logs(user_id);
CREATE INDEX idx_auth_logs_event_type ON audit.authentication_logs(event_type);
CREATE INDEX idx_auth_logs_timestamp ON audit.authentication_logs(timestamp);
CREATE INDEX idx_auth_logs_ip_address ON audit.authentication_logs(ip_address);

CREATE INDEX idx_financial_access_user_id ON audit.financial_access_logs(user_id);
CREATE INDEX idx_financial_access_type ON audit.financial_access_logs(access_type);
CREATE INDEX idx_financial_access_resource ON audit.financial_access_logs(resource_type);
CREATE INDEX idx_financial_access_timestamp ON audit.financial_access_logs(timestamp);

CREATE INDEX idx_data_exports_user_id ON audit.data_exports(user_id);
CREATE INDEX idx_data_exports_type ON audit.data_exports(export_type);
CREATE INDEX idx_data_exports_created_at ON audit.data_exports(created_at);

CREATE INDEX idx_compliance_events_type ON audit.compliance_events(event_type);
CREATE INDEX idx_compliance_events_regulation ON audit.compliance_events(regulation);
CREATE INDEX idx_compliance_events_status ON audit.compliance_events(compliance_status);
CREATE INDEX idx_compliance_events_timestamp ON audit.compliance_events(timestamp);

CREATE INDEX idx_security_incidents_severity ON audit.security_incidents(severity);
CREATE INDEX idx_security_incidents_status ON audit.security_incidents(status);
CREATE INDEX idx_security_incidents_detected_at ON audit.security_incidents(detected_at);

CREATE INDEX idx_performance_metrics_type ON audit.performance_metrics(metric_type);
CREATE INDEX idx_performance_metrics_name ON audit.performance_metrics(metric_name);
CREATE INDEX idx_performance_metrics_timestamp ON audit.performance_metrics(timestamp);
CREATE INDEX idx_performance_metrics_service ON audit.performance_metrics(service_name);

-- Partitioning setup for large tables (optional - can be enabled for high-volume deployments)
-- CREATE TABLE audit.audit_log_y2024 PARTITION OF audit.audit_log
--     FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Update timestamp triggers
CREATE TRIGGER update_security_incidents_updated_at
    BEFORE UPDATE ON audit.security_incidents
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_data_retention_policies_updated_at
    BEFORE UPDATE ON audit.data_retention_policies
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();