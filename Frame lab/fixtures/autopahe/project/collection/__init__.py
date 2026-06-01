"""
AutoPahe Collection Management System
=====================================
A comprehensive anime collection management system with:
- Full metadata tracking (type, year, genre, synopsis)
- Watch status and progress management
- File organization and duplicate detection
- Collection statistics and analytics
- Import/export functionality

Author: Haxsys
Version: 3.4.0
"""

from example_projects.autopahe.collection.models import AnimeEntry, Episode, WatchStatus, AnimeType
from example_projects.autopahe.collection.manager import CollectionManager
from example_projects.autopahe.collection.commands import handle_collection_command
from example_projects.autopahe.collection.stats import CollectionStats

__all__ = [
    'AnimeEntry',
    'Episode', 
    'WatchStatus',
    'AnimeType',
    'CollectionManager',
    'handle_collection_command',
    'CollectionStats',
]

# Global collection manager instance
_collection_manager = None

def get_collection_manager():
    """Get or create the global collection manager instance."""
    global _collection_manager
    if _collection_manager is None:
        _collection_manager = CollectionManager()
    return _collection_manager
