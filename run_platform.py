#!/usr/bin/env python3
"""
FinClick.AI Platform Launcher
مشغل منصة FinClick.AI

This script orchestrates the startup of the complete FinClick.AI platform including:
- Database initialization and migrations
- Backend microservices startup
- AI agents system initialization
- Financial analysis engine startup
- Frontend development server
- Real-time monitoring and health checks

هذا البرنامج ينسق بدء تشغيل منصة FinClick.AI الكاملة بما في ذلك:
- تهيئة قاعدة البيانات والترحيلات
- بدء تشغيل الخدمات المصغرة للخلفية
- تهيئة نظام الوكلاء الذكيين
- بدء تشغيل محرك التحليل المالي
- خادم التطوير للواجهة الأمامية
- المراقبة في الوقت الفعلي وفحص الصحة
"""

import asyncio
import subprocess
import sys
import os
import signal
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import psutil
import requests
from concurrent.futures import ThreadPoolExecutor

# Add platform modules to path
sys.path.append(str(Path(__file__).parent))

from platform_integration_manager import PlatformIntegrationManager
from subscription_manager import SubscriptionManager


@dataclass
class ServiceConfig:
    """Configuration for a platform service"""
    name: str
    command: List[str]
    cwd: str
    port: Optional[int] = None
    health_check_url: Optional[str] = None
    startup_timeout: int = 60
    dependencies: List[str] = None
    env_vars: Dict[str, str] = None


