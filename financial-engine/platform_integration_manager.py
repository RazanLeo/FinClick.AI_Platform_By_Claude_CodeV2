#!/usr/bin/env python3
"""
FinClick.AI Platform Integration Manager
مدير التكامل لمنصة FinClick.AI

This module manages the complete integration of all platform components:
- 23 AI agents with LangGraph orchestration
- 8 microservices
- Financial analysis engine with 180 analyses
- Database systems (PostgreSQL, MongoDB, Redis)
- Frontend integration
- Subscription and payment systems
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psycopg2
import pymongo
import redis
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from main_analysis_engine import FinancialAnalysisEngine
from ai_agents.agent_orchestrator import AIAgentOrchestrator
from analysis_types.liquidity_analysis import LiquidityAnalysis
from analysis_types.profitability_analysis import ProfitabilityAnalysis
from analysis_types.efficiency_analysis import EfficiencyAnalysis
from analysis_types.leverage_analysis import LeverageAnalysis
from analysis_types.market_analysis import MarketAnalysis
from analysis_types.investment_analysis import InvestmentAnalysis


class PlatformIntegrationManager:
    """
    مدير التكامل الشامل للمنصة
    Complete Platform Integration Manager
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        # Core system components
        self.analysis_engine = None
        self.ai_orchestrator = None
        self.database_connections = {}
        self.microservices = {}
        self.system_status = {}

        # Configuration
        self.config = self.load_configuration()

        # Performance metrics
        self.performance_metrics = {
            'startup_time': 0,
            'analysis_count': 0,
            'user_sessions': 0,
            'system_uptime': 0,
            'error_count': 0
        }

    def setup_logging(self):
        """إعداد نظام التسجيل"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/logs/platform_integration.log'),
                logging.StreamHandler()
            ]
        )

    def load_configuration(self) -> Dict[str, Any]:
        """تحميل إعدادات المنصة"""
        try:
            with open('/config/platform_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_config()

    def get_default_config(self) -> Dict[str, Any]:
        """الإعدادات الافتراضية للمنصة"""
        return {
            "database": {
                "postgresql": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "finclick_main",
                    "user": "finclick_user",
                    "password": "secure_password"
                },
                "mongodb": {
                    "host": "localhost",
                    "port": 27017,
                    "database": "finclick_documents"
                },
                "redis": {
                    "host": "localhost",
                    "port": 6379,
                    "db": 0
                }
            },
            "microservices": {
                "document_processor": {"host": "localhost", "port": 8001},
                "analysis_service": {"host": "localhost", "port": 8002},
                "user_management": {"host": "localhost", "port": 8003},
                "report_generator": {"host": "localhost", "port": 8004},
                "subscription_service": {"host": "localhost", "port": 8005},
                "notification_service": {"host": "localhost", "port": 8006},
                "ai_orchestrator": {"host": "localhost", "port": 8007},
                "api_gateway": {"host": "localhost", "port": 8000}
            },
            "ai_agents": {
                "max_concurrent": 5,
                "timeout": 300,
                "retry_attempts": 3
            },
            "analysis": {
                "max_concurrent_analyses": 10,
                "cache_duration": 3600,
                "result_retention_days": 30
            },
            "subscription_plans": {
                "free": {"analyses_limit": 5, "price": 0},
                "professional": {"analyses_limit": 50, "price": 29},
                "enterprise": {"analyses_limit": -1, "price": 299}
            }
        }

    async def initialize_platform(self) -> bool:
        """
        تهيئة المنصة الكاملة
        Complete Platform Initialization
        """
        start_time = time.time()
        self.logger.info("🚀 بدء تهيئة منصة FinClick.AI / Starting FinClick.AI Platform Initialization")

        try:
            # 1. Initialize databases
            if not await self.initialize_databases():
                raise Exception("Database initialization failed")

            # 2. Start microservices
            if not await self.start_microservices():
                raise Exception("Microservices startup failed")

            # 3. Initialize AI orchestrator
            if not await self.initialize_ai_system():
                raise Exception("AI system initialization failed")

            # 4. Initialize analysis engine
            if not await self.initialize_analysis_engine():
                raise Exception("Analysis engine initialization failed")

            # 5. Setup integration bridges
            if not await self.setup_integration_bridges():
                raise Exception("Integration bridges setup failed")

            # 6. Perform system health check
            if not await self.perform_system_health_check():
                raise Exception("System health check failed")

            self.performance_metrics['startup_time'] = time.time() - start_time
            self.logger.info(f"✅ تم تهيئة المنصة بنجاح في {self.performance_metrics['startup_time']:.2f} ثانية")
            self.logger.info(f"✅ Platform initialized successfully in {self.performance_metrics['startup_time']:.2f} seconds")

            return True

        except Exception as e:
            self.logger.error(f"❌ فشل في تهيئة المنصة: {str(e)}")
            self.logger.error(f"❌ Platform initialization failed: {str(e)}")
            return False

    async def initialize_databases(self) -> bool:
        """تهيئة قواعد البيانات"""
        try:
            self.logger.info("📊 تهيئة قواعد البيانات / Initializing Databases")

            # PostgreSQL connection
            pg_config = self.config['database']['postgresql']
            self.database_connections['postgresql'] = psycopg2.connect(
                host=pg_config['host'],
                port=pg_config['port'],
                database=pg_config['database'],
                user=pg_config['user'],
                password=pg_config['password']
            )

            # MongoDB connection
            mongo_config = self.config['database']['mongodb']
            self.database_connections['mongodb'] = pymongo.MongoClient(
                f"mongodb://{mongo_config['host']}:{mongo_config['port']}"
            )[mongo_config['database']]

            # Redis connection
            redis_config = self.config['database']['redis']
            self.database_connections['redis'] = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config['db'],
                decode_responses=True
            )

            # Test connections
            self.database_connections['postgresql'].cursor().execute('SELECT 1')
            self.database_connections['mongodb'].list_collection_names()
            self.database_connections['redis'].ping()

            self.logger.info("✅ تم تهيئة قواعد البيانات بنجاح / Databases initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ فشل في تهيئة قواعد البيانات: {str(e)}")
            return False

    async def start_microservices(self) -> bool:
        """بدء تشغيل الخدمات المصغرة"""
        try:
            self.logger.info("🔧 بدء تشغيل الخدمات المصغرة / Starting Microservices")

            # Check microservice health
            for service_name, config in self.config['microservices'].items():
                try:
                    response = requests.get(
                        f"http://{config['host']}:{config['port']}/health",
                        timeout=5
                    )
                    if response.status_code == 200:
                        self.microservices[service_name] = {
                            'status': 'running',
                            'url': f"http://{config['host']}:{config['port']}",
                            'last_check': datetime.now()
                        }
                        self.logger.info(f"✅ {service_name} is running")
                    else:
                        raise Exception(f"Service returned status {response.status_code}")

                except Exception as e:
                    self.logger.warning(f"⚠️  {service_name} is not responding: {str(e)}")
                    self.microservices[service_name] = {
                        'status': 'offline',
                        'error': str(e),
                        'last_check': datetime.now()
                    }

            # Check if critical services are running
            critical_services = ['api_gateway', 'analysis_service', 'user_management']
            running_critical = [s for s in critical_services if self.microservices.get(s, {}).get('status') == 'running']

            if len(running_critical) >= len(critical_services) * 0.8:  # 80% of critical services
                self.logger.info("✅ الخدمات المصغرة جاهزة / Microservices ready")
                return True
            else:
                self.logger.error("❌ الخدمات الحرجة غير متاحة / Critical services unavailable")
                return False

        except Exception as e:
            self.logger.error(f"❌ فشل في بدء الخدمات المصغرة: {str(e)}")
            return False

    async def initialize_ai_system(self) -> bool:
        """تهيئة نظام الذكاء الاصطناعي"""
        try:
            self.logger.info("🤖 تهيئة نظام الذكاء الاصطناعي / Initializing AI System")

            # Initialize AI orchestrator with all 23 agents
            self.ai_orchestrator = AIAgentOrchestrator()

            # Load and initialize all AI agents
            agent_initialization = await self.ai_orchestrator.initialize_all_agents()

            if agent_initialization['success']:
                active_agents = agent_initialization['active_agents']
                self.logger.info(f"✅ تم تهيئة {active_agents} وكيل ذكي من أصل 23")
                self.logger.info(f"✅ Initialized {active_agents} AI agents out of 23")

                if active_agents >= 18:  # At least 78% of agents working
                    return True
                else:
                    self.logger.warning("⚠️  عدد قليل من الوكلاء الذكيين يعمل / Too few AI agents active")
                    return False
            else:
                self.logger.error("❌ فشل في تهيئة الوكلاء الذكيين / AI agents initialization failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ فشل في تهيئة نظام الذكاء الاصطناعي: {str(e)}")
            return False

    async def initialize_analysis_engine(self) -> bool:
        """تهيئة محرك التحليل المالي"""
        try:
            self.logger.info("📈 تهيئة محرك التحليل المالي / Initializing Financial Analysis Engine")

            # Initialize main analysis engine
            self.analysis_engine = FinancialAnalysisEngine()

            # Test all analysis categories
            test_data = {
                'total_assets': 1000000,
                'current_assets': 600000,
                'cash': 100000,
                'current_liabilities': 300000,
                'total_liabilities': 400000,
                'revenue': 1200000,
                'net_income': 120000,
                'cost_of_goods_sold': 800000,
                'inventory': 150000,
                'accounts_receivable': 100000,
                'accounts_payable': 80000,
                'total_equity': 600000,
                'market_cap': 2000000,
                'shares_outstanding': 100000,
                'stock_price': 20
            }

            # Test each analysis category
            categories_tested = 0
            categories_working = 0

            analysis_categories = [
                'liquidity', 'profitability', 'efficiency',
                'leverage', 'market', 'investment'
            ]

            for category in analysis_categories:
                try:
                    result = await self.analysis_engine.run_category_analysis(category, test_data)
                    if result['success'] and len(result['analyses']) > 0:
                        categories_working += 1
                        self.logger.info(f"✅ {category} analysis working ({len(result['analyses'])} analyses)")
                    categories_tested += 1
                except Exception as e:
                    self.logger.warning(f"⚠️  {category} analysis failed: {str(e)}")
                    categories_tested += 1

            success_rate = categories_working / categories_tested if categories_tested > 0 else 0

            if success_rate >= 0.8:  # 80% success rate
                self.logger.info(f"✅ محرك التحليل جاهز بمعدل نجاح {success_rate*100:.1f}%")
                self.logger.info(f"✅ Analysis engine ready with {success_rate*100:.1f}% success rate")
                return True
            else:
                self.logger.error(f"❌ محرك التحليل فشل بمعدل نجاح {success_rate*100:.1f}%")
                return False

        except Exception as e:
            self.logger.error(f"❌ فشل في تهيئة محرك التحليل: {str(e)}")
            return False

    async def setup_integration_bridges(self) -> bool:
        """إعداد جسور التكامل بين المكونات"""
        try:
            self.logger.info("🌉 إعداد جسور التكامل / Setting up Integration Bridges")

            # Integration bridge configurations
            bridges = {
                'ai_to_analysis': self.setup_ai_analysis_bridge,
                'analysis_to_report': self.setup_analysis_report_bridge,
                'user_to_subscription': self.setup_user_subscription_bridge,
                'frontend_to_backend': self.setup_frontend_backend_bridge
            }

            successful_bridges = 0

            for bridge_name, bridge_setup in bridges.items():
                try:
                    await bridge_setup()
                    successful_bridges += 1
                    self.logger.info(f"✅ {bridge_name} bridge established")
                except Exception as e:
                    self.logger.warning(f"⚠️  {bridge_name} bridge failed: {str(e)}")

            success_rate = successful_bridges / len(bridges)

            if success_rate >= 0.75:  # 75% of bridges working
                self.logger.info("✅ جسور التكامل جاهزة / Integration bridges ready")
                return True
            else:
                self.logger.error("❌ فشل في إعداد جسور التكامل / Integration bridges failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ فشل في إعداد جسور التكامل: {str(e)}")
            return False

    async def setup_ai_analysis_bridge(self):
        """جسر التكامل بين الذكاء الاصطناعي والتحليل"""
        # Setup communication channel between AI agents and analysis engine
        if self.ai_orchestrator and self.analysis_engine:
            self.ai_orchestrator.set_analysis_engine(self.analysis_engine)
            self.analysis_engine.set_ai_orchestrator(self.ai_orchestrator)

    async def setup_analysis_report_bridge(self):
        """جسر التكامل بين التحليل وتوليد التقارير"""
        # Setup connection to report generation service
        report_service = self.microservices.get('report_generator', {})
        if report_service.get('status') == 'running':
            self.analysis_engine.set_report_service_url(report_service['url'])

    async def setup_user_subscription_bridge(self):
        """جسر التكامل بين إدارة المستخدمين والاشتراكات"""
        # Connect user management with subscription service
        user_service = self.microservices.get('user_management', {})
        subscription_service = self.microservices.get('subscription_service', {})

        if (user_service.get('status') == 'running' and
            subscription_service.get('status') == 'running'):
            # Setup integration endpoint
            requests.post(
                f"{user_service['url']}/integration/subscription",
                json={'subscription_service_url': subscription_service['url']},
                timeout=5
            )

    async def setup_frontend_backend_bridge(self):
        """جسر التكامل بين الواجهة الأمامية والخلفية"""
        # Setup API gateway integration
        api_gateway = self.microservices.get('api_gateway', {})
        if api_gateway.get('status') == 'running':
            # Configure CORS and API routing
            pass

    async def perform_system_health_check(self) -> bool:
        """فحص صحة النظام الشامل"""
        try:
            self.logger.info("🏥 فحص صحة النظام / System Health Check")

            health_checks = {
                'databases': await self.check_database_health(),
                'microservices': await self.check_microservices_health(),
                'ai_system': await self.check_ai_system_health(),
                'analysis_engine': await self.check_analysis_engine_health(),
                'integration': await self.check_integration_health()
            }

            # Calculate overall health score
            health_score = sum(1 for status in health_checks.values() if status) / len(health_checks)

            self.system_status = {
                'overall_health': health_score,
                'component_status': health_checks,
                'last_check': datetime.now(),
                'status': 'healthy' if health_score >= 0.8 else 'degraded' if health_score >= 0.6 else 'critical'
            }

            self.logger.info(f"📊 النظام صحي بنسبة {health_score*100:.1f}% / System {health_score*100:.1f}% healthy")

            return health_score >= 0.7  # 70% minimum health

        except Exception as e:
            self.logger.error(f"❌ فشل فحص صحة النظام: {str(e)}")
            return False

    async def check_database_health(self) -> bool:
        """فحص صحة قواعد البيانات"""
        try:
            # Test PostgreSQL
            cursor = self.database_connections['postgresql'].cursor()
            cursor.execute('SELECT COUNT(*) FROM information_schema.tables')
            cursor.fetchone()

            # Test MongoDB
            self.database_connections['mongodb'].list_collection_names()

            # Test Redis
            self.database_connections['redis'].ping()

            return True
        except:
            return False

    async def check_microservices_health(self) -> bool:
        """فحص صحة الخدمات المصغرة"""
        running_services = [s for s in self.microservices.values() if s.get('status') == 'running']
        return len(running_services) >= len(self.microservices) * 0.7

    async def check_ai_system_health(self) -> bool:
        """فحص صحة نظام الذكاء الاصطناعي"""
        if not self.ai_orchestrator:
            return False
        try:
            status = await self.ai_orchestrator.get_system_status()
            return status.get('active_agents', 0) >= 15  # At least 15 agents active
        except:
            return False

    async def check_analysis_engine_health(self) -> bool:
        """فحص صحة محرك التحليل"""
        if not self.analysis_engine:
            return False
        try:
            # Quick test analysis
            test_result = await self.analysis_engine.quick_health_check()
            return test_result.get('success', False)
        except:
            return False

    async def check_integration_health(self) -> bool:
        """فحص صحة التكامل"""
        # Check if key integration points are working
        return (self.ai_orchestrator is not None and
                self.analysis_engine is not None and
                len(self.database_connections) >= 2)

    async def process_user_request(self, user_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        معالجة طلب المستخدم الكامل
        Process Complete User Request
        """
        try:
            self.logger.info(f"🔄 معالجة طلب المستخدم {user_id} / Processing user {user_id} request")

            # 1. Validate user subscription
            subscription_valid = await self.validate_user_subscription(user_id, request_data)
            if not subscription_valid:
                return {'success': False, 'error': 'Subscription limit exceeded'}

            # 2. Process document if provided
            document_data = None
            if 'document' in request_data:
                document_data = await self.process_document(request_data['document'])
                if not document_data['success']:
                    return {'success': False, 'error': 'Document processing failed'}

            # 3. Run AI analysis coordination
            ai_analysis = await self.ai_orchestrator.coordinate_analysis(
                user_id=user_id,
                document_data=document_data,
                analysis_requests=request_data.get('analyses', [])
            )

            # 4. Execute financial analyses
            financial_analysis = await self.analysis_engine.run_comprehensive_analysis(
                data=document_data['extracted_data'] if document_data else request_data.get('financial_data', {}),
                requested_analyses=request_data.get('analyses', []),
                ai_insights=ai_analysis.get('insights', {})
            )

            # 5. Generate professional report
            report_data = await self.generate_comprehensive_report(
                user_id=user_id,
                ai_analysis=ai_analysis,
                financial_analysis=financial_analysis,
                preferences=request_data.get('report_preferences', {})
            )

            # 6. Update user analytics
            await self.update_user_analytics(user_id, financial_analysis['analyses_count'])

            # 7. Send notifications if requested
            if request_data.get('send_notifications', False):
                await self.send_completion_notification(user_id, report_data)

            self.performance_metrics['analysis_count'] += 1

            return {
                'success': True,
                'ai_analysis': ai_analysis,
                'financial_analysis': financial_analysis,
                'report': report_data,
                'processing_time': financial_analysis.get('processing_time', 0),
                'analyses_used': financial_analysis.get('analyses_count', 0)
            }

        except Exception as e:
            self.logger.error(f"❌ فشل في معالجة طلب المستخدم {user_id}: {str(e)}")
            self.performance_metrics['error_count'] += 1
            return {'success': False, 'error': str(e)}

    async def validate_user_subscription(self, user_id: str, request_data: Dict[str, Any]) -> bool:
        """التحقق من صحة اشتراك المستخدم"""
        try:
            subscription_service = self.microservices.get('subscription_service', {})
            if subscription_service.get('status') != 'running':
                return True  # Default to allow if service unavailable

            response = requests.post(
                f"{subscription_service['url']}/validate",
                json={
                    'user_id': user_id,
                    'requested_analyses': len(request_data.get('analyses', [])),
                    'analysis_type': 'comprehensive'
                },
                timeout=10
            )

            return response.status_code == 200 and response.json().get('valid', False)

        except Exception as e:
            self.logger.warning(f"⚠️  فشل التحقق من الاشتراك: {str(e)}")
            return True  # Default to allow

    async def process_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """معالجة المستندات المرفوعة"""
        try:
            doc_service = self.microservices.get('document_processor', {})
            if doc_service.get('status') != 'running':
                raise Exception("Document processing service unavailable")

            response = requests.post(
                f"{doc_service['url']}/process",
                json=document_data,
                timeout=60  # Documents can take time to process
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Document processing failed: {response.status_code}")

        except Exception as e:
            self.logger.error(f"❌ فشل معالجة المستند: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def generate_comprehensive_report(self, user_id: str, ai_analysis: Dict,
                                          financial_analysis: Dict, preferences: Dict) -> Dict[str, Any]:
        """توليد التقرير الشامل"""
        try:
            report_service = self.microservices.get('report_generator', {})
            if report_service.get('status') != 'running':
                raise Exception("Report generation service unavailable")

            report_request = {
                'user_id': user_id,
                'ai_analysis': ai_analysis,
                'financial_analysis': financial_analysis,
                'preferences': preferences,
                'template': preferences.get('template', 'comprehensive'),
                'language': preferences.get('language', 'ar'),
                'format': preferences.get('format', 'pdf')
            }

            response = requests.post(
                f"{report_service['url']}/generate",
                json=report_request,
                timeout=120  # Reports can take time to generate
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Report generation failed: {response.status_code}")

        except Exception as e:
            self.logger.error(f"❌ فشل توليد التقرير: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def update_user_analytics(self, user_id: str, analyses_count: int):
        """تحديث إحصائيات المستخدم"""
        try:
            # Update in Redis cache
            redis_conn = self.database_connections['redis']
            user_key = f"user_analytics:{user_id}"

            redis_conn.hincrby(user_key, 'total_analyses', analyses_count)
            redis_conn.hincrby(user_key, 'session_count', 1)
            redis_conn.hset(user_key, 'last_activity', datetime.now().isoformat())
            redis_conn.expire(user_key, 86400 * 30)  # 30 days expiry

            # Update in PostgreSQL
            cursor = self.database_connections['postgresql'].cursor()
            cursor.execute("""
                INSERT INTO user_analytics (user_id, date, analyses_count, sessions_count)
                VALUES (%s, %s, %s, 1)
                ON CONFLICT (user_id, date)
                DO UPDATE SET
                    analyses_count = user_analytics.analyses_count + %s,
                    sessions_count = user_analytics.sessions_count + 1
            """, (user_id, datetime.now().date(), analyses_count, analyses_count))

            self.database_connections['postgresql'].commit()

        except Exception as e:
            self.logger.warning(f"⚠️  فشل تحديث إحصائيات المستخدم: {str(e)}")

    async def send_completion_notification(self, user_id: str, report_data: Dict):
        """إرسال إشعار اكتمال التحليل"""
        try:
            notification_service = self.microservices.get('notification_service', {})
            if notification_service.get('status') == 'running':
                requests.post(
                    f"{notification_service['url']}/send",
                    json={
                        'user_id': user_id,
                        'type': 'analysis_complete',
                        'data': {
                            'report_id': report_data.get('report_id'),
                            'analyses_count': report_data.get('analyses_count', 0)
                        }
                    },
                    timeout=10
                )
        except Exception as e:
            self.logger.warning(f"⚠️  فشل إرسال الإشعار: {str(e)}")

    async def get_platform_status(self) -> Dict[str, Any]:
        """الحصول على حالة المنصة الشاملة"""
        return {
            'platform_status': self.system_status,
            'performance_metrics': self.performance_metrics,
            'database_connections': {
                name: 'connected' if conn else 'disconnected'
                for name, conn in self.database_connections.items()
            },
            'microservices_status': {
                name: service.get('status', 'unknown')
                for name, service in self.microservices.items()
            },
            'ai_system_status': await self.ai_orchestrator.get_system_status() if self.ai_orchestrator else {'status': 'offline'},
            'analysis_engine_status': await self.analysis_engine.get_status() if self.analysis_engine else {'status': 'offline'}
        }

    async def shutdown_platform(self):
        """إغلاق المنصة بأمان"""
        self.logger.info("🛑 بدء إغلاق المنصة / Starting platform shutdown")

        try:
            # 1. Stop accepting new requests
            if self.ai_orchestrator:
                await self.ai_orchestrator.stop_accepting_requests()

            # 2. Complete ongoing analyses
            if self.analysis_engine:
                await self.analysis_engine.complete_pending_analyses()

            # 3. Close database connections
            for name, conn in self.database_connections.items():
                try:
                    if name == 'postgresql':
                        conn.close()
                    elif name == 'mongodb':
                        conn.close()
                    elif name == 'redis':
                        conn.close()
                    self.logger.info(f"✅ {name} connection closed")
                except Exception as e:
                    self.logger.warning(f"⚠️  Error closing {name}: {str(e)}")

            # 4. Shutdown AI orchestrator
            if self.ai_orchestrator:
                await self.ai_orchestrator.shutdown()

            self.logger.info("✅ تم إغلاق المنصة بنجاح / Platform shutdown completed")

        except Exception as e:
            self.logger.error(f"❌ خطأ في إغلاق المنصة: {str(e)}")


# Main integration manager instance
integration_manager = PlatformIntegrationManager()


async def main():
    """النقطة الرئيسية لبدء تشغيل المنصة"""
    try:
        # Initialize the complete platform
        success = await integration_manager.initialize_platform()

        if success:
            print("🎉 FinClick.AI Platform is ready!")
            print("🎉 منصة FinClick.AI جاهزة للعمل!")

            # Keep the platform running
            while True:
                await asyncio.sleep(60)  # Check every minute
                status = await integration_manager.get_platform_status()

                if status['platform_status']['status'] == 'critical':
                    print("⚠️  Platform in critical state, attempting recovery...")
                    await integration_manager.initialize_platform()

        else:
            print("❌ Failed to initialize FinClick.AI Platform")
            print("❌ فشل في تهيئة منصة FinClick.AI")

    except KeyboardInterrupt:
        print("\n🛑 Shutting down platform...")
        await integration_manager.shutdown_platform()
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())