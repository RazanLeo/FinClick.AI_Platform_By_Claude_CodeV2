#!/bin/bash

# Redis Setup Script for FinClick.AI Platform
# This script sets up Redis with proper security and performance configurations

set -e

echo "Setting up Redis for FinClick.AI Platform..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_warning "Running as root. Consider running as a dedicated redis user."
fi

# Install Redis if not present
install_redis() {
    print_status "Checking Redis installation..."

    if ! command -v redis-server &> /dev/null; then
        print_status "Redis not found. Installing Redis..."

        # Detect OS and install accordingly
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y redis-server
            elif command -v yum &> /dev/null; then
                sudo yum install -y redis
            else
                print_error "Unsupported Linux distribution"
                exit 1
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            if command -v brew &> /dev/null; then
                brew install redis
            else
                print_error "Homebrew not found. Please install Homebrew first."
                exit 1
            fi
        else
            print_error "Unsupported operating system"
            exit 1
        fi
    else
        print_status "Redis is already installed"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating Redis directories..."

    sudo mkdir -p /etc/redis
    sudo mkdir -p /var/lib/redis
    sudo mkdir -p /var/log/redis
    sudo mkdir -p /var/lib/redis-sentinel
    sudo mkdir -p /var/log/redis-sentinel

    # Set proper permissions
    if id "redis" &>/dev/null; then
        sudo chown redis:redis /var/lib/redis
        sudo chown redis:redis /var/log/redis
        sudo chown redis:redis /var/lib/redis-sentinel
        sudo chown redis:redis /var/log/redis-sentinel
    else
        print_warning "Redis user not found. You may need to create it manually."
    fi

    sudo chmod 750 /var/lib/redis
    sudo chmod 750 /var/lib/redis-sentinel
}

# Copy configuration files
setup_configuration() {
    print_status "Setting up Redis configuration..."

    # Get the directory of this script
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    CONFIG_DIR="$(dirname "$SCRIPT_DIR")/config"

    # Copy main Redis configuration
    if [[ -f "$CONFIG_DIR/redis.conf" ]]; then
        sudo cp "$CONFIG_DIR/redis.conf" /etc/redis/redis.conf
        sudo chmod 640 /etc/redis/redis.conf
        if id "redis" &>/dev/null; then
            sudo chown redis:redis /etc/redis/redis.conf
        fi
        print_status "Redis configuration copied to /etc/redis/redis.conf"
    else
        print_error "Redis configuration file not found at $CONFIG_DIR/redis.conf"
        exit 1
    fi

    # Copy Sentinel configuration
    if [[ -f "$CONFIG_DIR/redis-sentinel.conf" ]]; then
        sudo cp "$CONFIG_DIR/redis-sentinel.conf" /etc/redis/sentinel.conf
        sudo chmod 640 /etc/redis/sentinel.conf
        if id "redis" &>/dev/null; then
            sudo chown redis:redis /etc/redis/sentinel.conf
        fi
        print_status "Sentinel configuration copied to /etc/redis/sentinel.conf"
    else
        print_warning "Sentinel configuration file not found. Skipping sentinel setup."
    fi
}

# Setup systemd services
setup_systemd_services() {
    print_status "Setting up systemd services..."

    # Redis service
    cat > /tmp/redis.service << 'EOF'
[Unit]
Description=Advanced key-value store for FinClick.AI
After=network.target
Documentation=http://redis.io/documentation, man:redis-server(1)

[Service]
Type=notify
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf
ExecStop=/bin/kill -s QUIT $MAINPID
ExecReload=/bin/kill -s HUP $MAINPID
TimeoutStopSec=0
Restart=always
User=redis
Group=redis
RuntimeDirectory=redis
RuntimeDirectoryMode=0755

UMask=007
PrivateTmp=yes
LimitNOFILE=65535
PrivateDevices=yes
ProtectHome=yes
ReadOnlyDirectories=/
ReadWriteDirectories=-/var/lib/redis
ReadWriteDirectories=-/var/log/redis
ReadWriteDirectories=-/var/run/redis

NoNewPrivileges=true
CapabilityBoundingSet=CAP_SETGID CAP_SETUID CAP_SYS_RESOURCE
MemoryDenyWriteExecute=true
ProtectKernelModules=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true
LockPersonality=true

[Install]
WantedBy=multi-user.target
EOF

    sudo mv /tmp/redis.service /etc/systemd/system/redis.service

    # Redis Sentinel service
    cat > /tmp/redis-sentinel.service << 'EOF'
[Unit]
Description=Redis Sentinel for FinClick.AI
After=network.target
Documentation=http://redis.io/topics/sentinel

[Service]
Type=notify
ExecStart=/usr/bin/redis-sentinel /etc/redis/sentinel.conf
ExecStop=/bin/kill -s QUIT $MAINPID
TimeoutStopSec=0
Restart=always
User=redis
Group=redis
RuntimeDirectory=redis-sentinel
RuntimeDirectoryMode=0755

UMask=007
PrivateTmp=yes
LimitNOFILE=65535
PrivateDevices=yes
ProtectHome=yes
ReadOnlyDirectories=/
ReadWriteDirectories=-/var/lib/redis-sentinel
ReadWriteDirectories=-/var/log/redis-sentinel

NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

    sudo mv /tmp/redis-sentinel.service /etc/systemd/system/redis-sentinel.service

    # Reload systemd
    sudo systemctl daemon-reload

    print_status "Systemd services created"
}

