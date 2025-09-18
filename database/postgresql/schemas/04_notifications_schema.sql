-- Notifications and Communications Schema
-- Contains structures for notifications, alerts, and communication management

-- Notification types and templates
CREATE TABLE notifications.notification_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('security', 'financial', 'budget', 'goal', 'system', 'marketing')),
    description TEXT,
    default_enabled BOOLEAN DEFAULT TRUE,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    can_disable BOOLEAN DEFAULT TRUE,
    template_subject VARCHAR(255),
    template_body TEXT,
    template_variables JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User notification preferences
CREATE TABLE notifications.user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    notification_type_id INTEGER NOT NULL REFERENCES notifications.notification_types(id),
    email_enabled BOOLEAN DEFAULT TRUE,
    push_enabled BOOLEAN DEFAULT TRUE,
    sms_enabled BOOLEAN DEFAULT FALSE,
    in_app_enabled BOOLEAN DEFAULT TRUE,
    frequency VARCHAR(20) DEFAULT 'immediate' CHECK (frequency IN ('immediate', 'daily', 'weekly', 'monthly', 'disabled')),
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, notification_type_id)
);

-- Notifications queue and delivery
CREATE TABLE notifications.notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    notification_type_id INTEGER NOT NULL REFERENCES notifications.notification_types(id),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    channels VARCHAR(20)[] DEFAULT ARRAY['in_app'],
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'read', 'failed', 'cancelled')),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    action_url TEXT,
    action_label VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification delivery tracking
CREATE TABLE notifications.delivery_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_id UUID NOT NULL REFERENCES notifications.notifications(id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('email', 'push', 'sms', 'in_app')),
    recipient VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'bounced')),
    external_id VARCHAR(255),
    response_data JSONB DEFAULT '{}',
    error_code VARCHAR(50),
    error_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email templates
CREATE TABLE notifications.email_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    notification_type_id INTEGER REFERENCES notifications.notification_types(id),
    name VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    html_body TEXT NOT NULL,
    text_body TEXT,
    variables JSONB DEFAULT '{}',
    locale VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Push notification tokens
CREATE TABLE notifications.push_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('ios', 'android', 'web')),
    token VARCHAR(500) NOT NULL,
    device_info JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(device_id, user_id)
);

-- Bulk notification campaigns
CREATE TABLE notifications.campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(30) NOT NULL CHECK (campaign_type IN ('promotional', 'announcement', 'educational', 'alert')),
    target_audience JSONB NOT NULL,
    notification_type_id INTEGER REFERENCES notifications.notification_types(id),
    template_id UUID REFERENCES notifications.email_templates(id),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'scheduled', 'running', 'completed', 'cancelled', 'failed')),
    total_recipients INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Campaign recipients tracking
CREATE TABLE notifications.campaign_recipients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES notifications.campaigns(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    notification_id UUID REFERENCES notifications.notifications(id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'skipped')),
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(campaign_id, user_id)
);

-- Notification rules and automation
CREATE TABLE notifications.notification_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50) NOT NULL CHECK (trigger_type IN ('transaction', 'budget_threshold', 'goal_milestone', 'account_balance', 'anomaly_detected', 'scheduled')),
    conditions JSONB NOT NULL,
    notification_type_id INTEGER NOT NULL REFERENCES notifications.notification_types(id),
    is_active BOOLEAN DEFAULT TRUE,
    user_id UUID REFERENCES auth.users(id),
    applies_to_all_users BOOLEAN DEFAULT FALSE,
    priority_override VARCHAR(20) CHECK (priority_override IN ('low', 'medium', 'high', 'urgent')),
    cooldown_period INTERVAL DEFAULT '1 hour',
    max_per_day INTEGER DEFAULT 10,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rule execution log
CREATE TABLE notifications.rule_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID NOT NULL REFERENCES notifications.notification_rules(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    trigger_data JSONB NOT NULL,
    conditions_met BOOLEAN NOT NULL,
    notification_created BOOLEAN DEFAULT FALSE,
    notification_id UUID REFERENCES notifications.notifications(id),
    execution_time_ms INTEGER,
    error_message TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Unsubscribe tracking
CREATE TABLE notifications.unsubscribes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    notification_type_id INTEGER REFERENCES notifications.notification_types(id),
    channel VARCHAR(20) CHECK (channel IN ('email', 'push', 'sms', 'in_app')),
    reason VARCHAR(100),
    feedback TEXT,
    unsubscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, notification_type_id, channel)
);

-- Insert default notification types
INSERT INTO notifications.notification_types (name, category, description, priority, template_subject, template_body) VALUES
-- Security notifications
('login_successful', 'security', 'Successful login notification', 'low', 'Successful Login to FinClick.AI', 'You have successfully logged into your FinClick.AI account from {{device}} at {{timestamp}}.'),
('login_failed', 'security', 'Failed login attempt notification', 'medium', 'Failed Login Attempt', 'Someone attempted to log into your FinClick.AI account from {{device}} at {{timestamp}}.'),
('password_changed', 'security', 'Password change notification', 'high', 'Password Changed', 'Your FinClick.AI password was successfully changed.'),
('two_factor_enabled', 'security', 'Two-factor authentication enabled', 'medium', '2FA Enabled', 'Two-factor authentication has been enabled for your account.'),

