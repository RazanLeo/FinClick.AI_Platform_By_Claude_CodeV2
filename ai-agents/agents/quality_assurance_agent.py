"""
Quality Assurance Agent
وكيل ضمان الجودة

This agent ensures the quality and accuracy of all financial analysis outputs,
performing validation, verification, and quality control across all agent results.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import statistics

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class QualityCheck(Enum):
    """Types of quality checks"""
    DATA_ACCURACY = "data_accuracy"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    LOGICAL_COHERENCE = "logical_coherence"
    CALCULATION_VERIFICATION = "calculation_verification"
    COMPLIANCE_ADHERENCE = "compliance_adherence"
    FORMAT_VALIDATION = "format_validation"


class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILED = "failed"


@dataclass
class QualityIssue:
    """Quality issue identified during assessment"""
    issue_id: str
    check_type: QualityCheck
    severity: str  # critical, high, medium, low
    description_ar: str
    description_en: str
    location: str
    suggested_fix: str
    impact_assessment: str


class QualityAssuranceAgent(FinancialAgent):
    """
    Specialized agent for quality assurance and validation
    وكيل متخصص في ضمان الجودة والتحقق
    """

    def __init__(self, agent_id: str = "quality_assurance_agent",
                 agent_name_ar: str = "وكيل ضمان الجودة",
                 agent_name_en: str = "Quality Assurance Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'QUALITY_ASSURANCE', 'quality_assurance')
        )

        self.quality_standards = self._initialize_quality_standards()
        self.validation_rules = self._initialize_validation_rules()
        self.quality_metrics = self._initialize_quality_metrics()

    def _initialize_capabilities(self) -> None:
        """Initialize quality assurance capabilities"""
        self.capabilities = {
            "quality_checks": {
                "data_validation": True,
                "calculation_verification": True,
                "consistency_checking": True,
                "completeness_assessment": True,
                "accuracy_verification": True,
                "logical_coherence": True
            },
            "validation_types": {
                "financial_data": True,
                "reports": True,
                "recommendations": True,
                "forecasts": True,
                "risk_assessments": True,
                "compliance_reports": True
            },
            "quality_metrics": {
                "accuracy_score": True,
                "completeness_score": True,
                "consistency_score": True,
                "overall_quality": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_quality_standards(self) -> Dict[str, Any]:
        """Initialize quality standards and thresholds"""
        return {
            "financial_analysis": {
                "data_accuracy_threshold": 0.95,
                "completeness_threshold": 0.90,
                "consistency_threshold": 0.92,
                "calculation_accuracy": 0.98,
                "required_fields": [
                    "revenue", "expenses", "assets", "liabilities", "equity"
                ]
            },
            "risk_assessment": {
                "data_accuracy_threshold": 0.98,
                "completeness_threshold": 0.95,
                "scenario_coverage": 0.85,
                "stress_test_validity": 0.90,
                "required_components": [
                    "credit_risk", "market_risk", "operational_risk"
                ]
            },
            "forecasting": {
                "model_accuracy_threshold": 0.85,
                "confidence_interval_validity": 0.90,
                "assumption_reasonableness": 0.80,
                "scenario_completeness": 0.85
            },
            "reports": {
                "content_completeness": 0.95,
                "format_compliance": 0.98,
                "data_consistency": 0.92,
                "narrative_quality": 0.85,
                "visualization_accuracy": 0.95
            }
        }

    def _initialize_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize validation rules for different data types"""
        return {
            "financial_ratios": [
                {
                    "rule": "debt_to_equity_range",
                    "condition": "0 <= debt_to_equity <= 10",
                    "message_ar": "نسبة الدين إلى حقوق الملكية خارج النطاق المعقول",
                    "severity": "medium"
                },
                {
                    "rule": "roe_range",
                    "condition": "-1 <= roe <= 1",
                    "message_ar": "العائد على حقوق الملكية خارج النطاق المتوقع",
                    "severity": "high"
                },
                {
                    "rule": "current_ratio_positive",
                    "condition": "current_ratio > 0",
                    "message_ar": "النسبة الجارية يجب أن تكون موجبة",
                    "severity": "critical"
                }
            ],
            "market_data": [
                {
                    "rule": "price_volatility",
                    "condition": "volatility >= 0 and volatility <= 2",
                    "message_ar": "تقلبات السعر خارج النطاق المعقول",
                    "severity": "medium"
                },
                {
                    "rule": "volume_positive",
                    "condition": "volume >= 0",
                    "message_ar": "حجم التداول يجب أن يكون موجب",
                    "severity": "high"
                }
            ],
            "forecasts": [
                {
                    "rule": "growth_rate_reasonable",
                    "condition": "-0.5 <= growth_rate <= 2.0",
                    "message_ar": "معدل النمو المتوقع خارج النطاق المعقول",
                    "severity": "high"
                },
                {
                    "rule": "confidence_interval_valid",
                    "condition": "lower_bound <= forecast <= upper_bound",
                    "message_ar": "التنبؤ خارج فترة الثقة المحددة",
                    "severity": "critical"
                }
            ]
        }

    def _initialize_quality_metrics(self) -> Dict[str, Any]:
        """Initialize quality measurement metrics"""
        return {
            "accuracy_weights": {
                "calculation_accuracy": 0.30,
                "data_accuracy": 0.25,
                "logical_consistency": 0.20,
                "completeness": 0.15,
                "format_compliance": 0.10
            },
            "severity_weights": {
                "critical": 1.0,
                "high": 0.7,
                "medium": 0.4,
                "low": 0.1
            },
            "minimum_pass_scores": {
                "overall_quality": 0.80,
                "accuracy": 0.85,
                "completeness": 0.80,
                "consistency": 0.75
            }
        }

    async def perform_quality_assessment(self, analysis_results: Dict[str, Any],
                                       assessment_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Perform comprehensive quality assessment
        إجراء تقييم شامل للجودة
        """
        try:
            assessment = {
                "assessment_id": f"qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "assessment_date": datetime.now().isoformat(),
                "assessment_type": assessment_type,
                "overall_quality": {},
                "quality_checks": {},
                "identified_issues": [],
                "quality_scores": {},
                "recommendations": [],
                "pass_fail_status": "pending"
            }

            # Perform individual quality checks
            for check_type in QualityCheck:
                check_result = await self._perform_quality_check(analysis_results, check_type)
                assessment["quality_checks"][check_type.value] = check_result

                # Collect issues
                if check_result.get("issues"):
                    assessment["identified_issues"].extend(check_result["issues"])

            # Calculate quality scores
            assessment["quality_scores"] = await self._calculate_quality_scores(
                assessment["quality_checks"]
            )

            # Determine overall quality level
            assessment["overall_quality"] = await self._determine_overall_quality(
                assessment["quality_scores"]
            )

            # Generate recommendations
            assessment["recommendations"] = await self._generate_quality_recommendations(
                assessment["identified_issues"],
                assessment["quality_scores"]
            )

            # Determine pass/fail status
            assessment["pass_fail_status"] = await self._determine_pass_fail_status(
                assessment["quality_scores"]
            )

            return assessment

        except Exception as e:
            return {"error": f"Quality assessment failed: {str(e)}"}

    async def _perform_quality_check(self, data: Dict[str, Any],
                                   check_type: QualityCheck) -> Dict[str, Any]:
        """Perform specific quality check"""

        check_result = {
            "check_type": check_type.value,
            "status": "completed",
            "score": 0.0,
            "issues": [],
            "details": {}
        }

        if check_type == QualityCheck.DATA_ACCURACY:
            check_result = await self._check_data_accuracy(data)
        elif check_type == QualityCheck.COMPLETENESS:
            check_result = await self._check_completeness(data)
        elif check_type == QualityCheck.CONSISTENCY:
            check_result = await self._check_consistency(data)
        elif check_type == QualityCheck.LOGICAL_COHERENCE:
            check_result = await self._check_logical_coherence(data)
        elif check_type == QualityCheck.CALCULATION_VERIFICATION:
            check_result = await self._verify_calculations(data)
        elif check_type == QualityCheck.COMPLIANCE_ADHERENCE:
            check_result = await self._check_compliance_adherence(data)
        elif check_type == QualityCheck.FORMAT_VALIDATION:
            check_result = await self._validate_format(data)

        check_result["check_type"] = check_type.value
        return check_result

    async def _check_data_accuracy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data accuracy and validity"""
        issues = []
        total_checks = 0
        passed_checks = 0

        # Check for missing critical data
        if "financial_data" in data:
            financial_data = data["financial_data"]
            required_fields = self.quality_standards["financial_analysis"]["required_fields"]

            for field in required_fields:
                total_checks += 1
                if field in financial_data and financial_data[field] is not None:
                    passed_checks += 1
                else:
                    issues.append(QualityIssue(
                        issue_id=f"missing_{field}",
                        check_type=QualityCheck.DATA_ACCURACY,
                        severity="high",
                        description_ar=f"بيانات مفقودة: {field}",
                        description_en=f"Missing data: {field}",
                        location=f"financial_data.{field}",
                        suggested_fix=f"تحديد قيمة صحيحة لـ {field}",
                        impact_assessment="متوسط إلى عالي"
                    ))

        # Validate numerical ranges
        if "ratios" in data:
            ratios = data["ratios"]
            validation_rules = self.validation_rules.get("financial_ratios", [])

            for rule in validation_rules:
                total_checks += 1
                field_name = rule["rule"].split("_")[0] + "_" + rule["rule"].split("_")[1]

                if field_name in ratios:
                    value = ratios[field_name]
                    if self._evaluate_rule_condition(rule["condition"], {field_name: value}):
                        passed_checks += 1
                    else:
                        issues.append(QualityIssue(
                            issue_id=f"invalid_{field_name}",
                            check_type=QualityCheck.DATA_ACCURACY,
                            severity=rule["severity"],
                            description_ar=rule["message_ar"],
                            description_en=f"Invalid {field_name}: {value}",
                            location=f"ratios.{field_name}",
                            suggested_fix="مراجعة وتصحيح القيمة",
                            impact_assessment="متوسط"
                        ))

        accuracy_score = passed_checks / total_checks if total_checks > 0 else 0.0

        return {
            "status": "completed",
            "score": accuracy_score,
            "issues": issues,
            "details": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "accuracy_percentage": accuracy_score * 100
            }
        }

    async def _check_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data completeness"""
        issues = []
        total_sections = 0
        complete_sections = 0

        expected_sections = [
            "financial_data", "market_analysis", "risk_assessment",
            "recommendations", "forecasts"
        ]

        for section in expected_sections:
            total_sections += 1
            if section in data and data[section]:
                # Check if section has meaningful content
                if isinstance(data[section], dict) and len(data[section]) > 0:
                    complete_sections += 1
                elif isinstance(data[section], list) and len(data[section]) > 0:
                    complete_sections += 1
                elif isinstance(data[section], str) and len(data[section].strip()) > 0:
                    complete_sections += 1
                else:
                    issues.append(QualityIssue(
                        issue_id=f"incomplete_{section}",
                        check_type=QualityCheck.COMPLETENESS,
                        severity="medium",
                        description_ar=f"قسم غير مكتمل: {section}",
                        description_en=f"Incomplete section: {section}",
                        location=section,
                        suggested_fix="إكمال المحتوى المطلوب",
                        impact_assessment="متوسط"
                    ))
            else:
                issues.append(QualityIssue(
                    issue_id=f"missing_{section}",
                    check_type=QualityCheck.COMPLETENESS,
                    severity="high",
                    description_ar=f"قسم مفقود: {section}",
                    description_en=f"Missing section: {section}",
                    location=section,
                    suggested_fix="إضافة القسم المطلوب",
                    impact_assessment="عالي"
                ))

        completeness_score = complete_sections / total_sections if total_sections > 0 else 0.0

        return {
            "status": "completed",
            "score": completeness_score,
            "issues": issues,
            "details": {
                "total_sections": total_sections,
                "complete_sections": complete_sections,
                "completeness_percentage": completeness_score * 100
            }
        }

    async def _check_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check internal consistency of data"""
        issues = []
        consistency_checks = 0
        passed_consistency = 0

        # Check financial statement consistency
        if "financial_data" in data:
            financial_data = data["financial_data"]

            # Assets = Liabilities + Equity
            if all(field in financial_data for field in ["assets", "liabilities", "equity"]):
                consistency_checks += 1
                assets = financial_data["assets"]
                liabilities = financial_data["liabilities"]
                equity = financial_data["equity"]

                balance_check = abs(assets - (liabilities + equity)) / assets if assets > 0 else 0
                if balance_check < 0.01:  # 1% tolerance
                    passed_consistency += 1
                else:
                    issues.append(QualityIssue(
                        issue_id="balance_sheet_imbalance",
                        check_type=QualityCheck.CONSISTENCY,
                        severity="critical",
                        description_ar="عدم توازن الميزانية العمومية",
                        description_en="Balance sheet imbalance",
                        location="financial_data",
                        suggested_fix="مراجعة أرقام الأصول والخصوم وحقوق الملكية",
                        impact_assessment="عالي جداً"
                    ))

        # Check ratio consistency
        if "ratios" in data and "financial_data" in data:
            consistency_checks += 1
            # Check if calculated ratios match expected values
            ratios = data["ratios"]
            financial_data = data["financial_data"]

            # Example: ROE = Net Income / Equity
            if all(field in financial_data for field in ["net_income", "equity"]) and "roe" in ratios:
                expected_roe = financial_data["net_income"] / financial_data["equity"] if financial_data["equity"] != 0 else 0
                actual_roe = ratios["roe"]

                if abs(expected_roe - actual_roe) / max(abs(expected_roe), 0.01) < 0.05:  # 5% tolerance
                    passed_consistency += 1
                else:
                    issues.append(QualityIssue(
                        issue_id="roe_calculation_inconsistency",
                        check_type=QualityCheck.CONSISTENCY,
                        severity="high",
                        description_ar="عدم تطابق حساب العائد على حقوق الملكية",
                        description_en="ROE calculation inconsistency",
                        location="ratios.roe",
                        suggested_fix="إعادة حساب العائد على حقوق الملكية",
                        impact_assessment="عالي"
                    ))

        consistency_score = passed_consistency / consistency_checks if consistency_checks > 0 else 1.0

        return {
            "status": "completed",
            "score": consistency_score,
            "issues": issues,
            "details": {
                "consistency_checks": consistency_checks,
                "passed_consistency": passed_consistency,
                "consistency_percentage": consistency_score * 100
            }
        }

    async def _check_logical_coherence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check logical coherence of analysis and recommendations"""
        issues = []
        coherence_score = 1.0

        # Check if recommendations align with analysis
        if "analysis_results" in data and "recommendations" in data:
            analysis = data["analysis_results"]
            recommendations = data["recommendations"]

            # Example: If risk is high, recommendations should address risk mitigation
            if "risk_level" in analysis and analysis["risk_level"] == "high":
                risk_related_recommendations = any(
                    "risk" in str(rec).lower() or "mitigation" in str(rec).lower()
                    for rec in recommendations
                    if isinstance(rec, (str, dict))
                )

                if not risk_related_recommendations:
                    issues.append(QualityIssue(
                        issue_id="high_risk_no_mitigation",
                        check_type=QualityCheck.LOGICAL_COHERENCE,
                        severity="medium",
                        description_ar="مخاطر عالية بدون توصيات للتخفيف",
                        description_en="High risk without mitigation recommendations",
                        location="recommendations",
                        suggested_fix="إضافة توصيات لإدارة المخاطر",
                        impact_assessment="متوسط"
                    ))
                    coherence_score *= 0.8

        return {
            "status": "completed",
            "score": coherence_score,
            "issues": issues,
            "details": {
                "coherence_percentage": coherence_score * 100
            }
        }

    async def _verify_calculations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify mathematical calculations"""
        issues = []
        total_calculations = 0
        correct_calculations = 0

        # Verify financial ratio calculations
        if "financial_data" in data and "ratios" in data:
            financial_data = data["financial_data"]
            ratios = data["ratios"]

            # Current Ratio = Current Assets / Current Liabilities
            if all(field in financial_data for field in ["current_assets", "current_liabilities"]):
                total_calculations += 1
                expected_current_ratio = (financial_data["current_assets"] /
                                        financial_data["current_liabilities"]
                                        if financial_data["current_liabilities"] != 0 else 0)

                if "current_ratio" in ratios:
                    actual_ratio = ratios["current_ratio"]
                    if abs(expected_current_ratio - actual_ratio) / max(abs(expected_current_ratio), 0.01) < 0.02:
                        correct_calculations += 1
                    else:
                        issues.append(QualityIssue(
                            issue_id="current_ratio_calculation_error",
                            check_type=QualityCheck.CALCULATION_VERIFICATION,
                            severity="high",
                            description_ar="خطأ في حساب النسبة الجارية",
                            description_en="Current ratio calculation error",
                            location="ratios.current_ratio",
                            suggested_fix="إعادة حساب النسبة الجارية",
                            impact_assessment="عالي"
                        ))

        calculation_accuracy = correct_calculations / total_calculations if total_calculations > 0 else 1.0

        return {
            "status": "completed",
            "score": calculation_accuracy,
            "issues": issues,
            "details": {
                "total_calculations": total_calculations,
                "correct_calculations": correct_calculations,
                "accuracy_percentage": calculation_accuracy * 100
            }
        }

    async def _check_compliance_adherence(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check adherence to compliance requirements"""
        issues = []
        compliance_score = 1.0

        # Check for compliance-related content
        if "compliance_check" in data:
            compliance_data = data["compliance_check"]

            if not compliance_data or len(compliance_data) == 0:
                issues.append(QualityIssue(
                    issue_id="missing_compliance_analysis",
                    check_type=QualityCheck.COMPLIANCE_ADHERENCE,
                    severity="high",
                    description_ar="تحليل الامتثال مفقود أو غير مكتمل",
                    description_en="Missing or incomplete compliance analysis",
                    location="compliance_check",
                    suggested_fix="إضافة تحليل شامل للامتثال",
                    impact_assessment="عالي"
                ))
                compliance_score *= 0.6

        return {
            "status": "completed",
            "score": compliance_score,
            "issues": issues,
            "details": {
                "compliance_percentage": compliance_score * 100
            }
        }

    async def _validate_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data format and structure"""
        issues = []
        format_score = 1.0

        # Check for proper data types
        expected_types = {
            "financial_data": dict,
            "ratios": dict,
            "recommendations": (list, dict),
            "analysis_date": str
        }

        for field, expected_type in expected_types.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    issues.append(QualityIssue(
                        issue_id=f"invalid_type_{field}",
                        check_type=QualityCheck.FORMAT_VALIDATION,
                        severity="low",
                        description_ar=f"نوع البيانات غير صحيح لـ {field}",
                        description_en=f"Invalid data type for {field}",
                        location=field,
                        suggested_fix="تصحيح نوع البيانات",
                        impact_assessment="منخفض"
                    ))
                    format_score *= 0.9

        return {
            "status": "completed",
            "score": format_score,
            "issues": issues,
            "details": {
                "format_percentage": format_score * 100
            }
        }

    def _evaluate_rule_condition(self, condition: str, values: Dict[str, Any]) -> bool:
        """Safely evaluate a rule condition"""
        try:
            # Simple implementation - in production, use a safer evaluation method
            for var_name, var_value in values.items():
                condition = condition.replace(var_name, str(var_value))

            # Basic range checks only
            if "<=" in condition and ">=" in condition:
                parts = condition.split("and")
                return all(eval(part.strip()) for part in parts)
            else:
                return eval(condition)
        except:
            return False

    async def _calculate_quality_scores(self, quality_checks: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate aggregated quality scores"""
        weights = self.quality_metrics["accuracy_weights"]

        scores = {}
        weighted_total = 0.0
        total_weight = 0.0

        for check_type, check_result in quality_checks.items():
            if check_result.get("score") is not None:
                score = check_result["score"]
                weight = weights.get(check_type, 0.1)

                scores[check_type] = score
                weighted_total += score * weight
                total_weight += weight

        overall_score = weighted_total / total_weight if total_weight > 0 else 0.0

        return {
            "individual_scores": scores,
            "overall_score": overall_score,
            "weighted_score": weighted_total,
            "score_breakdown": {
                check_type: {
                    "score": scores.get(check_type, 0.0),
                    "weight": weights.get(check_type, 0.1),
                    "contribution": scores.get(check_type, 0.0) * weights.get(check_type, 0.1)
                }
                for check_type in quality_checks.keys()
            }
        }

    async def _determine_overall_quality(self, quality_scores: Dict[str, Any]) -> Dict[str, Any]:
        """Determine overall quality level and assessment"""
        overall_score = quality_scores.get("overall_score", 0.0)

        if overall_score >= 0.9:
            quality_level = QualityLevel.EXCELLENT
            description_ar = "جودة ممتازة"
            description_en = "Excellent quality"
        elif overall_score >= 0.8:
            quality_level = QualityLevel.GOOD
            description_ar = "جودة جيدة"
            description_en = "Good quality"
        elif overall_score >= 0.7:
            quality_level = QualityLevel.ACCEPTABLE
            description_ar = "جودة مقبولة"
            description_en = "Acceptable quality"
        elif overall_score >= 0.5:
            quality_level = QualityLevel.POOR
            description_ar = "جودة ضعيفة"
            description_en = "Poor quality"
        else:
            quality_level = QualityLevel.FAILED
            description_ar = "فشل في معايير الجودة"
            description_en = "Failed quality standards"

        return {
            "quality_level": quality_level.value,
            "overall_score": overall_score,
            "description_ar": description_ar,
            "description_en": description_en,
            "score_percentage": overall_score * 100
        }

    async def _generate_quality_recommendations(self, issues: List[QualityIssue],
                                              quality_scores: Dict[str, Any]) -> List[str]:
        """Generate recommendations for quality improvement"""
        recommendations = []

        # Critical and high severity issues
        critical_issues = [issue for issue in issues if issue.severity in ["critical", "high"]]
        if critical_issues:
            recommendations.append("معالجة فورية للمشاكل عالية الأولوية")
            for issue in critical_issues[:3]:  # Top 3 critical issues
                recommendations.append(f"• {issue.suggested_fix}")

        # Overall score recommendations
        overall_score = quality_scores.get("overall_score", 0.0)
        if overall_score < 0.8:
            recommendations.extend([
                "تحسين دقة البيانات والحسابات",
                "مراجعة اكتمال جميع الأقسام المطلوبة",
                "التحقق من الاتساق الداخلي للبيانات"
            ])

        # Specific improvement areas
        individual_scores = quality_scores.get("individual_scores", {})
        for check_type, score in individual_scores.items():
            if score < 0.7:
                if check_type == "data_accuracy":
                    recommendations.append("تحسين دقة البيانات المدخلة")
                elif check_type == "completeness":
                    recommendations.append("إكمال جميع الأقسام المطلوبة")
                elif check_type == "consistency":
                    recommendations.append("مراجعة الاتساق بين البيانات والحسابات")

        return recommendations

    async def _determine_pass_fail_status(self, quality_scores: Dict[str, Any]) -> str:
        """Determine if analysis passes quality standards"""
        minimum_scores = self.quality_metrics["minimum_pass_scores"]
        overall_score = quality_scores.get("overall_score", 0.0)

        if overall_score >= minimum_scores["overall_quality"]:
            return "pass"
        else:
            return "fail"

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process quality assurance tasks"""
        try:
            task_type = task.task_data.get("type", "quality_assessment")

            if task_type == "quality_assessment":
                analysis_results = task.task_data.get("analysis_results", {})
                assessment_type = task.task_data.get("assessment_type", "comprehensive")
                return await self.perform_quality_assessment(analysis_results, assessment_type)

            else:
                return {"error": f"Unknown task type: {task_type}"}

        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}