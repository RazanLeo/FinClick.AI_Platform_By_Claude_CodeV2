# FinClick.AI Database Infrastructure

This directory contains the complete database infrastructure setup for the FinClick.AI platform, including PostgreSQL, MongoDB, Redis, migration system, backup solutions, and monitoring configurations.

## 📁 Directory Structure

```
database/
├── postgresql/               # PostgreSQL database files
│   ├── init/                # Initialization scripts
│   ├── schemas/             # Database schema definitions
│   ├── functions/           # Stored procedures and functions
│   └── triggers/            # Database triggers
├── mongodb/                 # MongoDB database files
│   ├── init/                # Initialization scripts
│   ├── collections/         # Collection configurations
│   └── indexes/             # Index creation scripts
├── redis/                   # Redis cache configuration
│   ├── config/              # Redis configuration files
│   └── scripts/             # Redis Lua scripts and utilities
├── migrations/              # Database migration system
│   ├── postgresql/          # PostgreSQL migrations
│   ├── mongodb/            # MongoDB migrations
│   └── scripts/            # Migration management scripts
├── backups/                # Backup storage and scripts
├── monitoring/             # Monitoring and alerting configuration
│   ├── grafana/            # Grafana dashboards and datasources
│   └── rules/              # Prometheus alerting rules
├── scripts/                # Utility scripts
└── docker-compose-db.yml  # Docker Compose for database services
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 4GB RAM available for database services
- 20GB+ disk space for data and backups

### Starting the Database Services

1. **Start all database services:**
   ```bash
   docker-compose -f docker-compose-db.yml up -d
   ```

2. **Start with monitoring tools:**
   ```bash
   docker-compose -f docker-compose-db.yml --profile tools --profile monitoring up -d
   ```

3. **Start with backup service:**
   ```bash
   docker-compose -f docker-compose-db.yml --profile backup up -d
   ```

### Service URLs

- **PostgreSQL**: `localhost:5432`
- **MongoDB**: `localhost:27017`
- **Redis**: `localhost:6379`
- **pgAdmin**: `http://localhost:8080`
- **MongoDB Express**: `http://localhost:8081`
- **RedisInsight**: `http://localhost:8001`
- **Grafana**: `http://localhost:3001`
- **Prometheus**: `http://localhost:9090`

### Default Credentials

**PostgreSQL:**
- Database: `finclick_ai_main`
- Username: `finclick_app`
- Password: `FinClick2024SecurePassword!`

**MongoDB:**
- Database: `finclick_ai`
- Username: `finclick_app`
- Password: `FinClick2024SecurePassword!`
- Admin Username: `admin`
- Admin Password: `FinClickAdminPassword2024!`

**Redis:**
- Password: `FinClick2024SecureRedisPassword!`

**Management Tools:**
- pgAdmin: `admin@finclick.ai` / `FinClickAdmin2024!`
- MongoDB Express: `admin` / `FinClickAdmin2024!`
- Grafana: `admin` / `FinClickAdmin2024!`

## 🗄️ Database Schemas

### PostgreSQL Schemas

1. **auth** - User authentication and authorization
   - Users, roles, sessions, API keys
   - OAuth connections and 2FA
   - Password reset and email verification

2. **financial** - Financial data and transactions
   - Accounts, transactions, categories
   - Budgets, goals, portfolios
   - Investment tracking and recurring transactions

3. **analytics** - Analytics and insights
   - Financial insights and patterns
   - Performance metrics and forecasts
   - Reports and benchmarks

4. **notifications** - Notification system
   - Notification types and preferences
   - Delivery tracking and campaigns
   - Push tokens and email templates

5. **audit** - Audit logs and compliance
   - System and user activity logs
   - Security incidents and compliance events
   - Data retention and cleanup policies

### MongoDB Collections

1. **documents** - File storage metadata
2. **analysis_results** - AI/ML analysis results
3. **user_activity_logs** - User activity tracking
4. **file_processing_queue** - Background job processing
5. **ml_training_data** - Machine learning datasets
6. **cache_storage** - Application cache data
7. **system_metrics** - System performance metrics
8. **user_preferences** - User preference settings

## 🔄 Migration System

### Running Migrations

```bash
# Initialize migration system
./migrations/scripts/migrate.sh init

# Check migration status
./migrations/scripts/migrate.sh status

# Run all pending migrations
./migrations/scripts/migrate.sh migrate

# Run PostgreSQL migrations only
./migrations/scripts/migrate.sh migrate-postgres

# Run MongoDB migrations only
./migrations/scripts/migrate.sh migrate-mongo

# Create new migration
./migrations/scripts/migrate.sh create add_new_feature
```

### Migration Files

- PostgreSQL migrations: `migrations/postgresql/YYYYMMDDHHMMSS_description.sql`
- MongoDB migrations: `migrations/mongodb/YYYYMMDDHHMMSS_description.js`

## 💾 Backup System

### Automated Backups

The backup system runs automatically via Docker Compose and creates:
- Daily PostgreSQL dumps (compressed)
- Daily MongoDB exports (compressed)
- Daily Redis snapshots (compressed)
- Backup verification and checksums
- 30-day retention policy

