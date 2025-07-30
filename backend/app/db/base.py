# Import all main database models to ensure they are registered with Base.metadata
from app.db.base_class import Base  # noqa
from app.models.session import CounselingSession  # noqa
from app.models.transcription import Transcription, TranscriptionSegment  # noqa
from app.models.script import (  # noqa
    ImprovementScript,
    ScriptUsageAnalytics,
    ScriptFeedback,
    ScriptGenerationJob,
    ScriptVersion,
    ScriptTemplate,
    ScriptPerformanceMetrics
)
# Note: Vector models are now in separate database