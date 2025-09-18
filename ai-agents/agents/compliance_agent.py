"""
Compliance Agent
وكيل الامتثال

This agent specializes in verifying regulatory compliance across financial reporting,
risk management frameworks, and industry standards for financial institutions.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class ComplianceStandard(Enum):
    """Supported compliance standards"""
    BASEL_III = "basel_iii"
    IFRS = "ifrs"
    GAAP = "gaap"
    SOX = "sarbanes_oxley"
    GDPR = "gdpr"
    SAMA = "sama"
    CMA = "cma"
    SOCPA = "socpa"
    ISLAMIC_FINANCE = "islamic_finance"
    ANTI_MONEY_LAUNDERING = "aml"
    KNOW_YOUR_CUSTOMER = "kyc"


class ComplianceRisk(Enum):
    """Compliance risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ComplianceViolation:
    """Represents a compliance violation"""
    violation_id: str
    standard: ComplianceStandard
    description_ar: str
    description_en: str
    risk_level: ComplianceRisk
    remediation_steps: List[str]
    deadline: Optional[datetime] = None
    impact_assessment: str = ""


class ComplianceAgent(FinancialAgent):
    """
    Specialized agent for regulatory compliance verification
    وكيل متخصص في التحقق من الامتثال التنظيمي
    """

    def __init__(self, agent_id: str = "compliance_agent",
                 agent_name_ar: str = "وكيل الامتثال",
                 agent_name_en: str = "Compliance Agent"):
        # Update AgentType to include COMPLIANCE
        from ..core.agent_base import AgentType

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'COMPLIANCE', 'compliance')
        )

        # Compliance frameworks and standards
        self.compliance_frameworks = self._initialize_compliance_frameworks()
        self.regulatory_requirements = self._initialize_regulatory_requirements()
        self.violation_patterns = self._initialize_violation_patterns()

    def _initialize_capabilities(self) -> None:
        """Initialize compliance verification capabilities"""
        self.capabilities = {
            "regulatory_compliance": {
                "basel_iii_verification": True,
                "ifrs_compliance": True,
                "gaap_compliance": True,
                "sox_compliance": True,
                "sama_regulations": True,
                "cma_requirements": True,
                "islamic_finance_compliance": True
            },
            "risk_assessment": {
                "compliance_risk_scoring": True,
                "violation_detection": True,
                "remediation_planning": True,
                "regulatory_reporting": True
            },
            "monitoring": {
                "continuous_monitoring": True,
                "alert_generation": True,
                "audit_trail": True,
                "documentation": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_compliance_frameworks(self) -> Dict[str, Any]:
        """Initialize compliance frameworks and their requirements"""
        return {
            "basel_iii": {
                "capital_adequacy": {
                    "minimum_capital_ratio": 0.08,
                    "tier1_capital_ratio": 0.06,
                    "common_equity_tier1": 0.045,
                    "conservation_buffer": 0.025,
                    "countercyclical_buffer": 0.025
                },
                "liquidity_coverage": {
                    "lcr_minimum": 1.0,
                    "nsfr_minimum": 1.0
                },
                "leverage_ratio": {
                    "minimum_leverage": 0.03
                }
            },
            "ifrs": {
                "financial_instruments": ["ifrs_9"],
                "revenue_recognition": ["ifrs_15"],
                "leases": ["ifrs_16"],
                "insurance_contracts": ["ifrs_17"]
            },
            "sama_regulations": {
                "banking_control_law": True,
                "anti_money_laundering": True,
                "cybersecurity_framework": True,
                "islamic_banking_regulations": True
            },
            "islamic_finance": {
                "sharia_compliance": True,
                "islamic_banking_standards": True,
                "sukuk_regulations": True,
                "takaful_requirements": True
            }
        }

    def _initialize_regulatory_requirements(self) -> Dict[str, Any]:
        """Initialize regulatory requirements by jurisdiction"""
        return {
            "saudi_arabia": {
                "sama": {
                    "capital_adequacy": "12.5%",
                    "liquidity_requirements": "NSFR >= 100%",
                    "large_exposure_limits": "25% of capital",
                    "provisioning_requirements": "IFRS 9 + SAMA adjustments"
                },
                "cma": {
                    "market_conduct": True,
                    "investor_protection": True,
                    "disclosure_requirements": True
                },
                "socpa": {
                    "accounting_standards": "IFRS as adopted in KSA",
                    "auditing_standards": "ISA",
                    "professional_requirements": True
                }
            },
            "gcc": {
                "common_requirements": {
                    "basel_iii_implementation": True,
                    "ifrs_adoption": True,
                    "kyc_aml_requirements": True
                }
            },
            "international": {
                "basel_committee": {
                    "basel_iii": True,
                    "operational_resilience": True,
                    "climate_risk": True
                },
                "iasb": {
                    "ifrs_standards": True,
                    "sustainability_reporting": True
                }
            }
        }

    def _initialize_violation_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for detecting compliance violations"""
        return {
            "capital_adequacy": {
                "patterns": [
                    r"capital\s+ratio.*below.*\d+%",
                    r"tier\s*1.*insufficient",
                    r"regulatory\s+capital.*deficiency"
                ],
                "thresholds": {
                    "critical": 0.08,
                    "warning": 0.10
                }
            },
            "liquidity": {
                "patterns": [
                    r"liquidity.*shortage",
                    r"lcr.*below.*100%",
                    r"funding.*gap"
                ],
                "thresholds": {
                    "lcr_minimum": 1.0,
                    "nsfr_minimum": 1.0
                }
            },
            "operational_risk": {
                "patterns": [
                    r"operational\s+loss.*exceeding",
                    r"control\s+failure",
                    r"process\s+breakdown"
                ]
            },
            "market_conduct": {
                "patterns": [
                    r"mis\s*selling",
                    r"unfair\s+treatment",
                    r"conflict\s+of\s+interest"
                ]
            }
        }

    async def verify_compliance(self, financial_data: Dict[str, Any],
                              standards: List[ComplianceStandard]) -> Dict[str, Any]:
        """
        Verify compliance against specified standards
        التحقق من الامتثال للمعايير المحددة
        """
        try:
            compliance_results = {
                "overall_status": "compliant",
                "violations": [],
                "warnings": [],
                "recommendations": [],
                "compliance_score": 0.0,
                "detailed_results": {}
            }

            for standard in standards:
                result = await self._check_standard_compliance(financial_data, standard)
                compliance_results["detailed_results"][standard.value] = result

                if result["violations"]:
                    compliance_results["violations"].extend(result["violations"])
                    compliance_results["overall_status"] = "non_compliant"

                if result["warnings"]:
                    compliance_results["warnings"].extend(result["warnings"])

            # Calculate overall compliance score
            compliance_results["compliance_score"] = await self._calculate_compliance_score(
                compliance_results["detailed_results"]
            )

            # Generate recommendations
            compliance_results["recommendations"] = await self._generate_compliance_recommendations(
                compliance_results["violations"],
                compliance_results["warnings"]
            )

            return compliance_results

        except Exception as e:
            return {"error": f"Compliance verification failed: {str(e)}"}

    async def _check_standard_compliance(self, financial_data: Dict[str, Any],
                                       standard: ComplianceStandard) -> Dict[str, Any]:
        """Check compliance against a specific standard"""
        result = {
            "standard": standard.value,
            "compliant": True,
            "violations": [],
            "warnings": [],
            "score": 100.0
        }

        if standard == ComplianceStandard.BASEL_III:
            result = await self._check_basel_iii_compliance(financial_data)
        elif standard == ComplianceStandard.IFRS:
            result = await self._check_ifrs_compliance(financial_data)
        elif standard == ComplianceStandard.SAMA:
            result = await self._check_sama_compliance(financial_data)
        elif standard == ComplianceStandard.ISLAMIC_FINANCE:
            result = await self._check_islamic_finance_compliance(financial_data)
        elif standard == ComplianceStandard.SOX:
            result = await self._check_sox_compliance(financial_data)

        return result

    async def _check_basel_iii_compliance(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check Basel III compliance"""
        violations = []
        warnings = []
        score = 100.0

        # Capital adequacy checks
        capital_ratio = financial_data.get("capital_adequacy_ratio", 0)
        tier1_ratio = financial_data.get("tier1_capital_ratio", 0)

        if capital_ratio < 0.08:
            violations.append(ComplianceViolation(
                violation_id=f"basel_cap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                standard=ComplianceStandard.BASEL_III,
                description_ar="نسبة كفاية رأس المال أقل من الحد الأدنى المطلوب (8%)",
                description_en=f"Capital adequacy ratio ({capital_ratio:.2%}) below minimum requirement (8%)",
                risk_level=ComplianceRisk.CRITICAL,
                remediation_steps=[
                    "زيادة رأس المال الأساسي",
                    "تقليل الأصول المرجحة بالمخاطر",
                    "إعادة تقييم محفظة الاستثمارات"
                ]
            ))
            score -= 30

        if tier1_ratio < 0.06:
            violations.append(ComplianceViolation(
                violation_id=f"basel_tier1_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                standard=ComplianceStandard.BASEL_III,
                description_ar="نسبة رأس المال من الشريحة الأولى أقل من الحد الأدنى",
                description_en=f"Tier 1 capital ratio ({tier1_ratio:.2%}) below minimum requirement (6%)",
                risk_level=ComplianceRisk.HIGH,
                remediation_steps=[
                    "تعزيز رأس المال الأساسي",
                    "مراجعة سياسات توزيع الأرباح"
                ]
            ))
            score -= 25

        # Liquidity checks
        lcr = financial_data.get("liquidity_coverage_ratio", 0)
        if lcr < 1.0:
            violations.append(ComplianceViolation(
                violation_id=f"basel_lcr_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                standard=ComplianceStandard.BASEL_III,
                description_ar="نسبة تغطية السيولة أقل من 100%",
                description_en=f"Liquidity Coverage Ratio ({lcr:.2%}) below minimum requirement (100%)",
                risk_level=ComplianceRisk.HIGH,
                remediation_steps=[
                    "زيادة الأصول السائلة عالية الجودة",
                    "تنويع مصادر التمويل",
                    "تحسين إدارة السيولة قصيرة الأجل"
                ]
            ))
            score -= 20

        return {
            "standard": "basel_iii",
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "score": max(0, score)
        }

    async def _check_ifrs_compliance(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check IFRS compliance"""
        violations = []
        warnings = []
        score = 100.0

        # IFRS 9 - Financial Instruments
        if not financial_data.get("ifrs9_implementation", False):
            violations.append(ComplianceViolation(
                violation_id=f"ifrs9_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                standard=ComplianceStandard.IFRS,
                description_ar="عدم تطبيق معيار التقرير المالي الدولي رقم 9 للأدوات المالية",
                description_en="IFRS 9 Financial Instruments not properly implemented",
                risk_level=ComplianceRisk.HIGH,
                remediation_steps=[
                    "تطبيق نموذج الخسائر الائتمانية المتوقعة",
                    "مراجعة تصنيف الأدوات المالية",
                    "تحديث سياسات المحاسبة"
                ]
            ))
            score -= 25

        # IFRS 15 - Revenue Recognition
        revenue_method = financial_data.get("revenue_recognition_method")
        if revenue_method != "ifrs15":
            warnings.append("يجب مراجعة طريقة الاعتراف بالإيرادات وفقاً لمعيار 15")
            score -= 10

        return {
            "standard": "ifrs",
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "score": max(0, score)
        }

    async def _check_sama_compliance(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check SAMA regulatory compliance"""
        violations = []
        warnings = []
        score = 100.0

        # SAMA capital requirements (higher than Basel III)
        capital_ratio = financial_data.get("capital_adequacy_ratio", 0)
        if capital_ratio < 0.125:  # SAMA requirement: 12.5%
            violations.append(ComplianceViolation(
                violation_id=f"sama_cap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                standard=ComplianceStandard.SAMA,
                description_ar="نسبة كفاية رأس المال أقل من متطلبات ساما (12.5%)",
                description_en=f"Capital ratio ({capital_ratio:.2%}) below SAMA requirement (12.5%)",
                risk_level=ComplianceRisk.CRITICAL,
                remediation_steps=[
                    "الامتثال لمتطلبات ساما لكفاية رأس المال",
                    "تقديم خطة لتعزيز رأس المال",
                    "مراجعة استراتيجية النمو"
                ]
            ))
            score -= 40

        # Large exposure limits
        large_exposures = financial_data.get("large_exposures", [])
        for exposure in large_exposures:
            if exposure.get("percentage", 0) > 0.25:  # 25% of capital
                violations.append(ComplianceViolation(
                    violation_id=f"sama_exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    standard=ComplianceStandard.SAMA,
                    description_ar=f"تجاوز حد التعرض الكبير: {exposure.get('percentage', 0):.1%}",
                    description_en=f"Large exposure limit exceeded: {exposure.get('percentage', 0):.1%}",
                    risk_level=ComplianceRisk.HIGH,
                    remediation_steps=[
                        "تقليل التعرض للطرف المقابل",
                        "تنويع محفظة الائتمان",
                        "الحصول على موافقة ساما إذا لزم الأمر"
                    ]
                ))
                score -= 15

        return {
            "standard": "sama",
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "score": max(0, score)
        }

    async def _check_islamic_finance_compliance(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check Islamic finance compliance (Sharia compliance)"""
        violations = []
        warnings = []
        score = 100.0

        # Check for prohibited activities
        prohibited_activities = financial_data.get("prohibited_activities", [])
        if prohibited_activities:
            for activity in prohibited_activities:
                violations.append(ComplianceViolation(
                    violation_id=f"sharia_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    standard=ComplianceStandard.ISLAMIC_FINANCE,
                    description_ar=f"نشاط محظور شرعياً: {activity}",
                    description_en=f"Sharia-prohibited activity detected: {activity}",
                    risk_level=ComplianceRisk.CRITICAL,
                    remediation_steps=[
                        "إزالة الأنشطة المحظورة شرعياً",
                        "مراجعة هيئة الرقابة الشرعية",
                        "تطهير الإيرادات المختلطة"
                    ]
                ))
                score -= 30

        # Check Sharia board approval
        if not financial_data.get("sharia_board_approval", False):
            warnings.append("يتطلب موافقة هيئة الرقابة الشرعية")
            score -= 10

        return {
            "standard": "islamic_finance",
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "score": max(0, score)
        }

    async def _check_sox_compliance(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check Sarbanes-Oxley compliance"""
        violations = []
        warnings = []
        score = 100.0

        # Internal controls assessment
        internal_controls = financial_data.get("internal_controls", {})

        if not internal_controls.get("management_assessment", False):
            violations.append(ComplianceViolation(
                violation_id=f"sox_mgmt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                standard=ComplianceStandard.SOX,
                description_ar="تقييم الإدارة للرقابة الداخلية غير مكتمل",
                description_en="Management assessment of internal controls incomplete",
                risk_level=ComplianceRisk.HIGH,
                remediation_steps=[
                    "إكمال تقييم الإدارة للرقابة الداخلية",
                    "توثيق العمليات والضوابط",
                    "تدريب الموظفين على متطلبات SOX"
                ]
            ))
            score -= 25

        if not internal_controls.get("auditor_attestation", False):
            violations.append(ComplianceViolation(
                violation_id=f"sox_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                standard=ComplianceStandard.SOX,
                description_ar="شهادة المراجع الخارجي للرقابة الداخلية مفقودة",
                description_en="External auditor attestation on internal controls missing",
                risk_level=ComplianceRisk.HIGH,
                remediation_steps=[
                    "الحصول على شهادة المراجع الخارجي",
                    "معالجة أوجه القصور المادية",
                    "تعزيز بيئة الرقابة"
                ]
            ))
            score -= 25

        return {
            "standard": "sox",
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "score": max(0, score)
        }

    async def _calculate_compliance_score(self, detailed_results: Dict[str, Any]) -> float:
        """Calculate overall compliance score"""
        if not detailed_results:
            return 0.0

        total_score = sum(result.get("score", 0) for result in detailed_results.values())
        return total_score / len(detailed_results)

    async def _generate_compliance_recommendations(self, violations: List[ComplianceViolation],
                                                 warnings: List[str]) -> List[Dict[str, Any]]:
        """Generate compliance recommendations"""
        recommendations = []

        # High-priority recommendations for critical violations
        critical_violations = [v for v in violations if v.risk_level == ComplianceRisk.CRITICAL]
        if critical_violations:
            recommendations.append({
                "priority": "critical",
                "title_ar": "معالجة المخالفات الحرجة",
                "title_en": "Address Critical Violations",
                "description_ar": "يجب معالجة المخالفات الحرجة فوراً لتجنب العقوبات التنظيمية",
                "description_en": "Critical violations must be addressed immediately to avoid regulatory penalties",
                "actions": [v.remediation_steps for v in critical_violations]
            })

        # Medium-priority recommendations
        high_violations = [v for v in violations if v.risk_level == ComplianceRisk.HIGH]
        if high_violations:
            recommendations.append({
                "priority": "high",
                "title_ar": "تحسين الامتثال",
                "title_en": "Improve Compliance",
                "description_ar": "تحسين إجراءات الامتثال لتقليل المخاطر التنظيمية",
                "description_en": "Enhance compliance procedures to reduce regulatory risks",
                "actions": [v.remediation_steps for v in high_violations]
            })

        # Continuous improvement recommendations
        if warnings:
            recommendations.append({
                "priority": "medium",
                "title_ar": "التحسين المستمر",
                "title_en": "Continuous Improvement",
                "description_ar": "تطوير إجراءات الامتثال والرقابة الداخلية",
                "description_en": "Develop compliance procedures and internal controls",
                "actions": warnings
            })

        return recommendations

    async def monitor_compliance(self, monitoring_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor ongoing compliance status
        مراقبة حالة الامتثال المستمرة
        """
        try:
            monitoring_results = {
                "monitoring_status": "active",
                "alerts": [],
                "trends": {},
                "next_review_date": datetime.now() + timedelta(days=30),
                "monitoring_metrics": {}
            }

            # Set up monitoring alerts
            alert_thresholds = monitoring_config.get("alert_thresholds", {})
            for metric, threshold in alert_thresholds.items():
                monitoring_results["monitoring_metrics"][metric] = {
                    "current_value": None,
                    "threshold": threshold,
                    "status": "monitoring"
                }

            # Schedule regular compliance checks
            monitoring_results["scheduled_checks"] = [
                {
                    "check_type": "basel_iii_quarterly",
                    "frequency": "quarterly",
                    "next_due": datetime.now() + timedelta(days=90)
                },
                {
                    "check_type": "sama_monthly",
                    "frequency": "monthly",
                    "next_due": datetime.now() + timedelta(days=30)
                },
                {
                    "check_type": "ifrs_annual",
                    "frequency": "annual",
                    "next_due": datetime.now() + timedelta(days=365)
                }
            ]

            return monitoring_results

        except Exception as e:
            return {"error": f"Compliance monitoring setup failed: {str(e)}"}

    async def generate_compliance_report(self, compliance_results: Dict[str, Any],
                                       language: str = "ar") -> Dict[str, Any]:
        """
        Generate comprehensive compliance report
        إنشاء تقرير شامل للامتثال
        """
        try:
            if language == "ar":
                report = {
                    "عنوان_التقرير": "تقرير الامتثال التنظيمي",
                    "تاريخ_التقرير": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "الحالة_العامة": compliance_results.get("overall_status", "غير محدد"),
                    "نقاط_الامتثال": compliance_results.get("compliance_score", 0),
                    "المخالفات": [],
                    "التحذيرات": compliance_results.get("warnings", []),
                    "التوصيات": compliance_results.get("recommendations", []),
                    "الملخص_التنفيذي": ""
                }

                # Add violations in Arabic
                for violation in compliance_results.get("violations", []):
                    report["المخالفات"].append({
                        "المعيار": violation.standard.value,
                        "الوصف": violation.description_ar,
                        "مستوى_المخاطر": violation.risk_level.value,
                        "خطوات_العلاج": violation.remediation_steps
                    })

            else:  # English
                report = {
                    "report_title": "Regulatory Compliance Report",
                    "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "overall_status": compliance_results.get("overall_status", "undefined"),
                    "compliance_score": compliance_results.get("compliance_score", 0),
                    "violations": [],
                    "warnings": compliance_results.get("warnings", []),
                    "recommendations": compliance_results.get("recommendations", []),
                    "executive_summary": ""
                }

                # Add violations in English
                for violation in compliance_results.get("violations", []):
                    report["violations"].append({
                        "standard": violation.standard.value,
                        "description": violation.description_en,
                        "risk_level": violation.risk_level.value,
                        "remediation_steps": violation.remediation_steps
                    })

            return report

        except Exception as e:
            return {"error": f"Report generation failed: {str(e)}"}

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process compliance-related tasks"""
        try:
            task_type = task.task_data.get("type", "verify_compliance")

            if task_type == "verify_compliance":
                financial_data = task.task_data.get("financial_data", {})
                standards = [ComplianceStandard(s) for s in task.task_data.get("standards", [])]
                return await self.verify_compliance(financial_data, standards)

            elif task_type == "monitor_compliance":
                monitoring_config = task.task_data.get("monitoring_config", {})
                return await self.monitor_compliance(monitoring_config)

            elif task_type == "generate_report":
                compliance_results = task.task_data.get("compliance_results", {})
                language = task.task_data.get("language", "ar")
                return await self.generate_compliance_report(compliance_results, language)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}