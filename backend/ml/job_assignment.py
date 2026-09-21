"""
Wrapper for job_assignment service to be used as ML module
Re-exports FairJobAssignmentEngine for API routes
"""
from ..services.job_assignment import FairJobAssignmentEngine, DEFAULT_WEIGHTS

__all__ = ["FairJobAssignmentEngine", "DEFAULT_WEIGHTS"]
