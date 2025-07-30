# Import all models to ensure they are registered with Base.metadata
from app.db.base_class import Base  # noqa
from app.models.session import CounselingSession  # noqa
from app.models.transcription import Transcription  # noqa
from app.models.vector import (  # noqa
    SuccessConversationVector,
    ClusterResult,
    ClusterAssignment,
    ClusterRepresentative,
    AnomalyDetectionResult
)
from app.models.script import (  # noqa
    ImprovementScript,
    ScriptUsageAnalytics,
    ScriptFeedback,
    ScriptGenerationJob,
    ScriptVersion,
    ScriptTemplate,
    ScriptPerformanceMetrics
)