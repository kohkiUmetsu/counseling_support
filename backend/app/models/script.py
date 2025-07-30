"""
スクリプト管理用データベースモデル
"""
from sqlalchemy import Column, Text, DateTime, UUID, Float, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.base_class import Base


class ImprovementScript(Base):
    """改善スクリプト"""
    __tablename__ = "improvement_scripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(Text, nullable=False)  # e.g., "v1.0.0", "v1.1.0"
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # スクリプト内容（構造化JSON）
    content = Column(JSONB, nullable=False)
    
    # 生成メタデータ
    generation_metadata = Column(JSONB, nullable=True)
    
    # 品質メトリクス
    quality_metrics = Column(JSONB, nullable=True)
    
    # ステータス管理
    status = Column(Text, default="draft")  # draft, review, active, archived
    is_active = Column(Boolean, default=False)
    
    # 生成元データ情報
    cluster_result_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to vector DB, no FK constraint
    based_on_failure_sessions = Column(JSONB, nullable=True)  # 失敗セッションIDのリスト
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
    
    # リレーション
    # Note: cluster_result relationship removed due to database separation
    usage_analytics = relationship("ScriptUsageAnalytics", back_populates="script")
    feedback_entries = relationship("ScriptFeedback", back_populates="script")


class ScriptUsageAnalytics(Base):
    """スクリプト使用分析"""
    __tablename__ = "script_usage_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey("improvement_scripts.id"), nullable=False)
    
    # 使用期間
    usage_start_date = Column(DateTime, nullable=False)
    usage_end_date = Column(DateTime, nullable=True)
    
    # パフォーマンスメトリクス
    total_sessions = Column(Integer, default=0)
    successful_sessions = Column(Integer, default=0)
    conversion_rate = Column(Float, nullable=True)
    
    # 改善効果
    baseline_conversion_rate = Column(Float, nullable=True)
    improvement_rate = Column(Float, nullable=True)
    
    # 詳細分析データ
    counselor_performance = Column(JSONB, nullable=True)  # カウンセラー別パフォーマンス
    time_period_analysis = Column(JSONB, nullable=True)   # 期間別分析
    customer_segment_analysis = Column(JSONB, nullable=True)  # 顧客セグメント別分析
    
    # 統計的有意性
    statistical_significance = Column(Boolean, nullable=True)
    confidence_level = Column(Float, nullable=True)
    p_value = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    script = relationship("ImprovementScript", back_populates="usage_analytics")


class ScriptFeedback(Base):
    """スクリプトフィードバック"""
    __tablename__ = "script_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey("improvement_scripts.id"), nullable=False)
    
    # フィードバック提供者
    counselor_name = Column(Text, nullable=True)
    role = Column(Text, nullable=True)  # counselor, manager, trainer
    
    # フィードバック内容
    rating = Column(Integer, nullable=True)  # 1-5 stars
    usability_score = Column(Integer, nullable=True)  # 1-5
    effectiveness_score = Column(Integer, nullable=True)  # 1-5
    
    # コメント
    positive_points = Column(Text, nullable=True)
    improvement_suggestions = Column(Text, nullable=True)
    specific_feedback = Column(JSONB, nullable=True)  # セクション別フィードバック
    
    # 使用状況
    usage_frequency = Column(Text, nullable=True)  # daily, weekly, monthly
    usage_context = Column(Text, nullable=True)  # specific use cases
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    script = relationship("ImprovementScript", back_populates="feedback_entries")


class ScriptGenerationJob(Base):
    """スクリプト生成ジョブ"""
    __tablename__ = "script_generation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(Text, unique=True, nullable=False)  # 外部から参照するID
    
    # ジョブ設定
    input_data = Column(JSONB, nullable=False)
    
    # ステータス管理
    status = Column(Text, default="pending")  # pending, running, completed, failed
    progress_percentage = Column(Integer, default=0)
    
    # 実行情報
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    processing_time = Column(Float, nullable=True)  # seconds
    
    # 結果
    result_script_id = Column(UUID(as_uuid=True), ForeignKey("improvement_scripts.id"), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # リソース使用量
    token_usage = Column(JSONB, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    result_script = relationship("ImprovementScript")


class ScriptVersion(Base):
    """スクリプトバージョン管理"""
    __tablename__ = "script_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey("improvement_scripts.id"), nullable=False)
    
    # バージョン情報
    version_number = Column(Text, nullable=False)
    parent_version_id = Column(UUID(as_uuid=True), ForeignKey("script_versions.id"), nullable=True)
    
    # 変更内容
    content_snapshot = Column(JSONB, nullable=False)
    change_summary = Column(Text, nullable=True)
    change_details = Column(JSONB, nullable=True)
    
    # 変更理由
    change_reason = Column(Text, nullable=True)  # improvement, bug_fix, feature_add
    changed_by = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 自己参照リレーション
    parent_version = relationship("ScriptVersion", remote_side=[id])
    child_versions = relationship("ScriptVersion")


class ScriptTemplate(Base):
    """スクリプトテンプレート"""
    __tablename__ = "script_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # テンプレート情報
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Text, nullable=True)  # basic, advanced, specialized
    
    # テンプレート内容
    template_content = Column(JSONB, nullable=False)
    
    # 使用設定
    is_public = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    
    # メタデータ
    tags = Column(JSONB, nullable=True)  # ["beginner", "closing", "objection_handling"]
    target_scenarios = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScriptPerformanceMetrics(Base):
    """スクリプトパフォーマンスメトリクス"""
    __tablename__ = "script_performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey("improvement_scripts.id"), nullable=False)
    
    # 測定期間
    measurement_date = Column(DateTime, nullable=False)
    measurement_period = Column(Text, nullable=False)  # daily, weekly, monthly
    
    # 成約率メトリクス
    total_counseling_sessions = Column(Integer, default=0)
    successful_conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, nullable=True)
    
    # 比較メトリクス
    baseline_conversion_rate = Column(Float, nullable=True)
    improvement_percentage = Column(Float, nullable=True)
    
    # セグメント別パフォーマンス
    performance_by_counselor = Column(JSONB, nullable=True)
    performance_by_time_slot = Column(JSONB, nullable=True)
    performance_by_customer_type = Column(JSONB, nullable=True)
    
    # 品質指標
    customer_satisfaction_score = Column(Float, nullable=True)
    script_adherence_rate = Column(Float, nullable=True)
    
    # 統計情報
    confidence_interval = Column(JSONB, nullable=True)
    sample_size = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    script = relationship("ImprovementScript")