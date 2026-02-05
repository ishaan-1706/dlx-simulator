"""
utils/ - Utility modules for the DLX simulator

Contains:
  - logger.py: Pipeline state visualization and logging
  - exceptions.py: Custom exception types (to be added)
"""

from .logger import print_pipeline_state, print_pipeline_summary

__all__ = ['print_pipeline_state', 'print_pipeline_summary']
