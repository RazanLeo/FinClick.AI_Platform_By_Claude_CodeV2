"""
Classical Foundational Analysis Module (106 analyses total)
- Structural Analysis (13 analyses)
- Financial Ratios (75 analyses)
- Flow and Movement Analysis (18 analyses)
"""

from .structural_analysis import StructuralAnalysis
from .financial_ratios import FinancialRatiosAnalysis
from .flow_movement_analysis import FlowMovementAnalysis

__all__ = [
    'StructuralAnalysis',
    'FinancialRatiosAnalysis',
    'FlowMovementAnalysis'
]