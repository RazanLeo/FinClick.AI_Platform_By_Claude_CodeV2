"""
Security Agent
وكيل الأمان والحماية

This agent handles security monitoring, access control, threat detection,
and compliance with cybersecurity frameworks for the FinClick.AI platform.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import uuid

from ..core.agent_base import FinancialAgent, AgentType, AgentTask


class SecurityThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(Enum):
    """Types of security events"""
    LOGIN_ATTEMPT = "login_attempt"
    FAILED_LOGIN = "failed_login"
    DATA_ACCESS = "data_access"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXPORT = "data_export"
    SYSTEM_BREACH = "system_breach"
    MALWARE_DETECTION = "malware_detection"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"


@dataclass
class SecurityIncident:
    """Security incident record"""
    incident_id: str
    event_type: SecurityEvent
    threat_level: SecurityThreatLevel
    description: str
    affected_resources: List[str]
    source_ip: Optional[str]
    user_id: Optional[str]
    timestamp: datetime
    status: str  # open, investigating, resolved
    mitigation_actions: List[str]


class SecurityAgent(FinancialAgent):
    """
    Specialized agent for security and protection
    وكيل متخصص في الأمان والحماية
    """

    def __init__(self, agent_id: str = "security_agent",
                 agent_name_ar: str = "وكيل الأمان والحماية",
                 agent_name_en: str = "Security Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'SECURITY', 'security')
        )

        self.security_incidents = []
        self.access_logs = []
        self.security_policies = self._initialize_security_policies()
        self.threat_intelligence = self._initialize_threat_intelligence()

    def _initialize_capabilities(self) -> None:
        """Initialize security capabilities"""
        self.capabilities = {
            "security_monitoring": {
                "access_control": True,
                "threat_detection": True,
                "anomaly_detection": True,
                "audit_logging": True,
                "incident_response": True
            },
            "compliance_frameworks": {
                "iso_27001": True,
                "nist_cybersecurity": True,
                "sama_cybersecurity": True,
                "gdpr_compliance": True,
                "pci_dss": True
            },
            "protection_mechanisms": {
                "data_encryption": True,
                "access_authentication": True,
                "session_management": True,
                "input_validation": True,
                "output_sanitization": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_security_policies(self) -> Dict[str, Any]:
        """Initialize security policies and rules"""
        return {
            "access_control": {
                "max_failed_login_attempts": 5,
                "account_lockout_duration": 30,  # minutes
                "session_timeout": 60,  # minutes
                "password_policy": {
                    "min_length": 12,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special_chars": True
                }
            },
            "data_protection": {
                "encryption_required": True,
                "data_classification_levels": ["public", "internal", "confidential", "restricted"],
                "retention_policy": {
                    "financial_data": 2555,  # days (7 years)
                    "audit_logs": 365,
                    "session_logs": 90
                }
            },
            "monitoring": {
                "log_all_access": True,
                "monitor_data_exports": True,
                "alert_on_anomalies": True,
                "real_time_monitoring": True
            }
        }

    def _initialize_threat_intelligence(self) -> Dict[str, Any]:
        """Initialize threat intelligence data"""
        return {
            "known_malicious_ips": [],
            "suspicious_patterns": [
                "multiple_failed_logins",
                "unusual_data_access_patterns",
                "off_hours_access",
                "geographic_anomalies",
                "privilege_escalation_attempts"
            ],
            "attack_signatures": {
                "sql_injection": ["union select", "drop table", "-- "],
                "xss_attack": ["<script>", "javascript:", "onerror="],
                "path_traversal": ["../", "..\\\\"]
            }
        }

    async def monitor_security_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor and analyze security events
        مراقبة وتحليل الأحداث الأمنية
        """
        try:
            event_type = SecurityEvent(event_data.get("event_type", "data_access"))
            user_id = event_data.get("user_id")
            source_ip = event_data.get("source_ip")
            resource = event_data.get("resource")
            timestamp = datetime.now()

            # Log the event
            self.access_logs.append({
                "timestamp": timestamp.isoformat(),
                "event_type": event_type.value,
                "user_id": user_id,
                "source_ip": source_ip,
                "resource": resource,
                "details": event_data
            })

            # Analyze threat level
            threat_assessment = await self._assess_threat_level(event_data)
            
            # Generate security response
            response = {
                "event_id": str(uuid.uuid4()),
                "timestamp": timestamp.isoformat(),
                "event_type": event_type.value,
                "threat_level": threat_assessment["threat_level"],
                "risk_score": threat_assessment["risk_score"],
                "allowed": threat_assessment["allowed"],
                "security_actions": threat_assessment["actions"],
                "monitoring_flags": threat_assessment["flags"]
            }

            # Create incident if high threat
            if threat_assessment["threat_level"] in ["high", "critical"]:
                incident = await self._create_security_incident(event_data, threat_assessment)
                response["incident_id"] = incident["incident_id"]

            return response

        except Exception as e:
            return {"error": f"Security monitoring failed: {str(e)}"}

    async def _assess_threat_level(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess threat level of security event"""
        risk_score = 0
        threat_indicators = []
        actions = []
        flags = []

        user_id = event_data.get("user_id")
        source_ip = event_data.get("source_ip")
        event_type = event_data.get("event_type")

        # Check for failed login patterns
        if event_type == "failed_login":
            recent_failures = len([
                log for log in self.access_logs[-50:]
                if (log.get("user_id") == user_id and 
                    log.get("event_type") == "failed_login" and
                    datetime.fromisoformat(log["timestamp"]) > datetime.now() - timedelta(minutes=15))
            ])
            
            if recent_failures >= 3:
                risk_score += 30
                threat_indicators.append("multiple_failed_login_attempts")
                
            if recent_failures >= 5:
                risk_score += 50
                actions.append("account_lockout")
                flags.append("brute_force_attack")

        # Check for suspicious IP
        if source_ip in self.threat_intelligence["known_malicious_ips"]:
            risk_score += 80
            threat_indicators.append("known_malicious_ip")
            actions.append("block_ip")

        # Check for unusual access patterns
        if event_type == "data_access":
            # Check for off-hours access
            current_hour = datetime.now().hour
            if current_hour < 6 or current_hour > 22:
                risk_score += 15
                threat_indicators.append("off_hours_access")

            # Check for bulk data access
            resource_count = event_data.get("resource_count", 1)
            if resource_count > 100:
                risk_score += 25
                threat_indicators.append("bulk_data_access")
                flags.append("potential_data_exfiltration")

        # Determine threat level
        if risk_score >= 80:
            threat_level = "critical"
            allowed = False
        elif risk_score >= 60:
            threat_level = "high"
            allowed = False
        elif risk_score >= 30:
            threat_level = "medium"
            allowed = True
            actions.append("additional_monitoring")
        else:
            threat_level = "low"
            allowed = True

        return {
            "threat_level": threat_level,
            "risk_score": risk_score,
            "allowed": allowed,
            "threat_indicators": threat_indicators,
            "actions": actions,
            "flags": flags
        }

    async def _create_security_incident(self, event_data: Dict[str, Any], 
                                      threat_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Create security incident record"""
        incident_id = f"sec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        incident = SecurityIncident(
            incident_id=incident_id,
            event_type=SecurityEvent(event_data.get("event_type")),
            threat_level=SecurityThreatLevel(threat_assessment["threat_level"]),
            description=f"Security incident: {threat_assessment['threat_indicators']}",
            affected_resources=[event_data.get("resource", "unknown")],
            source_ip=event_data.get("source_ip"),
            user_id=event_data.get("user_id"),
            timestamp=datetime.now(),
            status="open",
            mitigation_actions=threat_assessment["actions"]
        )
        
        self.security_incidents.append(incident)
        
        return {"incident_id": incident_id, "status": "created"}

    async def validate_access_request(self, access_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate access request against security policies
        التحقق من طلب الوصول وفقاً لسياسات الأمان
        """
        try:
            user_id = access_request.get("user_id")
            resource = access_request.get("resource")
            action = access_request.get("action")
            
            validation_result = {
                "access_granted": False,
                "validation_checks": [],
                "security_requirements": [],
                "additional_authentication": False
            }

            # Check user authentication status
            auth_check = await self._verify_user_authentication(user_id)
            validation_result["validation_checks"].append(auth_check)
            
            if not auth_check["valid"]:
                validation_result["security_requirements"].append("user_authentication_required")
                return validation_result

            # Check resource permissions
            permission_check = await self._check_resource_permissions(user_id, resource, action)
            validation_result["validation_checks"].append(permission_check)
            
            if not permission_check["valid"]:
                validation_result["security_requirements"].append("insufficient_permissions")
                return validation_result

            # Check for sensitive data access
            if self._is_sensitive_resource(resource):
                validation_result["additional_authentication"] = True
                validation_result["security_requirements"].append("mfa_required")

            # All checks passed
            validation_result["access_granted"] = True
            
            return validation_result

        except Exception as e:
            return {"error": f"Access validation failed: {str(e)}"}

    async def _verify_user_authentication(self, user_id: str) -> Dict[str, Any]:
        """Verify user authentication status"""
        # Mock implementation - in real system would check session/token
        return {
            "check_type": "user_authentication",
            "valid": True,  # Assume valid for demo
            "details": f"User {user_id} authenticated"
        }

    async def _check_resource_permissions(self, user_id: str, resource: str, action: str) -> Dict[str, Any]:
        """Check user permissions for resource and action"""
        # Mock implementation - in real system would check RBAC
        return {
            "check_type": "resource_permissions",
            "valid": True,  # Assume valid for demo
            "details": f"User {user_id} has {action} permission on {resource}"
        }

    def _is_sensitive_resource(self, resource: str) -> bool:
        """Check if resource contains sensitive data"""
        sensitive_keywords = ["financial_data", "personal_info", "bank_account", "ssn", "tax_id"]
        return any(keyword in resource.lower() for keyword in sensitive_keywords)

    async def generate_security_report(self, report_period_days: int = 30) -> Dict[str, Any]:
        """
        Generate security monitoring report
        إنشاء تقرير مراقبة الأمان
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=report_period_days)
            
            # Filter logs for report period
            period_logs = [
                log for log in self.access_logs
                if start_date <= datetime.fromisoformat(log["timestamp"]) <= end_date
            ]
            
            # Filter incidents for report period
            period_incidents = [
                incident for incident in self.security_incidents
                if start_date <= incident.timestamp <= end_date
            ]

            report = {
                "report_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": report_period_days
                },
                "summary_statistics": {
                    "total_events": len(period_logs),
                    "security_incidents": len(period_incidents),
                    "failed_login_attempts": len([log for log in period_logs if log["event_type"] == "failed_login"]),
                    "data_access_events": len([log for log in period_logs if log["event_type"] == "data_access"]),
                    "blocked_attempts": len([log for log in period_logs if "block" in str(log.get("details", {}))])
                },
                "incident_breakdown": {
                    "critical": len([i for i in period_incidents if i.threat_level == SecurityThreatLevel.CRITICAL]),
                    "high": len([i for i in period_incidents if i.threat_level == SecurityThreatLevel.HIGH]),
                    "medium": len([i for i in period_incidents if i.threat_level == SecurityThreatLevel.MEDIUM]),
                    "low": len([i for i in period_incidents if i.threat_level == SecurityThreatLevel.LOW])
                },
                "top_security_events": self._get_top_security_events(period_logs),
                "recommendations": self._generate_security_recommendations(period_logs, period_incidents)
            }

            return report

        except Exception as e:
            return {"error": f"Security report generation failed: {str(e)}"}

    def _get_top_security_events(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top security events by frequency"""
        event_counts = {}
        for log in logs:
            event_type = log.get("event_type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return [
            {"event_type": event_type, "count": count}
            for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]

    def _generate_security_recommendations(self, logs: List[Dict[str, Any]], 
                                         incidents: List[SecurityIncident]) -> List[str]:
        """Generate security recommendations based on analysis"""
        recommendations = []
        
        # High number of failed logins
        failed_logins = len([log for log in logs if log["event_type"] == "failed_login"])
        if failed_logins > 50:
            recommendations.append("تعزيز سياسة كلمات المرور وتفعيل المصادقة الثنائية")
        
        # High severity incidents
        critical_incidents = len([i for i in incidents if i.threat_level == SecurityThreatLevel.CRITICAL])
        if critical_incidents > 0:
            recommendations.append("مراجعة فورية لضوابط الأمان وتحديث الاستراتيجية الأمنية")
        
        # Off-hours access
        off_hours_access = len([log for log in logs 
                               if datetime.fromisoformat(log["timestamp"]).hour < 6 or 
                                  datetime.fromisoformat(log["timestamp"]).hour > 22])
        if off_hours_access > 20:
            recommendations.append("تعزيز مراقبة الوصول خارج ساعات العمل")
        
        if not recommendations:
            recommendations.append("الوضع الأمني مستقر - المتابعة الدورية مطلوبة")
        
        return recommendations

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process security tasks"""
        try:
            task_type = task.task_data.get("type", "monitor_event")

            if task_type == "monitor_event":
                event_data = task.task_data.get("event_data", {})
                return await self.monitor_security_event(event_data)

            elif task_type == "validate_access":
                access_request = task.task_data.get("access_request", {})
                return await self.validate_access_request(access_request)

            elif task_type == "security_report":
                report_period = task.task_data.get("report_period_days", 30)
                return await self.generate_security_report(report_period)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}