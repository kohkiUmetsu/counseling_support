"""
ベクトルデータベースモデル
"""
from sqlalchemy import Column, Text, DateTime, UUID, ForeignKey, Integer, Float, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime

from app.db.base_class import VectorBase


class SuccessConversationVector(VectorBase):
    """成功会話のベクトル化データ"""
    __tablename__ = "success_conversation_vectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(Text, nullable=False)  # Remove foreign key constraint
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)  # OpenAI text-embedding-3-small の次元数
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_index = Column(Integer, nullable=False, default=0)
    counselor_name = Column(Text, nullable=True)
    is_success = Column(Boolean, nullable=True)
    session_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Note: No relationship to CounselingSession as it's in a different database


class ClusterResult(VectorBase):
    """クラスタリング結果"""
    __tablename__ = "cluster_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    algorithm = Column(Text, nullable=False)  # 'kmeans' or 'hdbscan'
    cluster_count = Column(Integer, nullable=False)
    parameters = Column(JSONB, nullable=True)
    silhouette_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーション
    cluster_assignments = relationship("ClusterAssignment", back_populates="cluster_result")
    representatives = relationship("ClusterRepresentative", back_populates="cluster_result")


class ClusterAssignment(VectorBase):
    """ベクトルのクラスタ割り当て"""
    __tablename__ = "cluster_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vector_id = Column(UUID(as_uuid=True), ForeignKey("success_conversation_vectors.id"), nullable=False)
    cluster_result_id = Column(UUID(as_uuid=True), ForeignKey("cluster_results.id"), nullable=False)
    cluster_label = Column(Integer, nullable=False)
    distance_to_centroid = Column(Float, nullable=True)

    # リレーション
    vector = relationship("SuccessConversationVector")
    cluster_result = relationship("ClusterResult", back_populates="cluster_assignments")


class ClusterRepresentative(VectorBase):
    """クラスタ代表例"""
    __tablename__ = "cluster_representatives"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_result_id = Column(UUID(as_uuid=True), ForeignKey("cluster_results.id"), nullable=False)
    vector_id = Column(UUID(as_uuid=True), ForeignKey("success_conversation_vectors.id"), nullable=False)
    cluster_label = Column(Integer, nullable=False)
    quality_score = Column(Float, nullable=False)
    distance_to_centroid = Column(Float, nullable=False)
    is_primary = Column(Boolean, default=False)  # 主要代表例かどうか
    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーション
    cluster_result = relationship("ClusterResult", back_populates="representatives")
    vector = relationship("SuccessConversationVector")


class AnomalyDetectionResult(VectorBase):
    """異常検出結果"""
    __tablename__ = "anomaly_detection_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vector_id = Column(UUID(as_uuid=True), ForeignKey("success_conversation_vectors.id"), nullable=False)
    algorithm = Column(Text, nullable=False)  # 'isolation_forest' or 'lof'
    anomaly_score = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, nullable=False)
    parameters = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # リレーション
    vector = relationship("SuccessConversationVector")