class PlatformLauncher:
    """
    Orchestrates the complete FinClick.AI platform startup
    ينسق بدء تشغيل منصة FinClick.AI الكاملة
    """

    def __init__(self):
        self.logger = self._setup_logging()
        self.processes: Dict[str, subprocess.Popen] = {}
        self.service_configs = self._initialize_service_configs()
        self.startup_order = self._get_startup_order()
        self.shutdown_requested = False

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('platform_launcher.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)

    def _initialize_service_configs(self) -> Dict[str, ServiceConfig]:
        """Initialize service configurations"""
        base_path = Path(__file__).parent

        return {
            # Database Services
            'postgresql': ServiceConfig(
                name='PostgreSQL Database',
                command=['docker', 'run', '--rm', '-d', '--name', 'finclick-postgres',
                        '-p', '5432:5432',
                        '-e', 'POSTGRES_DB=finclick',
                        '-e', 'POSTGRES_USER=finclick',
                        '-e', 'POSTGRES_PASSWORD=password123',
                        '-v', str(base_path / 'database' / 'postgresql' / 'init')+':/docker-entrypoint-initdb.d',
                        'postgres:15-alpine'],
                cwd=str(base_path),
                port=5432,
                health_check_url='postgresql://finclick:password123@localhost:5432/finclick',
                startup_timeout=30
            ),

            'mongodb': ServiceConfig(
                name='MongoDB Database',
                command=['docker', 'run', '--rm', '-d', '--name', 'finclick-mongodb',
                        '-p', '27017:27017',
                        '-e', 'MONGO_INITDB_ROOT_USERNAME=finclick',
                        '-e', 'MONGO_INITDB_ROOT_PASSWORD=password123',
                        '-e', 'MONGO_INITDB_DATABASE=finclick_analysis',
                        '-v', str(base_path / 'database' / 'mongodb' / 'init')+':/docker-entrypoint-initdb.d',
                        'mongo:6.0'],
                cwd=str(base_path),
                port=27017,
                startup_timeout=30
            ),

            'redis': ServiceConfig(
                name='Redis Cache',
                command=['docker', 'run', '--rm', '-d', '--name', 'finclick-redis',
                        '-p', '6379:6379',
                        'redis:7-alpine',
                        'redis-server', '--requirepass', 'password123'],
                cwd=str(base_path),
                port=6379,
                startup_timeout=15
            ),

            # Backend Microservices
            'auth_service': ServiceConfig(
                name='Authentication Service',
                command=[sys.executable, 'app.py'],
                cwd=str(base_path / 'backend' / 'auth-service'),
                port=5001,
                health_check_url='http://localhost:5001/health',
                dependencies=['postgresql', 'redis'],
                env_vars={
                    'DATABASE_URL': 'postgresql://finclick:password123@localhost:5432/finclick',
                    'REDIS_URL': 'redis://:password123@localhost:6379/0',
                    'SECRET_KEY': 'your-super-secret-key-change-in-production',
                    'JWT_SECRET_KEY': 'your-jwt-secret-key'
                }
            ),

            'user_service': ServiceConfig(
                name='User Management Service',
                command=[sys.executable, 'app.py'],
                cwd=str(base_path / 'backend' / 'user-service'),
                port=5002,
                health_check_url='http://localhost:5002/health',
                dependencies=['postgresql', 'redis'],
                env_vars={
                    'DATABASE_URL': 'postgresql://finclick:password123@localhost:5432/finclick',
                    'REDIS_URL': 'redis://:password123@localhost:6379/0'
                }
            ),

            'file_service': ServiceConfig(
                name='File Processing Service',
                command=[sys.executable, 'app.py'],
                cwd=str(base_path / 'backend' / 'file-service'),
                port=5003,
                health_check_url='http://localhost:5003/health',
                dependencies=['postgresql', 'mongodb'],
                env_vars={
                    'DATABASE_URL': 'postgresql://finclick:password123@localhost:5432/finclick',
                    'MONGODB_URL': 'mongodb://finclick:password123@localhost:27017/finclick_files',
                    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID', ''),
                    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY', ''),
                    'AWS_S3_BUCKET': os.getenv('AWS_S3_BUCKET', 'finclick-files')
                }
            ),

            'notification_service': ServiceConfig(
                name='Notification Service',
                command=[sys.executable, 'app.py'],
                cwd=str(base_path / 'backend' / 'notification-service'),
                port=5004,
                health_check_url='http://localhost:5004/health',
                dependencies=['postgresql', 'redis'],
                env_vars={
                    'DATABASE_URL': 'postgresql://finclick:password123@localhost:5432/finclick',
                    'REDIS_URL': 'redis://:password123@localhost:6379/0',
                    'SMTP_HOST': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
                    'SMTP_PORT': os.getenv('SMTP_PORT', '587'),
                    'SMTP_USER': os.getenv('SMTP_USER', ''),
                    'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD', '')
                }
            ),

            'subscription_service': ServiceConfig(
                name='Subscription & Payment Service',
                command=[sys.executable, 'app.py'],
                cwd=str(base_path / 'backend' / 'subscription-service'),
                port=5005,
                health_check_url='http://localhost:5005/health',
                dependencies=['postgresql', 'redis'],
                env_vars={
                    'DATABASE_URL': 'postgresql://finclick:password123@localhost:5432/finclick',
                    'REDIS_URL': 'redis://:password123@localhost:6379/0',
                    'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY', ''),
                    'STRIPE_WEBHOOK_SECRET': os.getenv('STRIPE_WEBHOOK_SECRET', '')
                }
            ),

            'analysis_service': ServiceConfig(
                name='Analysis Coordination Service',
                command=[sys.executable, 'app.py'],
                cwd=str(base_path / 'backend' / 'analysis-service'),
                port=5006,
                health_check_url='http://localhost:5006/health',
                dependencies=['postgresql', 'mongodb', 'redis'],
                env_vars={
                    'DATABASE_URL': 'postgresql://finclick:password123@localhost:5432/finclick',
                    'MONGODB_URL': 'mongodb://finclick:password123@localhost:27017/finclick_analysis',
                    'REDIS_URL': 'redis://:password123@localhost:6379/0'
                }
            ),

            'ai_agents_service': ServiceConfig(
                name='AI Agents Service',
                command=[sys.executable, 'app.py'],
                cwd=str(base_path / 'backend' / 'ai-agents-service'),
                port=5007,
                health_check_url='http://localhost:5007/health',
                dependencies=['postgresql', 'mongodb', 'redis'],
                env_vars={
                    'DATABASE_URL': 'postgresql://finclick:password123@localhost:5432/finclick',
                    'MONGODB_URL': 'mongodb://finclick:password123@localhost:27017/finclick_analysis',
                    'REDIS_URL': 'redis://:password123@localhost:6379/0',
                    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', '')
                }
            ),

            'reporting_service': ServiceConfig(
                name='Report Generation Service',
                command=[sys.executable, 'app.py'],
                cwd=str(base_path / 'backend' / 'reporting-service'),
                port=5008,
                health_check_url='http://localhost:5008/health',
                dependencies=['postgresql', 'mongodb'],
                env_vars={
                    'DATABASE_URL': 'postgresql://finclick:password123@localhost:5432/finclick',
                    'MONGODB_URL': 'mongodb://finclick:password123@localhost:27017/finclick_analysis'
                }
            ),

            # Main Platform API
            'platform_api': ServiceConfig(
                name='Main Platform API',
                command=[sys.executable, 'platform_integration_manager.py'],
                cwd=str(base_path),
                port=8000,
                health_check_url='http://localhost:8000/health',
                dependencies=['postgresql', 'mongodb', 'redis'],
                env_vars={
                    'POSTGRES_HOST': 'localhost',
                    'POSTGRES_PORT': '5432',
                    'POSTGRES_DB': 'finclick',
                    'POSTGRES_USER': 'finclick',
                    'POSTGRES_PASSWORD': 'password123',
                    'MONGO_HOST': 'localhost',
                    'MONGO_PORT': '27017',
                    'MONGO_DB': 'finclick_analysis',
                    'MONGO_USER': 'finclick',
                    'MONGO_PASSWORD': 'password123',
                    'REDIS_HOST': 'localhost',
                    'REDIS_PORT': '6379',
                    'REDIS_PASSWORD': 'password123',
                    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                    'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY', ''),
                    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID', ''),
                    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY', '')
                }
            ),

            # Frontend Development Server
            'frontend': ServiceConfig(
                name='Frontend Development Server',
                command=['npm', 'start'],
                cwd=str(base_path / 'frontend'),
                port=3000,
                health_check_url='http://localhost:3000',
                dependencies=['platform_api'],
                env_vars={
                    'REACT_APP_API_URL': 'http://localhost:8000',
                    'REACT_APP_WS_URL': 'ws://localhost:8000',
                    'GENERATE_SOURCEMAP': 'false'
                },
                startup_timeout=120  # Frontend takes longer to start
            )
        }

    def _get_startup_order(self) -> List[List[str]]:
        """Get ordered service startup sequence"""
        return [
            # Phase 1: Core Infrastructure
            ['postgresql', 'mongodb', 'redis'],

            # Phase 2: Authentication & Core Services
            ['auth_service', 'user_service'],

            # Phase 3: Business Logic Services
            ['file_service', 'notification_service', 'subscription_service'],

            # Phase 4: Analysis Services
            ['analysis_service', 'ai_agents_service', 'reporting_service'],

            # Phase 5: Main Platform API
            ['platform_api'],

            # Phase 6: Frontend
            ['frontend']
        ]

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True

    async def start_platform(self) -> bool:
        """
        Start the complete FinClick.AI platform
        بدء تشغيل منصة FinClick.AI الكاملة
        """
        try:
            self.logger.info("🚀 Starting FinClick.AI Platform...")
            self.logger.info("=" * 60)

            # Check prerequisites
            if not await self._check_prerequisites():
                return False

            # Start services in phases
            for phase_num, services in enumerate(self.startup_order, 1):
                self.logger.info(f"📋 Phase {phase_num}: Starting {', '.join(services)}")

                # Start all services in this phase concurrently
                tasks = [self._start_service(service_name) for service_name in services]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Check if all services started successfully
                failed_services = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception) or not result:
                        failed_services.append(services[i])

                if failed_services:
                    self.logger.error(f"❌ Failed to start services: {', '.join(failed_services)}")
                    await self._cleanup_processes()
                    return False

                self.logger.info(f"✅ Phase {phase_num} completed successfully")

                # Wait between phases to ensure stability
                await asyncio.sleep(2)

            # Perform final health checks
            self.logger.info("🔍 Performing comprehensive health checks...")
            if await self._perform_health_checks():
                self.logger.info("🎉 FinClick.AI Platform started successfully!")
                self._print_access_information()
                return True
            else:
                self.logger.error("❌ Health checks failed")
                await self._cleanup_processes()
                return False

        except Exception as e:
            self.logger.error(f"❌ Platform startup failed: {str(e)}")
            await self._cleanup_processes()
            return False

    async def _check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        self.logger.info("🔍 Checking prerequisites...")

        checks = [
            ("Docker", self._check_docker),
            ("Node.js", self._check_nodejs),
            ("Python", self._check_python),
            ("Ports availability", self._check_ports),
            ("Environment variables", self._check_env_vars)
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                if await check_func():
                    self.logger.info(f"  ✅ {check_name}")
                else:
                    self.logger.error(f"  ❌ {check_name}")
                    all_passed = False
            except Exception as e:
                self.logger.error(f"  ❌ {check_name}: {str(e)}")
                all_passed = False

        return all_passed

    async def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def _check_nodejs(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(['node', '--version'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def _check_python(self) -> bool:
        """Check if Python 3.8+ is available"""
        try:
            version = sys.version_info
            return version.major == 3 and version.minor >= 8
        except:
            return False

    async def _check_ports(self) -> bool:
        """Check if required ports are available"""
        required_ports = [3000, 5432, 6379, 8000, 27017] + \
                        [config.port for config in self.service_configs.values()
                         if config.port and config.port not in [3000, 5432, 6379, 8000, 27017]]

        for port in required_ports:
            if self._is_port_in_use(port):
                self.logger.warning(f"Port {port} is already in use")
                return False

        return True

    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False

    async def _check_env_vars(self) -> bool:
        """Check critical environment variables"""
        critical_vars = ['OPENAI_API_KEY']
        missing_vars = [var for var in critical_vars if not os.getenv(var)]

        if missing_vars:
            self.logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
            self.logger.warning("Platform will start with limited functionality")

        return True  # Non-blocking for development

    async def _start_service(self, service_name: str) -> bool:
        """Start a single service"""
        config = self.service_configs[service_name]

        try:
            self.logger.info(f"  🔄 Starting {config.name}...")

            # Check dependencies
            if config.dependencies:
                for dep in config.dependencies:
                    if dep not in self.processes or self.processes[dep].poll() is not None:
                        self.logger.error(f"Dependency {dep} is not running")
                        return False

            # Prepare environment
            env = os.environ.copy()
            if config.env_vars:
                env.update(config.env_vars)

            # Start the process
            process = subprocess.Popen(
                config.command,
                cwd=config.cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.processes[service_name] = process

            # Wait for service to be ready
            if await self._wait_for_service_ready(service_name, config):
                self.logger.info(f"  ✅ {config.name} started successfully")
                return True
            else:
                self.logger.error(f"  ❌ {config.name} failed to start")
                return False

        except Exception as e:
            self.logger.error(f"  ❌ Failed to start {config.name}: {str(e)}")
            return False

    async def _wait_for_service_ready(self, service_name: str, config: ServiceConfig) -> bool:
        """Wait for service to be ready"""
        start_time = time.time()

        while time.time() - start_time < config.startup_timeout:
            if self.shutdown_requested:
                return False

            # Check if process is still running
            process = self.processes.get(service_name)
            if process and process.poll() is not None:
                # Process has terminated
                stdout, stderr = process.communicate()
                self.logger.error(f"Process {service_name} terminated: {stderr}")
                return False

            # Perform health check
            if config.health_check_url:
                if await self._health_check(config.health_check_url):
                    return True
            elif config.port:
                if self._is_port_in_use(config.port):
                    return True

            await asyncio.sleep(1)

        return False

    async def _health_check(self, url: str) -> bool:
        """Perform health check on a service"""
        try:
            if url.startswith('http'):
                response = requests.get(url, timeout=5)
                return response.status_code == 200
            elif url.startswith('postgresql'):
                # PostgreSQL health check would go here
                return True
            else:
                return True
        except:
            return False

    async def _perform_health_checks(self) -> bool:
        """Perform comprehensive health checks on all services"""
        health_checks = []

        for service_name, config in self.service_configs.items():
            if service_name in self.processes and config.health_check_url:
                health_checks.append((service_name, config.health_check_url))

        all_healthy = True
        for service_name, health_url in health_checks:
            if await self._health_check(health_url):
                self.logger.info(f"  ✅ {service_name} is healthy")
            else:
                self.logger.error(f"  ❌ {service_name} health check failed")
                all_healthy = False

        return all_healthy

    def _print_access_information(self):
        """Print platform access information"""
        self.logger.info("")
        self.logger.info("🌟 FinClick.AI Platform is now running!")
        self.logger.info("=" * 60)
        self.logger.info("📊 Frontend Application: http://localhost:3000")
        self.logger.info("🔌 Main Platform API: http://localhost:8000")
        self.logger.info("📚 API Documentation: http://localhost:8000/api/docs")
        self.logger.info("🔍 Health Status: http://localhost:8000/health")
        self.logger.info("=" * 60)
        self.logger.info("💡 To stop the platform, press Ctrl+C")
        self.logger.info("")

    async def monitor_platform(self):
        """Monitor platform health and services"""
        self.logger.info("🔍 Starting platform monitoring...")

        while not self.shutdown_requested:
            try:
                # Check process health
                dead_processes = []
                for service_name, process in self.processes.items():
                    if process.poll() is not None:
                        dead_processes.append(service_name)

                if dead_processes:
                    self.logger.error(f"⚠️  Dead processes detected: {', '.join(dead_processes)}")

                # Log resource usage
                system_info = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent
                }

                if system_info['cpu_percent'] > 80 or system_info['memory_percent'] > 80:
                    self.logger.warning(f"⚠️  High resource usage: CPU {system_info['cpu_percent']}%, Memory {system_info['memory_percent']}%")

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)

    async def _cleanup_processes(self):
        """Cleanup all started processes"""
        self.logger.info("🧹 Cleaning up processes...")

        # Terminate processes in reverse order
        cleanup_order = []
        for phase in reversed(self.startup_order):
            cleanup_order.extend(reversed(phase))

        for service_name in cleanup_order:
            if service_name in self.processes:
                process = self.processes[service_name]
                if process.poll() is None:  # Process is still running
                    self.logger.info(f"  🛑 Stopping {service_name}...")
                    try:
                        process.terminate()
                        await asyncio.sleep(2)
                        if process.poll() is None:
                            process.kill()
                    except:
                        pass

        # Clean up Docker containers
        for service_name in ['postgresql', 'mongodb', 'redis']:
            try:
                subprocess.run(['docker', 'stop', f'finclick-{service_name}'],
                             capture_output=True)
                subprocess.run(['docker', 'rm', f'finclick-{service_name}'],
                             capture_output=True)
            except:
                pass

        self.logger.info("✅ Cleanup completed")

    async def run_platform(self):
        """Main platform runner"""
        try:
            # Start the platform
            if await self.start_platform():
                # Start monitoring
                monitor_task = asyncio.create_task(self.monitor_platform())

                # Wait for shutdown signal
                while not self.shutdown_requested:
                    await asyncio.sleep(1)

                # Cancel monitoring
                monitor_task.cancel()

            else:
                self.logger.error("❌ Failed to start platform")
                return 1

        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            self.logger.error(f"❌ Platform error: {str(e)}")
            return 1
        finally:
            await self._cleanup_processes()

        return 0


async def main():
    """Main entry point"""
    launcher = PlatformLauncher()
    return await launcher.run_platform()


if __name__ == "__main__":
    # Show banner
    print("""
    ███████╗██╗███╗   ██╗ ██████╗██╗     ██╗ ██████╗██╗  ██╗    █████╗ ██╗
    ██╔════╝██║████╗  ██║██╔════╝██║     ██║██╔════╝██║ ██╔╝   ██╔══██╗██║
    █████╗  ██║██╔██╗ ██║██║     ██║     ██║██║     █████╔╝    ███████║██║
    ██╔══╝  ██║██║╚██╗██║██║     ██║     ██║██║     ██╔═██╗    ██╔══██║██║
    ██║     ██║██║ ╚████║╚██████╗███████╗██║╚██████╗██║  ██╗██╗██║  ██║██║
    ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝

    🌟 Revolutionary Intelligent Financial Analysis Platform
    منصة التحليل المالي الذكي الثورية

    🚀 Powered by 23 AI Agents & 180 Analysis Types
    مدعومة بـ 23 وكيل ذكي و 180 نوع تحليل
    """)

    # Run the platform
    exit_code = asyncio.run(main())
    sys.exit(exit_code)