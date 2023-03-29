"""Helper utilities."""
from typing import TypeVar, Generic, List, Optional
from datetime import datetime, timedelta, timezone

T = TypeVar("T")


class PaginatedResponse(Generic[T]):
    """Generic paginated response."""
    
    def __init__(self, items: List[T], total: int):
        self.items = items
        self.total = total


def get_time_range(hours: int = 24) -> tuple[datetime, datetime]:
    """
    Get start and end time for a range.
    
    Args:
        hours: Number of hours in the range
    
    Returns:
        Tuple of (start_time, end_time)
    """
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)
    return start, now
