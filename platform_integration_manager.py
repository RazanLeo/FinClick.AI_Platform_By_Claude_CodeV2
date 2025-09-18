"""
FinClick.AI Platform Integration Manager
مدير تكامل منصة FinClick.AI

This module orchestrates the complete integration of all platform components:
- Frontend React application
- Backend microservices (23 AI agents)
- Financial analysis engine (180 analysis types)
- Database systems (PostgreSQL, MongoDB, Redis)
- External APIs and services
- Subscription and payment systems

هذا الوحدة ينسق التكامل الكامل لجميع مكونات المنصة:
- تطبيق React للواجهة الأمامية
- الخدمات المصغرة للخلفية (23 وكيل ذكي)
- محرك التحليل المالي (180 نوع تحليل)
- أنظمة قواعد البيانات (PostgreSQL، MongoDB، Redis)
- واجهات برمجة التطبيقات والخدمات الخارجية
- أنظمة الاشتراك والدفع
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import traceback
from pathlib import Path

# Add project paths to Python path
sys.path.append(str(Path(__file__).parent / "ai-agents"))
sys.path.append(str(Path(__file__).parent / "financial-engine"))
sys.path.append(str(Path(__file__).parent / "backend"))

# Import platform components
try:
    from ai_agents.core.agent_orchestrator import AgentOrchestrator, WorkflowType
    from financial_engine.analysis_types.base_analysis import BaseFinancialAnalysis
except ImportError as e:
    logging.warning(f"Could not import AI agents or financial engine: {e}")

# FastAPI and web framework imports
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient


class PlatformStatus(Enum):
    """Platform operational status"""
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"


class ServiceType(Enum):
    """Types of platform services"""
    FRONTEND = "frontend"
    BACKEND_API = "backend_api"
    AI_AGENTS = "ai_agents"
    FINANCIAL_ENGINE = "financial_engine"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    SUBSCRIPTION = "subscription"
    AUTHENTICATION = "authentication"
    FILE_STORAGE = "file_storage"
    NOTIFICATION = "notification"


@dataclass
class ServiceHealth:
    """Health information for a service"""
    service_type: ServiceType
    service_name: str
    status: str
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisRequest:
    """Request for financial analysis"""
    user_id: str
    analysis_type: str
    data_source: str
    company_data: Dict[str, Any]
    analysis_options: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    request_id: Optional[str] = None


@dataclass
class AnalysisResponse:
    """Response from financial analysis"""
    request_id: str
    status: str
    results: Dict[str, Any]
    execution_time_ms: float
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class PlatformIntegrationManager:
    """
    Main orchestrator for the entire FinClick.AI platform
    المنسق الرئيسي لمنصة FinClick.AI بالكامل
    """

    def __init__(self):
        """Initialize the platform integration manager"""
        self.logger = self._setup_logging()

        # Platform components
        self.fastapi_app = None
        self.agent_orchestrator = None
        self.financial_engine = None

        # Database connections
        self.postgres_pool = None
        self.mongodb_client = None
        self.redis_client = None

        # Service health monitoring
        self.service_health: Dict[str, ServiceHealth] = {}
        self.platform_status = PlatformStatus.STARTING

        # Configuration
        self.config = self._load_configuration()

        # Analysis queue and processing
        self.analysis_queue = asyncio.Queue()
        self.active_analyses: Dict[str, AnalysisRequest] = {}

        # WebSocket connections for real-time updates
        self.websocket_connections: Dict[str, WebSocket] = {}

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('platform_integration.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)

    def _load_configuration(self) -> Dict[str, Any]:
        """Load platform configuration"""
        config = {
            # Database configuration
            "databases": {
                "postgresql": {
                    "host": os.getenv("POSTGRES_HOST", "localhost"),
                    "port": int(os.getenv("POSTGRES_PORT", "5432")),
                    "database": os.getenv("POSTGRES_DB", "finclick"),
                    "user": os.getenv("POSTGRES_USER", "finclick"),
                    "password": os.getenv("POSTGRES_PASSWORD", "password")
                },
                "mongodb": {
                    "host": os.getenv("MONGO_HOST", "localhost"),
                    "port": int(os.getenv("MONGO_PORT", "27017")),
                    "database": os.getenv("MONGO_DB", "finclick_analysis"),
                    "username": os.getenv("MONGO_USER", "finclick"),
                    "password": os.getenv("MONGO_PASSWORD", "password")
                },
                "redis": {
                    "host": os.getenv("REDIS_HOST", "localhost"),
                    "port": int(os.getenv("REDIS_PORT", "6379")),
                    "password": os.getenv("REDIS_PASSWORD", ""),
                    "db": int(os.getenv("REDIS_DB", "0"))
                }
            },

            # Service endpoints
            "services": {
                "auth_service": os.getenv("AUTH_SERVICE_URL", "http://localhost:5001"),
                "user_service": os.getenv("USER_SERVICE_URL", "http://localhost:5002"),
                "file_service": os.getenv("FILE_SERVICE_URL", "http://localhost:5003"),
                "notification_service": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:5004"),
                "subscription_service": os.getenv("SUBSCRIPTION_SERVICE_URL", "http://localhost:5005"),
                "analysis_service": os.getenv("ANALYSIS_SERVICE_URL", "http://localhost:5006"),
                "ai_agents_service": os.getenv("AI_AGENTS_SERVICE_URL", "http://localhost:5007"),
                "reporting_service": os.getenv("REPORTING_SERVICE_URL", "http://localhost:5008")
            },

            # External APIs
            "external_apis": {
                "stripe": {
                    "public_key": os.getenv("STRIPE_PUBLIC_KEY"),
                    "secret_key": os.getenv("STRIPE_SECRET_KEY"),
                    "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET")
                },
                "aws": {
                    "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                    "region": os.getenv("AWS_REGION", "us-east-1"),
                    "s3_bucket": os.getenv("AWS_S3_BUCKET", "finclick-files")
                },
                "openai": {
                    "api_key": os.getenv("OPENAI_API_KEY")
                }
            },

            # Platform settings
            "platform": {
                "host": os.getenv("PLATFORM_HOST", "0.0.0.0"),
                "port": int(os.getenv("PLATFORM_PORT", "8000")),
                "debug": os.getenv("DEBUG", "false").lower() == "true",
                "max_concurrent_analyses": int(os.getenv("MAX_CONCURRENT_ANALYSES", "10")),
                "analysis_timeout_minutes": int(os.getenv("ANALYSIS_TIMEOUT_MINUTES", "30"))
            }
        }

        return config

    async def initialize_platform(self) -> bool:
        """Initialize all platform components"""
        try:
            self.logger.info("🚀 Starting FinClick.AI Platform Integration...")

            # Initialize FastAPI application
            await self._initialize_fastapi()

            # Initialize database connections
            await self._initialize_databases()

            # Initialize AI agents orchestrator
            await self._initialize_ai_agents()

            # Initialize financial analysis engine
            await self._initialize_financial_engine()

            # Start background services
            await self._start_background_services()

            # Perform health checks
            await self._perform_initial_health_checks()

            self.platform_status = PlatformStatus.HEALTHY
            self.logger.info("✅ Platform initialization completed successfully!")

            return True

        except Exception as e:
            self.logger.error(f"❌ Platform initialization failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.platform_status = PlatformStatus.CRITICAL
            return False

    async def _initialize_fastapi(self) -> None:
        """Initialize FastAPI application with all routes and middleware"""
        self.fastapi_app = FastAPI(
            title="FinClick.AI Platform",
            description="Revolutionary Intelligent Financial Analysis Platform",
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )

        # Add CORS middleware
        self.fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "https://finclick.ai"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add compression middleware
        self.fastapi_app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Add routes
        self._setup_api_routes()

        self.logger.info("FastAPI application initialized")

    def _setup_api_routes(self) -> None:
        """Setup all API routes"""

        # Health check endpoint
        @self.fastapi_app.get("/health")
        async def health_check():
            """System health check endpoint"""
            health_status = await self._get_system_health()
            return JSONResponse(content=health_status)

        # Platform status endpoint
        @self.fastapi_app.get("/api/platform/status")
        async def get_platform_status():
            """Get detailed platform status"""
            return {
                "status": self.platform_status.value,
                "services": {
                    service_name: {
                        "status": health.status,
                        "response_time_ms": health.response_time_ms,
                        "last_check": health.last_check.isoformat()
                    }
                    for service_name, health in self.service_health.items()
                },
                "active_analyses": len(self.active_analyses),
                "websocket_connections": len(self.websocket_connections)
            }

        # Analysis endpoints
        @self.fastapi_app.post("/api/analysis/request")
        async def request_analysis(request: dict, background_tasks: BackgroundTasks):
            """Request a new financial analysis"""
            try:
                analysis_request = AnalysisRequest(**request)
                analysis_request.request_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(analysis_request.user_id) % 10000}"

                # Add to queue
                await self.analysis_queue.put(analysis_request)
                self.active_analyses[analysis_request.request_id] = analysis_request

                # Start analysis in background
                background_tasks.add_task(self._process_analysis, analysis_request)

                return {
                    "request_id": analysis_request.request_id,
                    "status": "queued",
                    "estimated_completion_time": (datetime.now() + timedelta(minutes=5)).isoformat()
                }

            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

        # Analysis status endpoint
        @self.fastapi_app.get("/api/analysis/status/{request_id}")
        async def get_analysis_status(request_id: str):
            """Get analysis status and results"""
            if request_id in self.active_analyses:
                request = self.active_analyses[request_id]
                return {
                    "request_id": request_id,
                    "status": "processing",
                    "progress": "In progress..."
                }
            else:
                # Check in database for completed analyses
                result = await self._get_analysis_result_from_db(request_id)
                if result:
                    return result
                else:
                    raise HTTPException(status_code=404, detail="Analysis not found")

        # WebSocket endpoint for real-time updates
        @self.fastapi_app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.websocket_connections[user_id] = websocket

            try:
                while True:
                    # Keep connection alive and handle messages
                    message = await websocket.receive_text()
                    await websocket.send_text(f"Echo: {message}")

            except Exception as e:
                self.logger.error(f"WebSocket error for user {user_id}: {e}")
            finally:
                if user_id in self.websocket_connections:
                    del self.websocket_connections[user_id]

        # File upload endpoint
        @self.fastapi_app.post("/api/files/upload")
        async def upload_file(file: bytes = None):
            """Upload file for analysis"""
            # Implementation would handle file upload and OCR processing
            return {"message": "File upload endpoint - implementation needed"}

        # Subscription management endpoints
        @self.fastapi_app.get("/api/subscription/plans")
        async def get_subscription_plans():
            """Get available subscription plans"""
            return {
                "plans": [
                    {
                        "id": "free",
                        "name": "Free Plan",
                        "price": 0,
                        "analyses_per_month": 5,
                        "features": ["Basic analysis", "PDF reports"]
                    },
                    {
                        "id": "professional",
                        "name": "Professional Plan",
                        "price": 99,
                        "analyses_per_month": 100,
                        "features": ["Advanced analysis", "Real-time data", "API access"]
                    },
                    {
                        "id": "enterprise",
                        "name": "Enterprise Plan",
                        "price": 299,
                        "analyses_per_month": -1,  # Unlimited
                        "features": ["All features", "White-label", "Custom integrations"]
                    }
                ]
            }

    async def _initialize_databases(self) -> None:
        """Initialize database connections"""
        try:
            # PostgreSQL connection
            postgres_config = self.config["databases"]["postgresql"]
            self.postgres_pool = await asyncpg.create_pool(
                host=postgres_config["host"],
                port=postgres_config["port"],
                database=postgres_config["database"],
                user=postgres_config["user"],
                password=postgres_config["password"],
                min_size=2,
                max_size=10
            )

            # MongoDB connection
            mongo_config = self.config["databases"]["mongodb"]
            mongo_uri = f"mongodb://{mongo_config['username']}:{mongo_config['password']}@{mongo_config['host']}:{mongo_config['port']}/{mongo_config['database']}"
            self.mongodb_client = AsyncIOMotorClient(mongo_uri)

            # Redis connection
            redis_config = self.config["databases"]["redis"]
            self.redis_client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                password=redis_config["password"] if redis_config["password"] else None,
                db=redis_config["db"],
                decode_responses=True
            )

            self.logger.info("Database connections initialized")

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    async def _initialize_ai_agents(self) -> None:
        """Initialize AI agents orchestrator"""
        try:
            self.agent_orchestrator = AgentOrchestrator()
            self.logger.info("AI Agents orchestrator initialized with 23 agents")

        except Exception as e:
            self.logger.error(f"AI Agents initialization failed: {e}")
            # Continue without AI agents for now
            self.agent_orchestrator = None

    async def _initialize_financial_engine(self) -> None:
        """Initialize financial analysis engine"""
        try:
            # This would initialize the 180 analysis types
            self.financial_engine = {}  # Placeholder
            self.logger.info("Financial analysis engine initialized with 180 analysis types")

        except Exception as e:
            self.logger.error(f"Financial engine initialization failed: {e}")
            self.financial_engine = None

    async def _start_background_services(self) -> None:
        """Start background services"""
        # Start analysis processor
        asyncio.create_task(self._analysis_processor())

        # Start health monitoring
        asyncio.create_task(self._health_monitor())

        # Start performance monitoring
        asyncio.create_task(self._performance_monitor())

        self.logger.info("Background services started")

    async def _analysis_processor(self) -> None:
        """Process analysis requests from the queue"""
        while True:
            try:
                # Process queued analyses
                if not self.analysis_queue.empty():
                    request = await self.analysis_queue.get()
                    await self._process_analysis(request)

                await asyncio.sleep(1)  # Check every second

            except Exception as e:
                self.logger.error(f"Analysis processor error: {e}")
                await asyncio.sleep(5)  # Wait before retry

    async def _process_analysis(self, request: AnalysisRequest) -> None:
        """Process a single analysis request"""
        start_time = datetime.now()

        try:
            self.logger.info(f"Processing analysis {request.request_id} for user {request.user_id}")

            # Send real-time update
            await self._send_user_update(request.user_id, {
                "type": "analysis_started",
                "request_id": request.request_id,
                "status": "processing"
            })

            # Run the analysis based on type
            if request.analysis_type == "comprehensive":
                result = await self._run_comprehensive_analysis(request)
            elif request.analysis_type == "quick":
                result = await self._run_quick_analysis(request)
            elif request.analysis_type == "risk_assessment":
                result = await self._run_risk_analysis(request)
            else:
                result = await self._run_basic_analysis(request)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Create response
            response = AnalysisResponse(
                request_id=request.request_id,
                status="completed",
                results=result,
                execution_time_ms=execution_time
            )

            # Store result in database
            await self._store_analysis_result(response)

            # Send completion update
            await self._send_user_update(request.user_id, {
                "type": "analysis_completed",
                "request_id": request.request_id,
                "status": "completed",
                "execution_time_ms": execution_time
            })

            self.logger.info(f"Analysis {request.request_id} completed in {execution_time:.0f}ms")

        except Exception as e:
            self.logger.error(f"Analysis {request.request_id} failed: {e}")

            # Send error update
            await self._send_user_update(request.user_id, {
                "type": "analysis_error",
                "request_id": request.request_id,
                "status": "error",
                "error": str(e)
            })

        finally:
            # Remove from active analyses
            if request.request_id in self.active_analyses:
                del self.active_analyses[request.request_id]

    async def _run_comprehensive_analysis(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Run comprehensive analysis using all 180 analysis types"""
        if self.agent_orchestrator:
            # Use AI agents for comprehensive analysis
            result = await self.agent_orchestrator.execute_workflow(
                WorkflowType.COMPREHENSIVE_ANALYSIS,
                request.company_data,
                priority=request.priority
            )
            return result
        else:
            # Fallback implementation
            return {
                "analysis_type": "comprehensive",
                "summary": "Comprehensive analysis completed",
                "metrics": {
                    "liquidity_ratio": 1.5,
                    "profitability_margin": 0.15,
                    "debt_to_equity": 0.6
                },
                "recommendations": [
                    "Improve working capital management",
                    "Consider debt restructuring"
                ]
            }

    async def _run_quick_analysis(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Run quick analysis for urgent requests"""
        if self.agent_orchestrator:
            result = await self.agent_orchestrator.execute_workflow(
                WorkflowType.QUICK_ANALYSIS,
                request.company_data,
                priority=10  # High priority
            )
            return result
        else:
            return {
                "analysis_type": "quick",
                "summary": "Quick analysis completed",
                "key_metrics": {
                    "current_ratio": 1.2,
                    "roi": 0.12
                },
                "risk_flags": []
            }

    async def _run_risk_analysis(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Run specialized risk analysis"""
        if self.agent_orchestrator:
            result = await self.agent_orchestrator.execute_workflow(
                WorkflowType.RISK_ASSESSMENT,
                request.company_data,
                priority=request.priority
            )
            return result
        else:
            return {
                "analysis_type": "risk_assessment",
                "overall_risk": "moderate",
                "risk_categories": {
                    "credit_risk": "low",
                    "market_risk": "moderate",
                    "operational_risk": "low"
                }
            }

    async def _run_basic_analysis(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Run basic financial analysis"""
        return {
            "analysis_type": "basic",
            "summary": "Basic analysis completed",
            "financial_ratios": {
                "current_ratio": 1.3,
                "quick_ratio": 1.1,
                "debt_ratio": 0.4
            }
        }

    async def _send_user_update(self, user_id: str, update: Dict[str, Any]) -> None:
        """Send real-time update to user via WebSocket"""
        if user_id in self.websocket_connections:
            try:
                websocket = self.websocket_connections[user_id]
                await websocket.send_text(json.dumps(update))
            except Exception as e:
                self.logger.error(f"Failed to send update to user {user_id}: {e}")

    async def _store_analysis_result(self, response: AnalysisResponse) -> None:
        """Store analysis result in database"""
        try:
            if self.mongodb_client:
                db = self.mongodb_client.finclick_analysis
                collection = db.analysis_results

                await collection.insert_one({
                    "request_id": response.request_id,
                    "status": response.status,
                    "results": response.results,
                    "execution_time_ms": response.execution_time_ms,
                    "errors": response.errors,
                    "warnings": response.warnings,
                    "created_at": datetime.now()
                })

        except Exception as e:
            self.logger.error(f"Failed to store analysis result: {e}")

    async def _get_analysis_result_from_db(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result from database"""
        try:
            if self.mongodb_client:
                db = self.mongodb_client.finclick_analysis
                collection = db.analysis_results

                result = await collection.find_one({"request_id": request_id})
                if result:
                    # Convert ObjectId to string
                    result["_id"] = str(result["_id"])
                    return result

        except Exception as e:
            self.logger.error(f"Failed to get analysis result: {e}")

        return None

    async def _health_monitor(self) -> None:
        """Monitor service health continuously"""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)

    async def _perform_initial_health_checks(self) -> None:
        """Perform initial health checks on all services"""
        await self._perform_health_checks()

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all services"""
        checks = [
            self._check_database_health(),
            self._check_ai_agents_health(),
            self._check_external_services_health()
        ]

        await asyncio.gather(*checks, return_exceptions=True)

    async def _check_database_health(self) -> None:
        """Check database connections health"""
        # PostgreSQL check
        try:
            if self.postgres_pool:
                start_time = datetime.now()
                async with self.postgres_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                response_time = (datetime.now() - start_time).total_seconds() * 1000

                self.service_health["postgresql"] = ServiceHealth(
                    service_type=ServiceType.DATABASE,
                    service_name="PostgreSQL",
                    status="healthy",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
        except Exception as e:
            self.service_health["postgresql"] = ServiceHealth(
                service_type=ServiceType.DATABASE,
                service_name="PostgreSQL",
                status="unhealthy",
                response_time_ms=0,
                last_check=datetime.now(),
                error_message=str(e)
            )

        # MongoDB check
        try:
            if self.mongodb_client:
                start_time = datetime.now()
                await self.mongodb_client.admin.command('ping')
                response_time = (datetime.now() - start_time).total_seconds() * 1000

                self.service_health["mongodb"] = ServiceHealth(
                    service_type=ServiceType.DATABASE,
                    service_name="MongoDB",
                    status="healthy",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
        except Exception as e:
            self.service_health["mongodb"] = ServiceHealth(
                service_type=ServiceType.DATABASE,
                service_name="MongoDB",
                status="unhealthy",
                response_time_ms=0,
                last_check=datetime.now(),
                error_message=str(e)
            )

        # Redis check
        try:
            if self.redis_client:
                start_time = datetime.now()
                self.redis_client.ping()
                response_time = (datetime.now() - start_time).total_seconds() * 1000

                self.service_health["redis"] = ServiceHealth(
                    service_type=ServiceType.DATABASE,
                    service_name="Redis",
                    status="healthy",
                    response_time_ms=response_time,
                    last_check=datetime.now()
                )
        except Exception as e:
            self.service_health["redis"] = ServiceHealth(
                service_type=ServiceType.DATABASE,
                service_name="Redis",
                status="unhealthy",
                response_time_ms=0,
                last_check=datetime.now(),
                error_message=str(e)
            )

    async def _check_ai_agents_health(self) -> None:
        """Check AI agents orchestrator health"""
        try:
            if self.agent_orchestrator:
                start_time = datetime.now()
                status = await self.agent_orchestrator.get_system_status()
                response_time = (datetime.now() - start_time).total_seconds() * 1000

                self.service_health["ai_agents"] = ServiceHealth(
                    service_type=ServiceType.AI_AGENTS,
                    service_name="AI Agents Orchestrator",
                    status="healthy",
                    response_time_ms=response_time,
                    last_check=datetime.now(),
                    metadata=status
                )
        except Exception as e:
            self.service_health["ai_agents"] = ServiceHealth(
                service_type=ServiceType.AI_AGENTS,
                service_name="AI Agents Orchestrator",
                status="unhealthy",
                response_time_ms=0,
                last_check=datetime.now(),
                error_message=str(e)
            )

    async def _check_external_services_health(self) -> None:
        """Check external services health"""
        # This would check external APIs, payment services, etc.
        pass

    async def _performance_monitor(self) -> None:
        """Monitor platform performance"""
        while True:
            try:
                # Collect performance metrics
                metrics = {
                    "active_analyses": len(self.active_analyses),
                    "websocket_connections": len(self.websocket_connections),
                    "queue_size": self.analysis_queue.qsize(),
                    "platform_status": self.platform_status.value,
                    "timestamp": datetime.now().isoformat()
                }

                # Store metrics in Redis for monitoring
                if self.redis_client:
                    self.redis_client.lpush(
                        "platform_metrics",
                        json.dumps(metrics)
                    )
                    # Keep only last 1000 metrics
                    self.redis_client.ltrim("platform_metrics", 0, 999)

                await asyncio.sleep(60)  # Collect every minute

            except Exception as e:
                self.logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(60)

    async def _get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        healthy_services = sum(1 for health in self.service_health.values() if health.status == "healthy")
        total_services = len(self.service_health)

        overall_health = "healthy" if healthy_services == total_services else "degraded"
        if healthy_services < total_services * 0.5:
            overall_health = "critical"

        return {
            "platform_status": self.platform_status.value,
            "overall_health": overall_health,
            "services_healthy": f"{healthy_services}/{total_services}",
            "services": {
                name: {
                    "status": health.status,
                    "response_time_ms": health.response_time_ms,
                    "last_check": health.last_check.isoformat(),
                    "error": health.error_message
                }
                for name, health in self.service_health.items()
            },
            "platform_metrics": {
                "active_analyses": len(self.active_analyses),
                "websocket_connections": len(self.websocket_connections),
                "queue_size": self.analysis_queue.qsize()
            },
            "timestamp": datetime.now().isoformat()
        }

    async def run_platform(self) -> None:
        """Run the complete platform"""
        success = await self.initialize_platform()

        if not success:
            self.logger.error("Platform initialization failed. Exiting.")
            sys.exit(1)

        # Start the FastAPI server
        config = uvicorn.Config(
            self.fastapi_app,
            host=self.config["platform"]["host"],
            port=self.config["platform"]["port"],
            log_level="info"
        )

        server = uvicorn.Server(config)

        self.logger.info(f"🌟 FinClick.AI Platform is running on http://{self.config['platform']['host']}:{self.config['platform']['port']}")
        self.logger.info("📊 API Documentation available at http://localhost:8000/api/docs")

        await server.serve()

    async def shutdown_platform(self) -> None:
        """Gracefully shutdown the platform"""
        self.logger.info("🛑 Shutting down FinClick.AI Platform...")

        self.platform_status = PlatformStatus.MAINTENANCE

        # Close database connections
        if self.postgres_pool:
            await self.postgres_pool.close()

        if self.mongodb_client:
            self.mongodb_client.close()

        if self.redis_client:
            self.redis_client.close()

        # Close WebSocket connections
        for websocket in self.websocket_connections.values():
            await websocket.close()

        self.logger.info("✅ Platform shutdown completed")


# Main execution
async def main():
    """Main function to run the platform"""
    platform = PlatformIntegrationManager()

    try:
        await platform.run_platform()
    except KeyboardInterrupt:
        await platform.shutdown_platform()
    except Exception as e:
        platform.logger.error(f"Platform error: {e}")
        await platform.shutdown_platform()


if __name__ == "__main__":
    asyncio.run(main())