-- Financial notifications
('transaction_created', 'financial', 'New transaction notification', 'low', 'New Transaction', 'A new {{transaction_type}} transaction of {{amount}} was recorded in your {{account_name}} account.'),
('large_transaction', 'financial', 'Large transaction alert', 'medium', 'Large Transaction Alert', 'A large transaction of {{amount}} was detected in your {{account_name}} account.'),
('account_sync_failed', 'financial', 'Account synchronization failed', 'medium', 'Account Sync Failed', 'We were unable to sync your {{account_name}} account. Please check your connection.'),
('low_balance_alert', 'financial', 'Low account balance warning', 'high', 'Low Balance Alert', 'Your {{account_name}} account balance is running low: {{balance}}.'),

-- Budget notifications
('budget_threshold_warning', 'budget', 'Budget threshold warning', 'medium', 'Budget Warning', 'You have spent {{percentage}}% of your {{budget_name}} budget.'),
('budget_exceeded', 'budget', 'Budget exceeded alert', 'high', 'Budget Exceeded', 'You have exceeded your {{budget_name}} budget by {{amount}}.'),
('budget_created', 'budget', 'New budget created', 'low', 'Budget Created', 'Your new budget "{{budget_name}}" has been created successfully.'),

-- Goal notifications
('goal_milestone', 'goal', 'Goal milestone reached', 'medium', 'Goal Milestone Reached!', 'Congratulations! You have reached {{percentage}}% of your goal "{{goal_name}}".'),
('goal_completed', 'goal', 'Goal completed', 'high', 'Goal Completed!', 'Congratulations! You have successfully completed your goal "{{goal_name}}".'),
('goal_deadline_approaching', 'goal', 'Goal deadline approaching', 'medium', 'Goal Deadline Approaching', 'Your goal "{{goal_name}}" deadline is approaching in {{days}} days.'),

-- System notifications
('account_created', 'system', 'Account created successfully', 'low', 'Welcome to FinClick.AI!', 'Your FinClick.AI account has been created successfully.'),
('maintenance_scheduled', 'system', 'Scheduled maintenance notification', 'medium', 'Scheduled Maintenance', 'FinClick.AI will undergo maintenance on {{date}} from {{start_time}} to {{end_time}}.'),
('feature_announcement', 'system', 'New feature announcement', 'low', 'New Feature Available', 'We have released a new feature: {{feature_name}}. {{description}}'),

-- Marketing notifications
('weekly_summary', 'marketing', 'Weekly financial summary', 'low', 'Your Weekly Financial Summary', 'Here is your weekly financial summary for {{week_ending}}.'),
('monthly_report', 'marketing', 'Monthly financial report', 'low', 'Your Monthly Financial Report', 'Your monthly financial report for {{month}} is ready.'),
('tips_and_insights', 'marketing', 'Financial tips and insights', 'low', 'Financial Tip', 'Here is a financial tip to help improve your financial health: {{tip}}');

-- Performance indexes
CREATE INDEX idx_notifications_user_id ON notifications.notifications(user_id);
CREATE INDEX idx_notifications_type_id ON notifications.notifications(notification_type_id);
CREATE INDEX idx_notifications_status ON notifications.notifications(status);
CREATE INDEX idx_notifications_priority ON notifications.notifications(priority);
CREATE INDEX idx_notifications_scheduled_at ON notifications.notifications(scheduled_at);
CREATE INDEX idx_notifications_created_at ON notifications.notifications(created_at);
CREATE INDEX idx_notifications_channels ON notifications.notifications USING GIN(channels);

CREATE INDEX idx_user_preferences_user_id ON notifications.user_preferences(user_id);
CREATE INDEX idx_delivery_log_notification_id ON notifications.delivery_log(notification_id);
CREATE INDEX idx_delivery_log_channel ON notifications.delivery_log(channel);
CREATE INDEX idx_delivery_log_status ON notifications.delivery_log(status);

CREATE INDEX idx_push_tokens_user_id ON notifications.push_tokens(user_id);
CREATE INDEX idx_push_tokens_device_id ON notifications.push_tokens(device_id);
CREATE INDEX idx_push_tokens_active ON notifications.push_tokens(is_active);

CREATE INDEX idx_campaigns_status ON notifications.campaigns(status);
CREATE INDEX idx_campaign_recipients_campaign_id ON notifications.campaign_recipients(campaign_id);
CREATE INDEX idx_campaign_recipients_user_id ON notifications.campaign_recipients(user_id);

CREATE INDEX idx_notification_rules_active ON notifications.notification_rules(is_active);
CREATE INDEX idx_notification_rules_trigger_type ON notifications.notification_rules(trigger_type);
CREATE INDEX idx_rule_executions_rule_id ON notifications.rule_executions(rule_id);
CREATE INDEX idx_rule_executions_user_id ON notifications.rule_executions(user_id);

-- Update timestamp triggers
CREATE TRIGGER update_notification_types_updated_at
    BEFORE UPDATE ON notifications.notification_types
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON notifications.user_preferences
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_notifications_updated_at
    BEFORE UPDATE ON notifications.notifications
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_push_tokens_updated_at
    BEFORE UPDATE ON notifications.push_tokens
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at
    BEFORE UPDATE ON notifications.campaigns
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_notification_rules_updated_at
    BEFORE UPDATE ON notifications.notification_rules
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();