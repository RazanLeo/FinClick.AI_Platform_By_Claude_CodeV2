"""
Integration Agent
وكيل التكامل مع الأنظمة الخارجية

This agent manages integration with external systems, APIs, databases,
and third-party financial data providers for the FinClick.AI platform.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import aiohttp
import time

from ..core.agent_base import FinancialAgent, AgentType, AgentTask


class IntegrationType(Enum):
    """Types of external integrations"""
    REST_API = "rest_api"
    DATABASE = "database"
    FILE_IMPORT = "file_import"
    STREAMING_DATA = "streaming_data"
    WEBHOOK = "webhook"
    FTP_SFTP = "ftp_sftp"


class DataProvider(Enum):
    """External data providers"""
    BLOOMBERG = "bloomberg"
    REFINITIV = "refinitiv"
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    SAUDI_EXCHANGE = "saudi_exchange"
    SAMA = "sama"
    CMA = "cma"
    BANK_SYSTEMS = "bank_systems"


@dataclass
class IntegrationConfig:
    """Integration configuration"""
    provider: DataProvider
    integration_type: IntegrationType
    endpoint_url: str
    authentication: Dict[str, str]
    data_format: str  # json, xml, csv, etc.
    update_frequency: str  # real_time, hourly, daily, etc.
    retry_policy: Dict[str, Any]
    rate_limits: Dict[str, int]


class IntegrationAgent(FinancialAgent):
    """
    Specialized agent for external systems integration
    وكيل متخصص في التكامل مع الأنظمة الخارجية
    """

    def __init__(self, agent_id: str = "integration_agent",
                 agent_name_ar: str = "وكيل التكامل مع الأنظمة الخارجية",
                 agent_name_en: str = "Integration Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'INTEGRATION', 'integration')
        )

        self.integrations = self._initialize_integrations()
        self.connection_pool = {}
        self.data_cache = {}
        self.api_call_history = []

    def _initialize_capabilities(self) -> None:
        """Initialize integration capabilities"""
        self.capabilities = {
            "data_providers": {
                "financial_data": True,
                "market_data": True,
                "economic_indicators": True,
                "regulatory_data": True,
                "news_feeds": True,
                "company_fundamentals": True
            },
            "integration_types": {
                "rest_api": True,
                "database_connections": True,
                "file_transfers": True,
                "streaming_data": True,
                "webhook_handlers": True
            },
            "data_formats": {
                "json": True,
                "xml": True,
                "csv": True,
                "excel": True,
                "pdf": True,
                "fixed_width": True
            },
            "authentication": {
                "api_keys": True,
                "oauth2": True,
                "basic_auth": True,
                "bearer_tokens": True,
                "certificates": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_integrations(self) -> Dict[str, IntegrationConfig]:
        """Initialize integration configurations"""
        return {
            "bloomberg_api": IntegrationConfig(
                provider=DataProvider.BLOOMBERG,
                integration_type=IntegrationType.REST_API,
                endpoint_url="https://api.bloomberg.com/v1/",
                authentication={"type": "api_key", "key": "BLOOMBERG_API_KEY"},
                data_format="json",
                update_frequency="real_time",
                retry_policy={"max_retries": 3, "backoff_factor": 2},
                rate_limits={"requests_per_minute": 100, "requests_per_hour": 1000}
            ),
            "refinitiv_eikon": IntegrationConfig(
                provider=DataProvider.REFINITIV,
                integration_type=IntegrationType.REST_API,
                endpoint_url="https://api.refinitiv.com/data/",
                authentication={"type": "oauth2", "client_id": "REFINITIV_CLIENT_ID"},
                data_format="json",
                update_frequency="real_time",
                retry_policy={"max_retries": 3, "backoff_factor": 1.5},
                rate_limits={"requests_per_minute": 200, "requests_per_hour": 2000}
            ),
            "saudi_exchange": IntegrationConfig(
                provider=DataProvider.SAUDI_EXCHANGE,
                integration_type=IntegrationType.REST_API,
                endpoint_url="https://www.saudiexchange.sa/wps/portal/tadawul/",
                authentication={"type": "api_key", "key": "TADAWUL_API_KEY"},
                data_format="json",
                update_frequency="real_time",
                retry_policy={"max_retries": 5, "backoff_factor": 1},
                rate_limits={"requests_per_minute": 60, "requests_per_hour": 500}
            ),
            "sama_data": IntegrationConfig(
                provider=DataProvider.SAMA,
                integration_type=IntegrationType.FILE_IMPORT,
                endpoint_url="https://www.sama.gov.sa/en-US/EconomicReports/",
                authentication={"type": "none"},
                data_format="excel",
                update_frequency="daily",
                retry_policy={"max_retries": 3, "backoff_factor": 2},
                rate_limits={"requests_per_hour": 24}
            ),
            "bank_core_system": IntegrationConfig(
                provider=DataProvider.BANK_SYSTEMS,
                integration_type=IntegrationType.DATABASE,
                endpoint_url="jdbc:oracle:thin:@bank-db:1521:prod",
                authentication={"type": "basic_auth", "username": "finclick_user"},
                data_format="sql_result",
                update_frequency="real_time",
                retry_policy={"max_retries": 2, "backoff_factor": 1},
                rate_limits={"queries_per_minute": 30}
            )
        }

    async def fetch_data(self, provider: DataProvider, data_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data from external provider
        جلب البيانات من مزود خارجي
        """
        try:
            provider_config = self._get_provider_config(provider)
            if not provider_config:
                return {"error": f"Provider {provider.value} not configured"}

            # Check rate limits
            rate_limit_check = await self._check_rate_limits(provider)
            if not rate_limit_check["allowed"]:
                return {"error": "Rate limit exceeded", "retry_after": rate_limit_check["retry_after"]}

            # Execute data fetch based on integration type
            if provider_config.integration_type == IntegrationType.REST_API:
                result = await self._fetch_rest_api_data(provider_config, data_request)
            elif provider_config.integration_type == IntegrationType.DATABASE:
                result = await self._fetch_database_data(provider_config, data_request)
            elif provider_config.integration_type == IntegrationType.FILE_IMPORT:
                result = await self._fetch_file_data(provider_config, data_request)
            else:
                return {"error": f"Integration type {provider_config.integration_type.value} not implemented"}

            # Log API call
            await self._log_api_call(provider, data_request, result)

            # Cache result if successful
            if "error" not in result:
                await self._cache_data(provider, data_request, result)

            return result

        except Exception as e:
            return {"error": f"Data fetch failed: {str(e)}"}

    def _get_provider_config(self, provider: DataProvider) -> Optional[IntegrationConfig]:
        """Get configuration for specific provider"""
        provider_mapping = {
            DataProvider.BLOOMBERG: "bloomberg_api",
            DataProvider.REFINITIV: "refinitiv_eikon",
            DataProvider.SAUDI_EXCHANGE: "saudi_exchange",
            DataProvider.SAMA: "sama_data",
            DataProvider.BANK_SYSTEMS: "bank_core_system"
        }

        config_key = provider_mapping.get(provider)
        return self.integrations.get(config_key) if config_key else None

    async def _check_rate_limits(self, provider: DataProvider) -> Dict[str, Any]:
        """Check rate limits for provider"""
        # Simple rate limiting implementation
        current_time = time.time()
        provider_calls = [
            call for call in self.api_call_history
            if call["provider"] == provider.value and current_time - call["timestamp"] < 3600  # Last hour
        ]

        config = self._get_provider_config(provider)
        hourly_limit = config.rate_limits.get("requests_per_hour", 1000) if config else 1000

        if len(provider_calls) >= hourly_limit:
            return {
                "allowed": False,
                "retry_after": 3600 - (current_time - min(call["timestamp"] for call in provider_calls))
            }

        return {"allowed": True}

    async def _fetch_rest_api_data(self, config: IntegrationConfig, request: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from REST API"""
        try:
            # Prepare authentication headers
            headers = await self._prepare_auth_headers(config)

            # Build request URL
            endpoint = request.get("endpoint", "")
            url = f"{config.endpoint_url.rstrip('/')}/{endpoint.lstrip('/')}"

            # Add query parameters
            params = request.get("parameters", {})

            # Mock API call (in real implementation, would use actual HTTP client)
            await asyncio.sleep(0.1)  # Simulate network delay

            # Simulate successful API response
            mock_data = {
                "status": "success",
                "data": {
                    "symbol": params.get("symbol", "UNKNOWN"),
                    "price": 125.50,
                    "currency": "SAR",
                    "timestamp": datetime.now().isoformat(),
                    "provider": config.provider.value
                },
                "metadata": {
                    "request_id": f"req_{int(time.time())}",
                    "response_time_ms": 150,
                    "data_points": 1
                }
            }

            return mock_data

        except Exception as e:
            return {"error": f"REST API call failed: {str(e)}"}

    async def _fetch_database_data(self, config: IntegrationConfig, request: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from database"""
        try:
            query = request.get("query", "")
            parameters = request.get("parameters", {})

            # Mock database query (in real implementation, would use actual DB connection)
            await asyncio.sleep(0.05)  # Simulate query execution

            mock_result = {
                "status": "success",
                "data": [
                    {"account_id": "ACC001", "balance": 1500000.00, "currency": "SAR"},
                    {"account_id": "ACC002", "balance": 2300000.00, "currency": "SAR"}
                ],
                "metadata": {
                    "rows_returned": 2,
                    "execution_time_ms": 45,
                    "query_hash": "db_query_123"
                }
            }

            return mock_result

        except Exception as e:
            return {"error": f"Database query failed: {str(e)}"}

    async def _fetch_file_data(self, config: IntegrationConfig, request: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from file source"""
        try:
            file_path = request.get("file_path", "")
            file_type = request.get("file_type", config.data_format)

            # Mock file processing
            await asyncio.sleep(0.2)  # Simulate file processing

            mock_result = {
                "status": "success",
                "data": {
                    "economic_indicators": {
                        "gdp_growth": 0.032,
                        "inflation_rate": 0.025,
                        "unemployment_rate": 0.049
                    }
                },
                "metadata": {
                    "file_name": file_path,
                    "file_size_bytes": 1024000,
                    "records_processed": 100,
                    "processing_time_ms": 180
                }
            }

            return mock_result

        except Exception as e:
            return {"error": f"File processing failed: {str(e)}"}

    async def _prepare_auth_headers(self, config: IntegrationConfig) -> Dict[str, str]:
        """Prepare authentication headers"""
        headers = {"Content-Type": "application/json"}

        auth_type = config.authentication.get("type", "none")

        if auth_type == "api_key":
            api_key = config.authentication.get("key", "")
            headers["X-API-Key"] = api_key
        elif auth_type == "bearer_token":
            token = config.authentication.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "basic_auth":
            username = config.authentication.get("username", "")
            password = config.authentication.get("password", "")
            # Would encode credentials in real implementation
            headers["Authorization"] = f"Basic {username}:{password}"

        return headers

    async def _log_api_call(self, provider: DataProvider, request: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Log API call for monitoring and rate limiting"""
        log_entry = {
            "timestamp": time.time(),
            "provider": provider.value,
            "request": request,
            "success": "error" not in response,
            "response_time": response.get("metadata", {}).get("response_time_ms", 0),
            "data_points": response.get("metadata", {}).get("data_points", 0)
        }

        self.api_call_history.append(log_entry)

        # Keep only recent history (last 24 hours)
        cutoff_time = time.time() - 86400
        self.api_call_history = [
            call for call in self.api_call_history
            if call["timestamp"] > cutoff_time
        ]

    async def _cache_data(self, provider: DataProvider, request: Dict[str, Any], data: Dict[str, Any]) -> None:
        """Cache fetched data"""
        cache_key = f"{provider.value}_{hash(str(request))}"

        self.data_cache[cache_key] = {
            "data": data,
            "timestamp": time.time(),
            "ttl": 300  # 5 minutes default TTL
        }

    async def get_cached_data(self, provider: DataProvider, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve cached data if available and valid"""
        cache_key = f"{provider.value}_{hash(str(request))}"
        cached_entry = self.data_cache.get(cache_key)

        if cached_entry:
            if time.time() - cached_entry["timestamp"] < cached_entry["ttl"]:
                return cached_entry["data"]
            else:
                # Remove expired cache entry
                del self.data_cache[cache_key]

        return None

    async def setup_data_stream(self, provider: DataProvider, stream_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Setup real-time data streaming
        إعداد تدفق البيانات في الوقت الفعلي
        """
        try:
            stream_id = f"stream_{provider.value}_{int(time.time())}"

            # Mock stream setup
            stream_info = {
                "stream_id": stream_id,
                "provider": provider.value,
                "status": "active",
                "data_types": stream_config.get("data_types", []),
                "symbols": stream_config.get("symbols", []),
                "update_frequency": stream_config.get("frequency", "real_time"),
                "created_at": datetime.now().isoformat()
            }

            return {
                "status": "success",
                "stream_info": stream_info,
                "message": f"Data stream {stream_id} created successfully"
            }

        except Exception as e:
            return {"error": f"Stream setup failed: {str(e)}"}

    async def test_connection(self, provider: DataProvider) -> Dict[str, Any]:
        """
        Test connection to external provider
        اختبار الاتصال مع المزود الخارجي
        """
        try:
            config = self._get_provider_config(provider)
            if not config:
                return {"error": f"Provider {provider.value} not configured"}

            start_time = time.time()

            # Mock connection test
            await asyncio.sleep(0.1)  # Simulate connection test

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            test_result = {
                "provider": provider.value,
                "connection_status": "success",
                "response_time_ms": response_time,
                "endpoint": config.endpoint_url,
                "authentication_status": "valid",
                "test_timestamp": datetime.now().isoformat()
            }

            return test_result

        except Exception as e:
            return {
                "provider": provider.value,
                "connection_status": "failed",
                "error": str(e),
                "test_timestamp": datetime.now().isoformat()
            }

    async def get_integration_status(self) -> Dict[str, Any]:
        """
        Get status of all integrations
        الحصول على حالة جميع التكاملات
        """
        try:
            status_report = {
                "report_timestamp": datetime.now().isoformat(),
                "total_integrations": len(self.integrations),
                "integration_status": {},
                "api_usage_summary": {},
                "cache_statistics": {}
            }

            # Test each integration
            for integration_name, config in self.integrations.items():
                test_result = await self.test_connection(config.provider)
                status_report["integration_status"][integration_name] = {
                    "provider": config.provider.value,
                    "type": config.integration_type.value,
                    "status": test_result.get("connection_status", "unknown"),
                    "last_tested": test_result.get("test_timestamp", ""),
                    "response_time": test_result.get("response_time_ms", 0)
                }

            # API usage summary
            recent_calls = [
                call for call in self.api_call_history
                if time.time() - call["timestamp"] < 3600  # Last hour
            ]

            status_report["api_usage_summary"] = {
                "calls_last_hour": len(recent_calls),
                "successful_calls": len([call for call in recent_calls if call["success"]]),
                "failed_calls": len([call for call in recent_calls if not call["success"]]),
                "average_response_time": sum(call["response_time"] for call in recent_calls) / len(recent_calls) if recent_calls else 0
            }

            # Cache statistics
            valid_cache_entries = sum(
                1 for entry in self.data_cache.values()
                if time.time() - entry["timestamp"] < entry["ttl"]
            )

            status_report["cache_statistics"] = {
                "total_cache_entries": len(self.data_cache),
                "valid_cache_entries": valid_cache_entries,
                "cache_hit_rate": 0.85  # Mock cache hit rate
            }

            return status_report

        except Exception as e:
            return {"error": f"Status report generation failed: {str(e)}"}

    async def configure_integration(self, provider: DataProvider, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure or update integration settings
        تكوين أو تحديث إعدادات التكامل
        """
        try:
            # Create new integration configuration
            new_config = IntegrationConfig(
                provider=provider,
                integration_type=IntegrationType(configuration.get("integration_type", "rest_api")),
                endpoint_url=configuration.get("endpoint_url", ""),
                authentication=configuration.get("authentication", {}),
                data_format=configuration.get("data_format", "json"),
                update_frequency=configuration.get("update_frequency", "hourly"),
                retry_policy=configuration.get("retry_policy", {"max_retries": 3, "backoff_factor": 2}),
                rate_limits=configuration.get("rate_limits", {"requests_per_minute": 60, "requests_per_hour": 1000})
            )

            # Store configuration
            config_key = f"{provider.value}_integration"
            self.integrations[config_key] = new_config

            # Test the new configuration
            test_result = await self.test_connection(provider)

            return {
                "status": "success",
                "provider": provider.value,
                "configuration_updated": True,
                "connection_test": test_result,
                "updated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Integration configuration failed: {str(e)}"}

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process integration tasks"""
        try:
            task_type = task.task_data.get("type", "fetch_data")

            if task_type == "fetch_data":
                provider = DataProvider(task.task_data.get("provider", "yahoo_finance"))
                data_request = task.task_data.get("data_request", {})

                # Check cache first
                cached_data = await self.get_cached_data(provider, data_request)
                if cached_data:
                    return {"status": "success", "source": "cache", "data": cached_data}

                return await self.fetch_data(provider, data_request)

            elif task_type == "test_connection":
                provider = DataProvider(task.task_data.get("provider", "yahoo_finance"))
                return await self.test_connection(provider)

            elif task_type == "setup_stream":
                provider = DataProvider(task.task_data.get("provider", "bloomberg"))
                stream_config = task.task_data.get("stream_config", {})
                return await self.setup_data_stream(provider, stream_config)

            elif task_type == "get_status":
                return await self.get_integration_status()

            elif task_type == "configure_integration":
                provider = DataProvider(task.task_data.get("provider"))
                configuration = task.task_data.get("configuration", {})
                return await self.configure_integration(provider, configuration)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}