### Manual Backup Operations

```bash
# Run full backup
docker exec finclick-db-backup /backup.sh backup

# Check database health
docker exec finclick-db-backup /backup.sh health

# Clean old backups
docker exec finclick-db-backup /backup.sh cleanup

# Generate backup report
docker exec finclick-db-backup /backup.sh report
```

### Backup Locations

- PostgreSQL: `/backups/postgresql/`
- MongoDB: `/backups/mongodb/`
- Redis: `/backups/redis/`
- Logs: `/backups/logs/`

## 📊 Monitoring and Alerting

### Metrics Collection

- **Prometheus** collects metrics from all database services
- **Grafana** provides visualization dashboards
- **Exporters** for PostgreSQL, MongoDB, and Redis

### Available Dashboards

1. **Database Overview** - High-level metrics for all databases
2. **PostgreSQL Performance** - Detailed PostgreSQL metrics
3. **MongoDB Performance** - MongoDB-specific monitoring
4. **Redis Performance** - Redis cache performance
5. **System Resources** - CPU, memory, disk usage
6. **Backup Status** - Backup success/failure tracking

### Alerting Rules

- Database service down alerts
- High resource usage warnings
- Slow query detection
- Backup failure notifications
- Replication lag alerts
- Security incident notifications

## 🔧 Configuration

### Environment Variables

Create environment-specific configuration files in `migrations/scripts/`:

```bash
# .env.dev
DB_HOST=localhost
DB_PASSWORD=dev_password
MONGO_HOST=localhost
MONGO_PASSWORD=dev_password
REDIS_HOST=localhost
REDIS_PASSWORD=dev_password

# .env.prod
DB_HOST=prod-postgres.example.com
DB_PASSWORD=secure_prod_password
# ... production settings
```

### Security Configuration

1. **Change default passwords** in production
2. **Enable SSL/TLS** for all database connections
3. **Configure firewall rules** to restrict access
4. **Enable audit logging** for compliance
5. **Set up proper user permissions** and role-based access

### Performance Tuning

#### PostgreSQL Optimization

- Configured for 2GB RAM (adjust shared_buffers for your environment)
- Query performance monitoring enabled
- Connection pooling configured
- Index optimization recommendations

#### MongoDB Optimization

- WiredTiger storage engine with compression
- Proper indexing for all collections
- Sharding configuration ready
- Change streams for real-time processing

#### Redis Optimization

- Memory management with LRU eviction
- AOF and RDB persistence
- Sentinel for high availability
- Lua scripts for atomic operations

## 🔍 Troubleshooting

### Common Issues

1. **Database connection failures**
   ```bash
   # Check service status
   docker-compose -f docker-compose-db.yml ps

   # Check logs
   docker-compose -f docker-compose-db.yml logs postgres
   ```

2. **Migration failures**
   ```bash
   # Check migration logs
   ./migrations/scripts/migrate.sh status

   # Validate migration files
   ./migrations/scripts/migrate.sh validate
   ```

3. **Backup failures**
   ```bash
   # Check backup logs
   docker exec finclick-db-backup tail -f /backups/logs/backup_log.csv

   # Test database health
   docker exec finclick-db-backup /backup.sh health
   ```

4. **Performance issues**
   - Check Grafana dashboards for resource usage
   - Review slow query logs
   - Analyze index usage patterns

### Log Locations

- PostgreSQL: `docker logs finclick-postgres`
- MongoDB: `docker logs finclick-mongodb`
- Redis: `docker logs finclick-redis`
- Backup: `./backups/logs/`
- Migration: Console output during execution

## 🛡️ Security Best Practices

1. **Network Security**
   - Use dedicated network for database services
   - Implement proper firewall rules
   - Enable SSL/TLS encryption

2. **Authentication & Authorization**
   - Strong passwords and regular rotation
   - Principle of least privilege
   - Regular security audits

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Secure backup storage
   - Regular security updates

4. **Monitoring & Alerting**
   - Monitor for suspicious activities
   - Set up security incident alerts
   - Regular compliance reviews

## 📝 Maintenance Tasks

### Daily Tasks
- Monitor backup success
- Check system resources
- Review security alerts

### Weekly Tasks
- Analyze slow queries
- Review disk usage trends
- Update monitoring dashboards

### Monthly Tasks
- Security audit review
- Performance optimization review
- Backup restoration testing
- Update database statistics

## 🆘 Support and Documentation

For additional support:

1. Check the monitoring dashboards for system health
2. Review application logs for specific errors
3. Consult the migration system for schema changes
4. Use the backup system for data recovery needs

## 🔄 Updates and Maintenance

To update the database infrastructure:

1. **Update Docker images** in docker-compose-db.yml
2. **Test migrations** in development environment
3. **Update monitoring configurations** as needed
4. **Review and update security settings**
5. **Document any configuration changes**

---

**Note**: Always test configuration changes in a development environment before applying to production. Ensure proper backups are in place before making any structural changes to the database systems.