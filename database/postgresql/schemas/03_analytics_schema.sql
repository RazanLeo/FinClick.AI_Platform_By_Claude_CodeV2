-- Analytics and Reporting Schema
-- Contains data structures for analytics, insights, and reporting

-- Financial insights and analysis results
CREATE TABLE analytics.insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL CHECK (insight_type IN ('spending_pattern', 'budget_analysis', 'goal_progress', 'investment_performance', 'cash_flow', 'anomaly_detection')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20) DEFAULT 'info' CHECK (severity IN ('low', 'medium', 'high', 'critical', 'info')),
    confidence_score DECIMAL(3,2) CHECK (confidence_score BETWEEN 0 AND 1),
    data_points JSONB NOT NULL,
    recommendations JSONB DEFAULT '[]',
    action_items JSONB DEFAULT '[]',
    affected_accounts UUID[],
    affected_categories INTEGER[],
    time_period_start DATE,
    time_period_end DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'dismissed', 'resolved')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User engagement with insights
CREATE TABLE analytics.insight_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_id UUID NOT NULL REFERENCES analytics.insights(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    interaction_type VARCHAR(30) NOT NULL CHECK (interaction_type IN ('viewed', 'acknowledged', 'dismissed', 'shared', 'action_taken')),
    interaction_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Spending analysis patterns
CREATE TABLE analytics.spending_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    pattern_type VARCHAR(30) NOT NULL CHECK (pattern_type IN ('monthly', 'weekly', 'daily', 'seasonal', 'category_trend')),
    category_id INTEGER REFERENCES financial.categories(id),
    time_period VARCHAR(20) NOT NULL,
    average_amount DECIMAL(15,2),
    trend_direction VARCHAR(10) CHECK (trend_direction IN ('up', 'down', 'stable')),
    trend_percentage DECIMAL(5,2),
    pattern_data JSONB NOT NULL,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial health scores
CREATE TABLE analytics.financial_health_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    overall_score INTEGER CHECK (overall_score BETWEEN 0 AND 100),
    cash_flow_score INTEGER CHECK (cash_flow_score BETWEEN 0 AND 100),
    debt_score INTEGER CHECK (debt_score BETWEEN 0 AND 100),
    savings_score INTEGER CHECK (savings_score BETWEEN 0 AND 100),
    investment_score INTEGER CHECK (investment_score BETWEEN 0 AND 100),
    budget_adherence_score INTEGER CHECK (budget_adherence_score BETWEEN 0 AND 100),
    score_factors JSONB NOT NULL,
    improvement_areas JSONB DEFAULT '[]',
    strengths JSONB DEFAULT '[]',
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Budget performance analytics
CREATE TABLE analytics.budget_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_id UUID NOT NULL REFERENCES financial.budgets(id) ON DELETE CASCADE,
    analysis_period_start DATE NOT NULL,
    analysis_period_end DATE NOT NULL,
    budgeted_amount DECIMAL(15,2) NOT NULL,
    actual_amount DECIMAL(15,2) NOT NULL,
    variance_amount DECIMAL(15,2) NOT NULL,
    variance_percentage DECIMAL(5,2) NOT NULL,
    performance_rating VARCHAR(20) CHECK (performance_rating IN ('excellent', 'good', 'fair', 'poor', 'exceeded')),
    category_breakdown JSONB DEFAULT '{}',
    daily_spending_pattern JSONB DEFAULT '{}',
    recommendations JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Goal progress tracking
CREATE TABLE analytics.goal_progress_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    goal_id UUID NOT NULL REFERENCES financial.goals(id) ON DELETE CASCADE,
    tracking_date DATE NOT NULL,
    current_amount DECIMAL(15,2) NOT NULL,
    target_amount DECIMAL(15,2) NOT NULL,
    progress_percentage DECIMAL(5,2) NOT NULL,
    projected_completion_date DATE,
    monthly_contribution_needed DECIMAL(15,2),
    on_track BOOLEAN NOT NULL,
    variance_from_plan DECIMAL(15,2),
    recommendations JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(goal_id, tracking_date)
);

-- Investment performance analytics
CREATE TABLE analytics.investment_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID NOT NULL REFERENCES financial.portfolios(id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL,
    total_value DECIMAL(15,2) NOT NULL,
    total_cost DECIMAL(15,2) NOT NULL,
    unrealized_gain_loss DECIMAL(15,2) NOT NULL,
    realized_gain_loss DECIMAL(15,2) DEFAULT 0,
    total_return DECIMAL(15,2) NOT NULL,
    return_percentage DECIMAL(8,4) NOT NULL,
    annualized_return DECIMAL(8,4),
    volatility DECIMAL(8,4),
    sharpe_ratio DECIMAL(8,4),
    asset_allocation JSONB NOT NULL,
    performance_attribution JSONB DEFAULT '{}',
    benchmark_comparison JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(portfolio_id, analysis_date)
);

-- Cash flow analysis
CREATE TABLE analytics.cash_flow_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_period_start DATE NOT NULL,
    analysis_period_end DATE NOT NULL,
    total_inflow DECIMAL(15,2) NOT NULL DEFAULT 0,
    total_outflow DECIMAL(15,2) NOT NULL DEFAULT 0,
    net_cash_flow DECIMAL(15,2) NOT NULL DEFAULT 0,
    average_daily_balance DECIMAL(15,2),
    category_breakdown JSONB NOT NULL DEFAULT '{}',
    monthly_pattern JSONB NOT NULL DEFAULT '{}',
    income_stability_score INTEGER CHECK (income_stability_score BETWEEN 0 AND 100),
    expense_predictability_score INTEGER CHECK (expense_predictability_score BETWEEN 0 AND 100),
    cash_flow_health VARCHAR(20) CHECK (cash_flow_health IN ('excellent', 'good', 'warning', 'critical')),
    recommendations JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, analysis_period_start, analysis_period_end)
);

