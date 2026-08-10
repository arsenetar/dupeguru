# Pipeline package initialization
from core.pipeline.discovery import FileDiscovery
from core.pipeline.hasher import ContentHasher
from core.pipeline.matcher import DuplicateMatcher

__all__ = ["FileDiscovery", "ContentHasher", "DuplicateMatcher"]
