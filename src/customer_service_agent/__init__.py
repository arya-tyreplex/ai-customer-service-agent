"""
TyrePlex AI Customer Service - In-house ML system for tyre business.
"""

__version__ = "2.0.0"
__author__ = "Bhavik Jikadara"
__email__ = "bhavikjikadara@yahoo.com"

from .integrated_agent import IntegratedTyrePlexAgent
from .csv_tools import CSVTyrePlexTools

__all__ = [
    # Main agent
    "IntegratedTyrePlexAgent",
    # CSV tools
    "CSVTyrePlexTools",
]
