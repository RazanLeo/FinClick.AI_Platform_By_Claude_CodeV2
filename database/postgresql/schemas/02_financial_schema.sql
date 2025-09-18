-- Financial Data Schema
-- Contains all financial data structures for the FinClick.AI platform

-- Financial institutions/banks
CREATE TABLE financial.institutions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    country_code VARCHAR(3) NOT NULL,
    institution_type VARCHAR(50) NOT NULL CHECK (institution_type IN ('bank', 'credit_union', 'fintech', 'other')),
    api_endpoint TEXT,
    supported_services JSONB DEFAULT '[]',
    logo_url TEXT,
    website_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User financial accounts
CREATE TABLE financial.accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    institution_id INTEGER REFERENCES financial.institutions(id),
    account_name VARCHAR(255) NOT NULL,
    account_number VARCHAR(100),
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('checking', 'savings', 'credit', 'investment', 'loan', 'other')),
    currency VARCHAR(3) DEFAULT 'USD',
    current_balance DECIMAL(15,2),
    available_balance DECIMAL(15,2),
    credit_limit DECIMAL(15,2),
    interest_rate DECIMAL(5,4),
    account_status VARCHAR(20) DEFAULT 'active' CHECK (account_status IN ('active', 'inactive', 'closed', 'frozen')),
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(20) DEFAULT 'pending' CHECK (sync_status IN ('pending', 'syncing', 'success', 'error')),
    sync_error TEXT,
    metadata JSONB DEFAULT '{}',
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial transactions
CREATE TABLE financial.transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES financial.accounts(id) ON DELETE CASCADE,
    external_id VARCHAR(255),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('debit', 'credit', 'transfer', 'fee', 'interest')),
    category_id INTEGER,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    description TEXT,
    merchant_name VARCHAR(255),
    merchant_category VARCHAR(100),
    location JSONB,
    transaction_date DATE NOT NULL,
    posted_date DATE,
    pending BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    tags TEXT[],
    notes TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_pattern JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(account_id, external_id)
);

-- Transaction categories
CREATE TABLE financial.categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES financial.categories(id),
    icon VARCHAR(50),
    color VARCHAR(7),
    description TEXT,
    is_system_category BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User custom categories
CREATE TABLE financial.user_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES financial.categories(id),
    custom_name VARCHAR(100),
    custom_icon VARCHAR(50),
    custom_color VARCHAR(7),
    budget_limit DECIMAL(15,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Budgets
CREATE TABLE financial.budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    budget_type VARCHAR(20) NOT NULL CHECK (budget_type IN ('monthly', 'weekly', 'yearly', 'custom')),
    total_amount DECIMAL(15,2) NOT NULL,
    spent_amount DECIMAL(15,2) DEFAULT 0,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'exceeded')),
    alert_threshold DECIMAL(5,2) DEFAULT 80.00,
    categories INTEGER[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Budget alerts
CREATE TABLE financial.budget_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_id UUID NOT NULL REFERENCES financial.budgets(id) ON DELETE CASCADE,
    alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('threshold', 'exceeded', 'near_end')),
    threshold_percentage DECIMAL(5,2),
    message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Financial goals
