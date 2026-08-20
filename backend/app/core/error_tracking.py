"""Optional error tracking (Sentry).

A no-op unless SENTRY_DSN is set, so this never forces a Sentry account on
anyone running the app locally or evaluating the project.
"""

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def configure_error_tracking() -> None:
    """Initialize Sentry if SENTRY_DSN is configured; no-op otherwise."""
    if not settings.SENTRY_DSN:
        return

    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=0.1,
    )
    logger.info("Sentry error tracking enabled")
