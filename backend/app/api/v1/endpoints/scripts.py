"""
スクリプト生成・管理API エンドポイント
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.db.session import get_db
from app.core.database import get_vector_database as get_vector_db
from app.models.script import (
    ImprovementScript, 
    ScriptUsageAnalytics,
    ScriptFeedback,
    ScriptPerformanceMetrics
)
from app.services.script_generation_service import create_script_generation_service
from app.services.script_quality_analyzer import create_script_quality_analyzer
# Note: representative_extraction_service moved to vector DB endpoints


router = APIRouter()


# Pydanticモデル
class ScriptGenerationRequest(BaseModel):
    title: Optional[str] = Field(default=None, description="スクリプトタイトル")
    description: Optional[str] = Field(default=None, description="スクリプト説明")


class ScriptGenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ScriptUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ScriptFeedbackRequest(BaseModel):
    counselor_name: Optional[str] = None
    role: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    usability_score: Optional[int] = Field(None, ge=1, le=5)
    effectiveness_score: Optional[int] = Field(None, ge=1, le=5)
    positive_points: Optional[str] = None
    improvement_suggestions: Optional[str] = None
    specific_feedback: Optional[Dict[str, Any]] = None
    usage_frequency: Optional[str] = None
    usage_context: Optional[str] = None


@router.post("/generate", response_model=ScriptGenerationResponse)
async def generate_script(
    request: ScriptGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """スクリプト生成を開始"""
    try:
        script_id = str(uuid.uuid4())
        
        # 直接ImprovementScriptレコードを作成
        improvement_script = ImprovementScript(
            id=script_id,
            version="v1.0.0",
            title=request.title or "AI生成スクリプト",
            description=request.description or "AI生成による改善スクリプト",
            content={},  # 生成処理で更新
            status="generating"
        )
        
        db.add(improvement_script)
        db.commit()
        
        # バックグラウンドで生成処理を実行
        background_tasks.add_task(
            execute_script_generation,
            script_id,
            request.dict(),
            db
        )
        
        return ScriptGenerationResponse(
            job_id=script_id,
            status="generating",
            message="スクリプト生成を開始しました"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"スクリプト生成開始エラー: {str(e)}")


@router.get("/generate/{job_id}/status")
async def get_generation_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """スクリプト生成状況確認"""
    try:
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == job_id
        ).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="スクリプトが見つかりません")
        
        response = {
            "job_id": job_id,
            "status": script.status,
            "progress_percentage": 100 if script.status == "completed" else 50 if script.status == "generating" else 0,
            "created_at": script.created_at,
            "started_at": script.created_at,
            "completed_at": script.updated_at if script.status == "completed" else None
        }
        
        if script.status == "completed":
            # 完了時は生成されたスクリプト情報も返却
            
            response["script"] = {
                "id": str(script.id),
                "title": script.title,
                "version": script.version,
                "status": script.status,
                "quality_metrics": script.quality_metrics
            }
        
        elif script.status == "failed":
            response["error_message"] = "生成に失敗しました"
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"状況確認エラー: {str(e)}")


@router.get("/")
async def get_scripts(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """スクリプト一覧取得"""
    try:
        query = db.query(ImprovementScript)
        
        if status:
            query = query.filter(ImprovementScript.status == status)
        
        scripts = query.order_by(
            ImprovementScript.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        total = query.count()
        
        return {
            "scripts": [
                {
                    "id": str(script.id),
                    "title": script.title,
                    "description": script.description,
                    "version": script.version,
                    "status": script.status,
                    "is_active": script.is_active,
                    "created_at": script.created_at,
                    "updated_at": script.updated_at,
                    "quality_metrics": script.quality_metrics
                }
                for script in scripts
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"スクリプト一覧取得エラー: {str(e)}")


@router.get("/{script_id}")
async def get_script(
    script_id: str,
    db: Session = Depends(get_db)
):
    """特定スクリプト取得"""
    try:
        # UUIDフォーマットの検証
        try:
            import uuid
            uuid.UUID(script_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="無効なスクリプトIDフォーマットです")
        
        # Connection timeout handling
        from sqlalchemy import text
        try:
            # Test connection with timeout
            db.execute(text("SELECT 1"))
            db.commit()
        except Exception as conn_error:
            raise HTTPException(status_code=503, detail="データベース接続エラー")
        
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == script_id
        ).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="スクリプトが見つかりません")
        
        return {
            "id": str(script.id),
            "title": script.title,
            "description": script.description,
            "version": script.version,
            "content": script.content,
            "status": script.status,
            "is_active": script.is_active,
            "generation_metadata": script.generation_metadata,
            "quality_metrics": script.quality_metrics,
            "created_at": script.created_at,
            "updated_at": script.updated_at,
            "activated_at": script.activated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # More specific error handling for timeouts
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            raise HTTPException(status_code=504, detail="データベースクエリがタイムアウトしました")
        raise HTTPException(status_code=500, detail=f"スクリプト取得エラー: {str(e)}")


@router.put("/{script_id}")
async def update_script(
    script_id: str,
    request: ScriptUpdateRequest,
    db: Session = Depends(get_db)
):
    """スクリプト更新"""
    try:
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == script_id
        ).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="スクリプトが見つかりません")
        
        # 更新可能フィールドの更新
        update_data = request.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(script, field, value)
        
        db.commit()
        db.refresh(script)
        
        return {
            "message": "スクリプトを更新しました",
            "script_id": script_id,
            "updated_fields": list(update_data.keys())
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"スクリプト更新エラー: {str(e)}")


@router.post("/{script_id}/activate")
async def activate_script(
    script_id: str,
    db: Session = Depends(get_db)
):
    """スクリプト有効化"""
    try:
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == script_id
        ).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="スクリプトが見つかりません")
        
        # 他のアクティブなスクリプトを無効化
        db.query(ImprovementScript).filter(
            ImprovementScript.is_active == True
        ).update({"is_active": False})
        
        # 対象スクリプトを有効化
        script.is_active = True
        script.status = "active"
        script.activated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "message": "スクリプトを有効化しました",
            "script_id": script_id,
            "activated_at": script.activated_at
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"スクリプト有効化エラー: {str(e)}")


@router.post("/{script_id}/feedback")
async def submit_feedback(
    script_id: str,
    request: ScriptFeedbackRequest,
    db: Session = Depends(get_db)
):
    """スクリプトフィードバック投稿"""
    try:
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == script_id
        ).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="スクリプトが見つかりません")
        
        feedback = ScriptFeedback(
            script_id=script_id,
            **request.dict(exclude_unset=True)
        )
        
        db.add(feedback)
        db.commit()
        
        return {
            "message": "フィードバックを投稿しました",
            "feedback_id": str(feedback.id)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"フィードバック投稿エラー: {str(e)}")


@router.get("/{script_id}/feedback")
async def get_script_feedback(
    script_id: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """スクリプトフィードバック取得"""
    try:
        feedback_entries = db.query(ScriptFeedback).filter(
            ScriptFeedback.script_id == script_id
        ).order_by(
            ScriptFeedback.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "feedback": [
                {
                    "id": str(fb.id),
                    "counselor_name": fb.counselor_name,
                    "role": fb.role,
                    "rating": fb.rating,
                    "usability_score": fb.usability_score,
                    "effectiveness_score": fb.effectiveness_score,
                    "positive_points": fb.positive_points,
                    "improvement_suggestions": fb.improvement_suggestions,
                    "created_at": fb.created_at
                }
                for fb in feedback_entries
            ],
            "total": db.query(ScriptFeedback).filter(
                ScriptFeedback.script_id == script_id
            ).count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"フィードバック取得エラー: {str(e)}")


@router.get("/{script_id}/analytics")
async def get_script_analytics(
    script_id: str,
    db: Session = Depends(get_db)
):
    """スクリプト分析データ取得"""
    try:
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == script_id
        ).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="スクリプトが見つかりません")
        
        # 使用分析データ取得
        usage_analytics = db.query(ScriptUsageAnalytics).filter(
            ScriptUsageAnalytics.script_id == script_id
        ).order_by(ScriptUsageAnalytics.created_at.desc()).all()
        
        # パフォーマンスメトリクス取得
        performance_metrics = db.query(ScriptPerformanceMetrics).filter(
            ScriptPerformanceMetrics.script_id == script_id
        ).order_by(ScriptPerformanceMetrics.measurement_date.desc()).all()
        
        # フィードバックサマリー
        feedback_summary = db.query(ScriptFeedback).filter(
            ScriptFeedback.script_id == script_id
        ).all()
        
        avg_rating = sum(fb.rating for fb in feedback_summary if fb.rating) / len(feedback_summary) if feedback_summary else 0
        avg_usability = sum(fb.usability_score for fb in feedback_summary if fb.usability_score) / len(feedback_summary) if feedback_summary else 0
        avg_effectiveness = sum(fb.effectiveness_score for fb in feedback_summary if fb.effectiveness_score) / len(feedback_summary) if feedback_summary else 0
        
        return {
            "script_id": script_id,
            "usage_analytics": [
                {
                    "id": str(ua.id),
                    "usage_period": f"{ua.usage_start_date} - {ua.usage_end_date}",
                    "total_sessions": ua.total_sessions,
                    "successful_sessions": ua.successful_sessions,
                    "conversion_rate": ua.conversion_rate,
                    "improvement_rate": ua.improvement_rate,
                    "statistical_significance": ua.statistical_significance
                }
                for ua in usage_analytics
            ],
            "performance_metrics": [
                {
                    "measurement_date": pm.measurement_date,
                    "conversion_rate": pm.conversion_rate,
                    "improvement_percentage": pm.improvement_percentage,
                    "customer_satisfaction_score": pm.customer_satisfaction_score
                }
                for pm in performance_metrics
            ],
            "feedback_summary": {
                "total_feedback": len(feedback_summary),
                "average_rating": round(avg_rating, 2),
                "average_usability": round(avg_usability, 2),
                "average_effectiveness": round(avg_effectiveness, 2)
            },
            "quality_metrics": script.quality_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析データ取得エラー: {str(e)}")


@router.delete("/{script_id}")
async def delete_script(
    script_id: str,
    db: Session = Depends(get_db)
):
    """スクリプト削除"""
    try:
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == script_id
        ).first()
        
        if not script:
            raise HTTPException(status_code=404, detail="スクリプトが見つかりません")
        
        if script.is_active:
            raise HTTPException(status_code=400, detail="アクティブなスクリプトは削除できません")
        
        # 関連データを削除
        db.query(ScriptFeedback).filter(
            ScriptFeedback.script_id == script_id
        ).delete()
        
        db.query(ScriptUsageAnalytics).filter(
            ScriptUsageAnalytics.script_id == script_id
        ).delete()
        
        db.query(ScriptPerformanceMetrics).filter(
            ScriptPerformanceMetrics.script_id == script_id
        ).delete()
        
        db.delete(script)
        db.commit()
        
        return {
            "message": "スクリプトを削除しました",
            "script_id": script_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"スクリプト削除エラー: {str(e)}")


# バックグラウンドタスク
async def execute_script_generation(
    script_id: str,
    request_data: Dict[str, Any],
    db: Session
):
    """スクリプト生成をバックグラウンドで実行"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        import asyncio
        from datetime import datetime
        
        logger.info(f"🚀 Starting script generation for script_id: {script_id}")
        logger.info(f"📋 Request data: {request_data}")
        
        # スクリプト開始
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == script_id
        ).first()
        
        if not script:
            logger.error(f"❌ Script {script_id} not found in database")
            return
        
        logger.info(f"✅ Script found: {script.title}")
        script.status = "generating"
        script.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"📊 Script status updated to 'generating'")
        
        # 最新データでクラスタリングを実行
        logger.info(f"🔄 Starting clustering process")
        from app.db.session import VectorSessionLocal
        from app.models.vector import ClusterResult, SuccessConversationVector
        from app.services.clustering_service import ClusteringService
        
        vector_db = VectorSessionLocal()
        try:
            logger.info(f"📊 Connected to vector database")
            # 利用可能なベクトルデータを確認
            vector_count = vector_db.query(SuccessConversationVector).count()
            logger.info(f"📈 Found {vector_count} vectors in database")
            
            if vector_count < 5:  # 最小クラスタリング要件
                logger.error(f"❌ Insufficient data for clustering: {vector_count} vectors (minimum: 5)")
                script.status = "failed"
                script.updated_at = datetime.utcnow()
                db.commit()
                return
            
            # クラスタリング実行
            logger.info(f"🎯 Starting clustering with {vector_count} vectors")
            clustering_service = ClusteringService(vector_db)
            cluster_result = await clustering_service.perform_clustering(
                algorithm="kmeans",
                k_range=(2, min(10, vector_count // 2)),
                auto_select_k=True
            )
            
            cluster_result_id = str(cluster_result["cluster_result_id"])
            logger.info(f"✅ Clustering completed with ID: {cluster_result_id}")
            db.commit()
            
        finally:
            vector_db.close()
        
        # スクリプト生成サービス実行
        logger.info(f"🤖 Starting script generation service")
        # 新しいベクトルDBセッションを作成
        vector_db_for_generation = next(get_vector_db())
        generation_service = create_script_generation_service(db, vector_db_for_generation)
        
        analysis_data = {
            "cluster_result_id": cluster_result_id
        }
        
        logger.info(f"📊 Analysis data prepared: {analysis_data}")
        
        # 生成実行
        logger.info(f"🎯 Executing script generation")
        result = await generation_service.generate_improvement_script(
            analysis_data=analysis_data
        )
        
        logger.info(f"✅ Script generation completed")
        logger.info(f"📋 Result keys: {list(result.keys()) if result else 'None'}")
        
        # スクリプト内容を更新
        script.content = result.get("script", {})
        script.generation_metadata = result.get("generation_metadata", {})
        script.quality_metrics = result.get("quality_metrics", {})
        script.cluster_result_id = cluster_result_id
        script.based_on_failure_sessions = []
        script.status = "review"
        
        logger.info(f"💾 Saving script to database")
        db.commit()
        
        # ベクトルDBセッションをクローズ
        vector_db_for_generation.close()
        
        # スクリプト完了
        script.status = "completed"
        script.updated_at = datetime.utcnow()
        
        logger.info(f"🎉 Script generation completed successfully for {script_id}")
        db.commit()
        
    except Exception as e:
        logger.error(f"❌ Script generation failed for {script_id}: {str(e)}")
        logger.error(f"🔍 Error type: {type(e).__name__}")
        
        # エラー処理
        script = db.query(ImprovementScript).filter(
            ImprovementScript.id == script_id
        ).first()
        
        if script:
            script.status = "failed"
            script.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"📊 Script status updated to 'failed'")
        else:
            logger.error(f"❌ Could not find script {script_id} to update failure status")


# ヘルスチェック
@router.get("/health")
async def health_check():
    """スクリプトサービスのヘルスチェック"""
    return {
        "status": "healthy",
        "service": "script-generation",
        "features": [
            "script_generation",
            "quality_analysis",
            "feedback_management",
            "performance_analytics"
        ]
    }