"""
Data Validation Agent
وكيل التحقق من البيانات

This agent validates and verifies data integrity, consistency, and quality
across all financial data inputs and processing stages.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..core.agent_base import FinancialAgent, AgentType, AgentTask
from langchain_core.prompts import ChatPromptTemplate


class ValidationRule(Enum):
    """Types of validation rules"""
    DATA_TYPE = "data_type"
    RANGE_CHECK = "range_check"
    FORMAT_CHECK = "format_check"
    BUSINESS_LOGIC = "business_logic"
    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    REFERENTIAL_INTEGRITY = "referential_integrity"


class DataValidationAgent(FinancialAgent):
    """
    Specialized agent for data validation and verification
    وكيل متخصص في التحقق من صحة البيانات
    """

    def __init__(self, agent_id: str = "data_validation_agent",
                 agent_name_ar: str = "وكيل التحقق من البيانات",
                 agent_name_en: str = "Data Validation Agent"):

        super().__init__(
            agent_id=agent_id,
            agent_name=f"{agent_name_ar} | {agent_name_en}",
            agent_type=getattr(AgentType, 'DATA_VALIDATION', 'data_validation')
        )

        self.validation_rules = self._initialize_validation_rules()
        self.data_schemas = self._initialize_data_schemas()

    def _initialize_capabilities(self) -> None:
        """Initialize data validation capabilities"""
        self.capabilities = {
            "validation_types": {
                "data_type_validation": True,
                "range_validation": True,
                "format_validation": True,
                "business_rule_validation": True,
                "completeness_check": True,
                "consistency_check": True
            },
            "data_types": {
                "financial_statements": True,
                "market_data": True,
                "risk_metrics": True,
                "compliance_data": True,
                "esg_data": True
            },
            "languages": ["ar", "en"]
        }

    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules"""
        return {
            "financial_data": {
                "revenue": {"type": "float", "min": 0, "required": True},
                "expenses": {"type": "float", "min": 0, "required": True},
                "assets": {"type": "float", "min": 0, "required": True},
                "liabilities": {"type": "float", "min": 0, "required": True},
                "equity": {"type": "float", "required": True}
            },
            "market_data": {
                "price": {"type": "float", "min": 0, "required": True},
                "volume": {"type": "int", "min": 0, "required": False},
                "market_cap": {"type": "float", "min": 0, "required": False}
            }
        }

    def _initialize_data_schemas(self) -> Dict[str, Any]:
        """Initialize data schemas for validation"""
        return {
            "financial_statement": {
                "required_fields": ["revenue", "expenses", "assets", "liabilities"],
                "optional_fields": ["notes", "audit_opinion"],
                "calculated_fields": ["net_income", "total_equity"]
            }
        }

    async def validate_data(self, data: Dict[str, Any], 
                          data_type: str = "financial_data") -> Dict[str, Any]:
        """
        Validate data according to specified rules
        التحقق من صحة البيانات وفقاً للقواعد المحددة
        """
        validation_result = {
            "validation_id": f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "data_type": data_type,
            "validation_date": datetime.now().isoformat(),
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {}
        }

        try:
            # Get validation rules for data type
            rules = self.validation_rules.get(data_type, {})
            
            # Validate each field
            for field, rule in rules.items():
                field_validation = await self._validate_field(data, field, rule)
                
                if not field_validation["is_valid"]:
                    validation_result["is_valid"] = False
                    validation_result["errors"].extend(field_validation["errors"])
                
                validation_result["warnings"].extend(field_validation.get("warnings", []))

            # Business logic validation
            business_validation = await self._validate_business_logic(data, data_type)
            if not business_validation["is_valid"]:
                validation_result["is_valid"] = False
                validation_result["errors"].extend(business_validation["errors"])

            # Calculate statistics
            validation_result["statistics"] = {
                "total_fields": len(rules),
                "valid_fields": len(rules) - len(validation_result["errors"]),
                "error_rate": len(validation_result["errors"]) / len(rules) if rules else 0,
                "completeness": self._calculate_completeness(data, rules)
            }

            return validation_result

        except Exception as e:
            return {"error": f"Data validation failed: {str(e)}"}

    async def _validate_field(self, data: Dict[str, Any], field: str, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual field"""
        result = {"is_valid": True, "errors": [], "warnings": []}
        
        value = data.get(field)
        
        # Check if required field is present
        if rule.get("required", False) and value is None:
            result["is_valid"] = False
            result["errors"].append(f"Required field '{field}' is missing")
            return result
        
        if value is not None:
            # Type validation
            expected_type = rule.get("type")
            if expected_type == "float" and not isinstance(value, (int, float)):
                result["is_valid"] = False
                result["errors"].append(f"Field '{field}' must be numeric")
            
            # Range validation
            if "min" in rule and value < rule["min"]:
                result["is_valid"] = False
                result["errors"].append(f"Field '{field}' below minimum value {rule['min']}")
            
            if "max" in rule and value > rule["max"]:
                result["is_valid"] = False
                result["errors"].append(f"Field '{field}' above maximum value {rule['max']}")
        
        return result

    async def _validate_business_logic(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Validate business logic rules"""
        result = {"is_valid": True, "errors": []}
        
        if data_type == "financial_data":
            # Assets should equal Liabilities + Equity
            assets = data.get("assets", 0)
            liabilities = data.get("liabilities", 0)
            equity = data.get("equity", 0)
            
            if assets > 0 and abs(assets - (liabilities + equity)) / assets > 0.01:
                result["errors"].append("Balance sheet does not balance (Assets ≠ Liabilities + Equity)")
                result["is_valid"] = False
        
        return result

    def _calculate_completeness(self, data: Dict[str, Any], rules: Dict[str, Any]) -> float:
        """Calculate data completeness percentage"""
        if not rules:
            return 1.0
        
        present_fields = sum(1 for field in rules.keys() if data.get(field) is not None)
        return present_fields / len(rules)

    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process data validation tasks"""
        try:
            task_type = task.task_data.get("type", "validate_data")
            
            if task_type == "validate_data":
                data = task.task_data.get("data", {})
                data_type = task.task_data.get("data_type", "financial_data")
                return await self.validate_data(data, data_type)
            
            else:
                return {"error": f"Unknown task type: {task_type}"}
        
        except Exception as e:
            return {"error": f"Task processing failed: {str(e)}"}