CREATE TABLE financial.goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    goal_type VARCHAR(20) NOT NULL CHECK (goal_type IN ('savings', 'debt_payoff', 'investment', 'expense_reduction')),
    target_amount DECIMAL(15,2) NOT NULL,
    current_amount DECIMAL(15,2) DEFAULT 0,
    target_date DATE,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'cancelled')),
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
    auto_contribute BOOLEAN DEFAULT FALSE,
    contribution_amount DECIMAL(15,2),
    contribution_frequency VARCHAR(20) CHECK (contribution_frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Goal contributions
CREATE TABLE financial.goal_contributions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    goal_id UUID NOT NULL REFERENCES financial.goals(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES financial.transactions(id),
    amount DECIMAL(15,2) NOT NULL,
    contribution_date DATE NOT NULL,
    contribution_type VARCHAR(20) NOT NULL CHECK (contribution_type IN ('manual', 'automatic', 'transfer')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Investment portfolios
CREATE TABLE financial.portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    portfolio_type VARCHAR(20) NOT NULL CHECK (portfolio_type IN ('stocks', 'bonds', 'crypto', 'mixed', 'retirement')),
    total_value DECIMAL(15,2) DEFAULT 0,
    initial_investment DECIMAL(15,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    risk_level VARCHAR(20) CHECK (risk_level IN ('conservative', 'moderate', 'aggressive')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Investment holdings
CREATE TABLE financial.holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID NOT NULL REFERENCES financial.portfolios(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(255),
    asset_type VARCHAR(20) NOT NULL CHECK (asset_type IN ('stock', 'bond', 'etf', 'mutual_fund', 'crypto', 'commodity')),
    quantity DECIMAL(18,8) NOT NULL,
    average_cost DECIMAL(15,2),
    current_price DECIMAL(15,2),
    market_value DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'USD',
    purchase_date DATE,
    last_price_update TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Investment transactions
CREATE TABLE financial.investment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID NOT NULL REFERENCES financial.portfolios(id) ON DELETE CASCADE,
    holding_id UUID REFERENCES financial.holdings(id),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('buy', 'sell', 'dividend', 'split', 'transfer')),
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(18,8),
    price DECIMAL(15,2),
    fees DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    transaction_date DATE NOT NULL,
    settlement_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recurring transactions/subscriptions
CREATE TABLE financial.recurring_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    account_id UUID REFERENCES financial.accounts(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly')),
    next_date DATE NOT NULL,
    end_date DATE,
    category_id INTEGER REFERENCES financial.categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    auto_categorize BOOLEAN DEFAULT TRUE,
    merchant_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default categories
INSERT INTO financial.categories (name, parent_id, icon, color, is_system_category) VALUES
('Income', NULL, 'income', '#4CAF50', TRUE),
('Salary', 1, 'salary', '#4CAF50', TRUE),
('Freelance', 1, 'freelance', '#4CAF50', TRUE),
('Investment Income', 1, 'investment', '#4CAF50', TRUE),
('Expenses', NULL, 'expenses', '#F44336', TRUE),
('Food & Dining', 4, 'restaurant', '#FF9800', TRUE),
('Shopping', 4, 'shopping', '#E91E63', TRUE),
('Transportation', 4, 'car', '#2196F3', TRUE),
('Bills & Utilities', 4, 'bill', '#9C27B0', TRUE),
('Entertainment', 4, 'entertainment', '#FF5722', TRUE),
('Healthcare', 4, 'health', '#009688', TRUE),
('Education', 4, 'education', '#795548', TRUE),
('Travel', 4, 'travel', '#607D8B', TRUE),
('Insurance', 4, 'insurance', '#3F51B5', TRUE),
('Taxes', 4, 'tax', '#FFC107', TRUE);

-- Performance indexes
CREATE INDEX idx_accounts_user_id ON financial.accounts(user_id);
CREATE INDEX idx_accounts_institution_id ON financial.accounts(institution_id);
CREATE INDEX idx_accounts_status ON financial.accounts(account_status);
CREATE INDEX idx_accounts_sync_status ON financial.accounts(sync_status);

CREATE INDEX idx_transactions_account_id ON financial.transactions(account_id);
CREATE INDEX idx_transactions_date ON financial.transactions(transaction_date);
CREATE INDEX idx_transactions_amount ON financial.transactions(amount);
CREATE INDEX idx_transactions_category ON financial.transactions(category_id);
CREATE INDEX idx_transactions_type ON financial.transactions(transaction_type);
CREATE INDEX idx_transactions_pending ON financial.transactions(pending);
CREATE INDEX idx_transactions_merchant ON financial.transactions(merchant_name);
CREATE INDEX idx_transactions_external_id ON financial.transactions(external_id);

CREATE INDEX idx_budgets_user_id ON financial.budgets(user_id);
CREATE INDEX idx_budgets_status ON financial.budgets(status);
CREATE INDEX idx_budgets_dates ON financial.budgets(start_date, end_date);

CREATE INDEX idx_goals_user_id ON financial.goals(user_id);
CREATE INDEX idx_goals_status ON financial.goals(status);
CREATE INDEX idx_goals_type ON financial.goals(goal_type);

CREATE INDEX idx_portfolios_user_id ON financial.portfolios(user_id);
CREATE INDEX idx_holdings_portfolio_id ON financial.holdings(portfolio_id);
CREATE INDEX idx_holdings_symbol ON financial.holdings(symbol);

-- Update timestamp triggers
CREATE TRIGGER update_accounts_updated_at
    BEFORE UPDATE ON financial.accounts
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON financial.transactions
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_budgets_updated_at
    BEFORE UPDATE ON financial.budgets
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

CREATE TRIGGER update_goals_updated_at
    BEFORE UPDATE ON financial.goals
    FOR EACH ROW EXECUTE FUNCTION auth.update_updated_at_column();

-- Audit triggers for critical tables
CREATE TRIGGER audit_accounts_trigger
    AFTER INSERT OR UPDATE OR DELETE ON financial.accounts
    FOR EACH ROW EXECUTE FUNCTION audit.audit_trigger_function();

CREATE TRIGGER audit_transactions_trigger
    AFTER INSERT OR UPDATE OR DELETE ON financial.transactions
    FOR EACH ROW EXECUTE FUNCTION audit.audit_trigger_function();