# Configure firewall
configure_firewall() {
    print_status "Configuring firewall for Redis..."

    if command -v ufw &> /dev/null; then
        # UFW (Ubuntu)
        sudo ufw allow 6379/tcp comment "Redis"
        sudo ufw allow 26379/tcp comment "Redis Sentinel"
        print_status "UFW rules added for Redis"
    elif command -v firewall-cmd &> /dev/null; then
        # FirewallD (CentOS/RHEL)
        sudo firewall-cmd --permanent --add-port=6379/tcp
        sudo firewall-cmd --permanent --add-port=26379/tcp
        sudo firewall-cmd --reload
        print_status "FirewallD rules added for Redis"
    else
        print_warning "No supported firewall found. Please configure manually."
    fi
}

# Optimize system parameters
optimize_system() {
    print_status "Optimizing system parameters for Redis..."

    # Kernel parameters
    cat > /tmp/99-redis.conf << 'EOF'
# Redis optimizations for FinClick.AI
vm.overcommit_memory = 1
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
EOF

    sudo mv /tmp/99-redis.conf /etc/sysctl.d/99-redis.conf

    # Apply sysctl changes
    sudo sysctl -p /etc/sysctl.d/99-redis.conf

    # Disable Transparent Huge Pages
    echo 'never' | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
    echo 'never' | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

    # Make THP disable persistent
    cat > /tmp/disable-thp.service << 'EOF'
[Unit]
Description=Disable Transparent Huge Pages (THP) for Redis
DefaultDependencies=no
After=sysinit.target local-fs.target
Before=redis.service

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/enabled'
ExecStart=/bin/sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/defrag'

[Install]
WantedBy=basic.target
EOF

    sudo mv /tmp/disable-thp.service /etc/systemd/system/disable-thp.service
    sudo systemctl enable disable-thp.service

    print_status "System optimizations applied"
}

# Test Redis installation
test_redis() {
    print_status "Testing Redis installation..."

    # Start Redis service
    sudo systemctl start redis

    # Wait a moment for service to start
    sleep 2

    # Test connection
    if redis-cli -a "FinClick2024SecureRedisPassword!" ping | grep -q "PONG"; then
        print_status "Redis is working correctly!"
    else
        print_error "Redis test failed"
        return 1
    fi

    # Test basic operations
    redis-cli -a "FinClick2024SecureRedisPassword!" set test_key "FinClick.AI Test" > /dev/null
    TEST_VALUE=$(redis-cli -a "FinClick2024SecureRedisPassword!" get test_key)

    if [[ "$TEST_VALUE" == "FinClick.AI Test" ]]; then
        print_status "Redis read/write test passed"
        redis-cli -a "FinClick2024SecureRedisPassword!" del test_key > /dev/null
    else
        print_error "Redis read/write test failed"
        return 1
    fi
}

# Main execution
main() {
    print_status "Starting Redis setup for FinClick.AI Platform..."

    install_redis
    create_directories
    setup_configuration

    # Only setup systemd services on Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        setup_systemd_services
        configure_firewall
        optimize_system

        # Enable and start services
        sudo systemctl enable redis
        sudo systemctl enable redis-sentinel

        test_redis

        print_status "Redis setup completed successfully!"
        print_status "Services status:"
        sudo systemctl status redis --no-pager -l
        echo ""
        print_status "You can start Redis Sentinel with: sudo systemctl start redis-sentinel"
    else
        print_status "Redis setup completed!"
        print_status "To start Redis manually: redis-server /etc/redis/redis.conf"
        print_status "To start Sentinel manually: redis-sentinel /etc/redis/sentinel.conf"
    fi

    print_status "Redis is configured for FinClick.AI Platform"
    print_warning "Remember to:"
    print_warning "1. Change default passwords in production"
    print_warning "2. Configure SSL/TLS for production use"
    print_warning "3. Set up monitoring and alerting"
    print_warning "4. Configure backup procedures"
}

# Run main function
main "$@"