-- Anomaly detection results
CREATE TABLE analytics.anomaly_detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES financial.transactions(id),
    account_id UUID REFERENCES financial.accounts(id),
    anomaly_type VARCHAR(50) NOT NULL CHECK (anomaly_type IN ('unusual_spending', 'suspicious_transaction', 'budget_deviation', 'income_anomaly', 'merchant_anomaly')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    anomaly_details JSONB NOT NULL,
    expected_value DECIMAL(15,2),
    actual_value DECIMAL(15,2),
    deviation_percentage DECIMAL(5,2),
    context_data JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'false_positive', 'confirmed', 'resolved')),
    reviewed_by UUID REFERENCES auth.users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    review_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Predictive models and forecasts
CREATE TABLE analytics.forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    forecast_type VARCHAR(50) NOT NULL CHECK (forecast_type IN ('spending_forecast', 'income_forecast', 'balance_forecast', 'goal_projection', 'budget_forecast')),
    model_type VARCHAR(30) NOT NULL,
    forecast_period_start DATE NOT NULL,
    forecast_period_end DATE NOT NULL,
    baseline_data JSONB NOT NULL,
    forecast_data JSONB NOT NULL,
    confidence_interval JSONB DEFAULT '{}',
    model_accuracy DECIMAL(5,2),
    assumptions JSONB DEFAULT '{}',
    external_factors JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Report templates and configurations
CREATE TABLE analytics.report_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('monthly_summary', 'budget_analysis', 'investment_summary', 'cash_flow_report', 'custom')),
    template_config JSONB NOT NULL,
    filters JSONB DEFAULT '{}',
    schedule_config JSONB DEFAULT '{}',
    is_system_template BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated reports
CREATE TABLE analytics.generated_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES analytics.report_templates(id),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    report_name VARCHAR(255) NOT NULL,
    report_period_start DATE NOT NULL,
    report_period_end DATE NOT NULL,
    report_data JSONB NOT NULL,
    file_path TEXT,
    file_format VARCHAR(10) CHECK (file_format IN ('pdf', 'excel', 'csv', 'json')),
    generation_status VARCHAR(20) DEFAULT 'pending' CHECK (generation_status IN ('pending', 'generating', 'completed', 'failed')),
    error_message TEXT,
    generated_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Benchmark data for comparisons
CREATE TABLE analytics.benchmarks (
    id SERIAL PRIMARY KEY,
    benchmark_type VARCHAR(50) NOT NULL CHECK (benchmark_type IN ('spending_category', 'savings_rate', 'investment_return', 'debt_ratio')),
    category VARCHAR(100),
    demographic_filter JSONB DEFAULT '{}',
    period_type VARCHAR(20) NOT NULL CHECK (period_type IN ('monthly', 'quarterly', 'yearly')),
    percentile_25 DECIMAL(15,2),
    percentile_50 DECIMAL(15,2),
    percentile_75 DECIMAL(15,2),
    average_value DECIMAL(15,2),
    sample_size INTEGER,
    data_source VARCHAR(100),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_insights_user_id ON analytics.insights(user_id);
CREATE INDEX idx_insights_type ON analytics.insights(insight_type);
CREATE INDEX idx_insights_status ON analytics.insights(status);
CREATE INDEX idx_insights_severity ON analytics.insights(severity);
CREATE INDEX idx_insights_created_at ON analytics.insights(created_at);

CREATE INDEX idx_spending_patterns_user_id ON analytics.spending_patterns(user_id);
CREATE INDEX idx_spending_patterns_type ON analytics.spending_patterns(pattern_type);
CREATE INDEX idx_spending_patterns_category ON analytics.spending_patterns(category_id);

CREATE INDEX idx_health_scores_user_id ON analytics.financial_health_scores(user_id);
CREATE INDEX idx_health_scores_calculated_at ON analytics.financial_health_scores(calculated_at);

CREATE INDEX idx_budget_performance_budget_id ON analytics.budget_performance(budget_id);
CREATE INDEX idx_goal_progress_goal_id ON analytics.goal_progress_tracking(goal_id);
CREATE INDEX idx_goal_progress_date ON analytics.goal_progress_tracking(tracking_date);

CREATE INDEX idx_investment_performance_portfolio_id ON analytics.investment_performance(portfolio_id);
CREATE INDEX idx_investment_performance_date ON analytics.investment_performance(analysis_date);

CREATE INDEX idx_cash_flow_user_id ON analytics.cash_flow_analysis(user_id);
CREATE INDEX idx_cash_flow_period ON analytics.cash_flow_analysis(analysis_period_start, analysis_period_end);

CREATE INDEX idx_anomalies_user_id ON analytics.anomaly_detections(user_id);
CREATE INDEX idx_anomalies_type ON analytics.anomaly_detections(anomaly_type);
CREATE INDEX idx_anomalies_severity ON analytics.anomaly_detections(severity);
CREATE INDEX idx_anomalies_status ON analytics.anomaly_detections(status);

CREATE INDEX idx_forecasts_user_id ON analytics.forecasts(user_id);
CREATE INDEX idx_forecasts_type ON analytics.forecasts(forecast_type);

CREATE INDEX idx_reports_user_id ON analytics.generated_reports(user_id);
CREATE INDEX idx_reports_template_id ON analytics.generated_reports(template_id);
CREATE INDEX idx_reports_status ON analytics.generated_reports(generation_status);

-- Update timestamp triggers
CREATE TRIGGER update_insights_updated_at
    BEFORE UPDATE ON analytics.insights
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_report_templates_updated_at
    BEFORE UPDATE ON analytics.report_templates
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();