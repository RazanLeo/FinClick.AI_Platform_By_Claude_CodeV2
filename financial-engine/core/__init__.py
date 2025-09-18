"""
FinClick.AI Financial Analysis Engine - Core Module
Revolutionary Intelligent Financial Analysis Platform

This module contains the core financial analysis engine that performs
180 types of quantitative financial analysis automatically.
"""

__version__ = "1.0.0"
__author__ = "FinClick.AI"
__email__ = "support@finclick.ai"

from .engine import FinancialAnalysisEngine
from .data_models import (
    FinancialStatements,
    AnalysisRequest,
    AnalysisResult,
    CompanyInfo
)
from .analysis_registry import AnalysisRegistry

__all__ = [
    'FinancialAnalysisEngine',
    'FinancialStatements',
    'AnalysisRequest',
    'AnalysisResult',
    'CompanyInfo',
    'AnalysisRegistry'
]