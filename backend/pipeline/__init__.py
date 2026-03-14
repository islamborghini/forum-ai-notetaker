"""
Pipeline package for Sprint 1 backend processing.
"""

from .audio import extract_audio
from .transcribe import transcribe_audio
from .process import process_recording

__all__ = ["extract_audio", "transcribe_audio", "process_recording"]
Pipeline package.

This file can stay empty. The real point is that the backend has
a clear place where the processing workflow is triggered.
"""
