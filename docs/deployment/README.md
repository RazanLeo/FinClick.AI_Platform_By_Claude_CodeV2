# FinClick.AI Deployment Guide

Comprehensive deployment documentation for the FinClick.AI platform across all environments.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Deployment Process](#deployment-process)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)

## Overview

FinClick.AI is a comprehensive financial analysis platform built with microservices architecture. This guide covers deployment across three environments:

- **Development**: Local development environment
- **Staging**: Pre-production testing environment
- **Production**: Live production environment

### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Frontend      │    │   API Gateway   │
│   (Nginx)       │────│   (React)       │────│   (Node.js)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Microservices │    │   AI Engine     │    │   Financial     │
│   (8 Services)  │    │   (GPT/Gemini)  │    │   Data APIs     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   MongoDB       │    │   Redis Cache   │
│   (Master/Slave)│    │   (Replica Set) │    │   (Cluster)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## System Requirements

### Minimum Requirements

#### Development Environment
- **OS**: Linux, macOS, or Windows with WSL2
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB free space
- **Network**: Broadband internet connection

#### Staging Environment
- **OS**: Linux (Ubuntu 20.04+ or CentOS 8+)
- **CPU**: 8 cores
- **RAM**: 16GB
- **Storage**: 200GB SSD
- **Network**: 100Mbps connection

#### Production Environment
- **OS**: Linux (Ubuntu 20.04+ or CentOS 8+)
- **CPU**: 16+ cores
- **RAM**: 32GB+
- **Storage**: 500GB+ SSD (with backup storage)
- **Network**: 1Gbps+ connection
- **High Availability**: Multiple servers/regions

### Software Requirements

#### Required Software
- Docker 24.0+
- Docker Compose 2.20+
- Git 2.30+
- OpenSSL 1.1+
- curl
- jq

#### Optional Tools
- kubectl (for Kubernetes deployment)
- Helm (for Kubernetes package management)
- Terraform (for infrastructure as code)
- AWS CLI (for AWS deployments)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/finclick/finclick-ai-platform.git
cd finclick-ai-platform
```

### 2. Choose Environment

```bash
# Development
./scripts/deployment/deploy.sh development

# Staging
./scripts/deployment/deploy.sh staging

# Production (requires additional setup)
./scripts/deployment/deploy.sh production
```

### 3. Access Application

- **Development**: http://localhost:3000
- **Staging**: https://staging.finclick.ai
- **Production**: https://finclick.ai

## Environment Setup

### Development Environment

Perfect for local development and testing.

#### Setup Steps

1. **Copy Environment Variables**
   ```bash
   cp .env.development.example .env.development
   # Edit .env.development with your values
   ```

2. **Start Services**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

3. **Initialize Database**
   ```bash
   ./scripts/database/init-dev.sh
   ```

4. **Seed Test Data**
   ```bash
   ./scripts/database/seed-data.sh --environment development
   ```

#### Development Features

- Hot reload for frontend and backend
- Debug ports exposed for debugging
- MailHog for email testing
- Database admin interfaces (pgAdmin, mongo-express)
- Relaxed security settings
- Mock external API responses

#### Access Points

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **pgAdmin**: http://localhost:5050
- **MongoDB Express**: http://localhost:8081
- **Redis Commander**: http://localhost:8082
- **MailHog**: http://localhost:8025
- **Grafana**: http://localhost:3001

### Staging Environment

Mirrors production with test data and relaxed security.

#### Setup Steps

1. **Server Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **SSL Certificates**
   ```bash
   # Using Let's Encrypt
   sudo apt install certbot
   sudo certbot certonly --standalone -d staging.finclick.ai

   # Copy certificates
   sudo cp /etc/letsencrypt/live/staging.finclick.ai/fullchain.pem ./nginx/ssl/
   sudo cp /etc/letsencrypt/live/staging.finclick.ai/privkey.pem ./nginx/ssl/
   ```

3. **Environment Configuration**
   ```bash
   cp .env.staging.example .env.staging
   # Configure staging-specific values
   ```

4. **Deploy**
   ```bash
   ./scripts/deployment/deploy.sh staging --migrate --backup
   ```

#### Staging Features

- Production-like environment
- SSL/TLS encryption
- Monitoring and logging
- Automated backups
- E2E testing capabilities
- Performance monitoring

### Production Environment

High-availability, secure, and optimized for performance.

#### Pre-Deployment Checklist

- [ ] SSL certificates obtained and configured
- [ ] Database clusters set up with replication
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured
- [ ] Security hardening completed
- [ ] Performance testing passed
- [ ] Disaster recovery plan in place

#### Setup Steps

1. **Infrastructure Setup**
   ```bash
   # For AWS deployment
   terraform init
   terraform plan -var-file="production.tfvars"
   terraform apply
   ```

2. **Security Configuration**
   ```bash
   # Generate production secrets
   ./scripts/secrets/manage-secrets.sh init
   ./scripts/secrets/manage-secrets.sh generate jwt_secret --environment production
   ./scripts/secrets/manage-secrets.sh generate database_password --environment production
   ```

3. **SSL Configuration**
   ```bash
   # Configure SSL certificates
   ./scripts/ssl/setup-ssl.sh --domain finclick.ai --environment production
   ```

4. **Database Setup**
   ```bash
   # Initialize production databases
   ./scripts/database/init-production.sh
   ./scripts/database/setup-replication.sh
   ```

5. **Deploy with Blue-Green Strategy**
   ```bash
   ./scripts/deployment/blue-green-deploy.sh production
   ```

#### Production Features

- High availability with load balancing
- Database clustering and replication
- Automated backups and disaster recovery
- Comprehensive monitoring and alerting
- Security scanning and compliance
- Performance optimization
- CDN integration
- Multi-region deployment support

## Deployment Process

### Automated Deployment

Our CI/CD pipeline automatically handles deployments:

1. **Code Push**: Developer pushes code to repository
2. **CI Pipeline**: Tests, builds, and scans for security
3. **Staging Deploy**: Automatic deployment to staging
4. **QA Testing**: Automated and manual testing
5. **Production Deploy**: Manual approval required
6. **Monitoring**: Post-deployment monitoring and alerts

### Manual Deployment

For manual deployments or emergencies:

```bash
# Full deployment with all checks
./scripts/deployment/deploy.sh production \
  --backup \
  --migrate \
  --health-check \
  --rollback-on-failure

# Quick update without recreation
./scripts/deployment/deploy.sh production \
  --update-only \
  --skip-tests

# Rollback to previous version
./scripts/deployment/deploy.sh production \
  --rollback v1.2.0
```

### Deployment Strategies

#### Rolling Deployment (Default)
- Services updated one by one
- Zero downtime
- Gradual traffic migration

#### Blue-Green Deployment
- Complete environment duplication
- Instant traffic switch
- Easy rollback

#### Canary Deployment
- Gradual traffic shifting
- Risk mitigation
- Performance monitoring

## Monitoring & Maintenance

### Monitoring Stack

- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **ELK Stack**: Log aggregation and analysis
- **AlertManager**: Alert routing and notification

### Key Metrics

#### Application Metrics
- Response time (95th percentile)
- Error rate
- Request throughput
- Active users

#### Infrastructure Metrics
- CPU and memory usage
- Disk I/O and space
- Network traffic
- Container health

#### Business Metrics
- User registrations
- Financial analysis requests
- AI processing time
- Revenue metrics

### Health Checks

```bash
# Check overall system health
./scripts/monitoring/health-check.sh --environment production

# Check specific service
./scripts/monitoring/health-check.sh --service api-gateway

# Check database connectivity
./scripts/monitoring/db-health.sh
```

### Maintenance Tasks

#### Daily
- Monitor system health
- Check error logs
- Verify backup completion

#### Weekly
- Review performance metrics
- Update security patches
- Test disaster recovery procedures

#### Monthly
- Rotate secrets and certificates
- Performance optimization review
- Security audit

### Backup and Recovery

#### Automated Backups

```bash
# Full system backup
./scripts/backup/backup.sh --environment production --type full --s3-upload

# Database only backup
./scripts/backup/backup.sh --environment production --type database
```

#### Recovery Procedures

```bash
# Restore from latest backup
./scripts/backup/restore.sh --environment production --latest

# Restore from specific backup
./scripts/backup/restore.sh --environment production --backup backup_20241201_020000.tar.gz
```

## Troubleshooting

### Common Issues

#### Service Won't Start

1. **Check logs**:
   ```bash
   docker-compose logs service-name
   ```

2. **Check resource usage**:
   ```bash
   docker stats
   ```

3. **Verify configuration**:
   ```bash
   docker-compose config
   ```

#### Database Connection Issues

1. **Check database status**:
   ```bash
   docker-compose exec postgres pg_isready
   ```

2. **Test connectivity**:
   ```bash
   docker-compose exec api-gateway npm run db:test
   ```

#### Performance Issues

1. **Check metrics**:
   - Open Grafana dashboard
   - Monitor CPU, memory, and I/O
   - Check response times

2. **Scale services**:
   ```bash
   docker-compose up -d --scale api-gateway=3
   ```

### Log Analysis

#### Application Logs
```bash
# View real-time logs
docker-compose logs -f api-gateway

# Search for errors
docker-compose logs api-gateway | grep ERROR

# Export logs for analysis
docker-compose logs --since 24h > logs.txt
```

#### System Logs
```bash
# Check system logs
journalctl -u docker
systemctl status docker

# Monitor resource usage
htop
iotop
```

### Emergency Procedures

#### Service Recovery
```bash
# Restart failed service
docker-compose restart service-name

# Recreate problematic container
docker-compose up -d --force-recreate service-name
```

#### Database Recovery
```bash
# Restore from backup
./scripts/backup/restore.sh --environment production --database-only

# Rebuild database from replica
./scripts/database/promote-replica.sh
```

#### Complete System Recovery
```bash
# Full system restore
./scripts/disaster-recovery/full-restore.sh --backup-date 2024-12-01
```

## Security Considerations

### Security Best Practices

#### Container Security
- Use non-root users in containers
- Scan images for vulnerabilities
- Keep base images updated
- Implement resource limits

#### Network Security
- Use encrypted communication (HTTPS/TLS)
- Implement proper firewall rules
- Isolate services with Docker networks
- Regular security audits

#### Data Security
- Encrypt data at rest and in transit
- Implement proper access controls
- Regular security patches
- Secure backup storage

#### Secret Management
```bash
# Initialize secrets management
./scripts/secrets/manage-secrets.sh init

# Generate new secret
./scripts/secrets/manage-secrets.sh generate jwt_secret --environment production

# Rotate existing secret
./scripts/secrets/manage-secrets.sh rotate database_password --environment production
```

### Compliance

#### GDPR Compliance
- Data encryption
- Right to be forgotten implementation
- Data processing consent
- Privacy by design

#### SOC 2 Compliance
- Access controls
- Monitoring and logging
- Incident response procedures
- Regular audits

## Performance Optimization

### Database Optimization

#### PostgreSQL
- Connection pooling
- Query optimization
- Index maintenance
- Regular VACUUM operations

#### MongoDB
- Proper indexing
- Aggregation pipeline optimization
- Sharding for scale
- Connection pooling

#### Redis
- Memory optimization
- Appropriate data structures
- TTL management
- Clustering for high availability

### Application Optimization

#### Backend Services
- Code profiling and optimization
- Caching strategies
- Database query optimization
- Async processing

#### Frontend Optimization
- Code splitting
- Bundle optimization
- CDN usage
- Image optimization
- Progressive loading

### Infrastructure Optimization

#### Container Optimization
- Multi-stage builds
- Minimal base images
- Resource limit tuning
- Health check optimization

#### Network Optimization
- CDN configuration
- Load balancer optimization
- Connection pooling
- HTTP/2 implementation

### Monitoring Performance

```bash
# Generate performance report
./scripts/monitoring/performance-report.sh --environment production

# Run load tests
./scripts/testing/load-test.sh --environment staging --concurrent-users 100

# Analyze slow queries
./scripts/database/slow-query-analysis.sh
```

## Getting Help

### Documentation
- [API Documentation](../api/README.md)
- [Database Schema](../database/README.md)
- [Frontend Guide](../frontend/README.md)
- [Security Guide](../security/README.md)

### Support Channels
- **Emergency**: Call the on-call engineer
- **General Issues**: Create a ticket in JIRA
- **Development Questions**: Slack #dev-support
- **Infrastructure Issues**: Slack #infrastructure

### Useful Commands

```bash
# Quick system status
./scripts/monitoring/system-status.sh

# View all service logs
docker-compose logs --tail=100 -f

# Export system configuration
./scripts/utils/export-config.sh

# Generate deployment report
./scripts/utils/deployment-report.sh --environment production
```

---

## Appendix

### Environment Variables Reference
See the complete list of environment variables in:
- [Development Variables](.env.development.example)
- [Staging Variables](.env.staging.example)
- [Production Variables](.env.production.example)

### Port Reference
| Service | Development | Staging | Production |
|---------|------------|---------|------------|
| Frontend | 3000 | 443 | 443 |
| API Gateway | 8000 | 443 | 443 |
| PostgreSQL | 5432 | 5432 | 5432 |
| MongoDB | 27017 | 27017 | 27017 |
| Redis | 6379 | 6379 | 6379 |
| Grafana | 3001 | 443 | 443 |

### Useful Resources
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

---

*Last updated: December 2024*
*Version: 1.0.0*