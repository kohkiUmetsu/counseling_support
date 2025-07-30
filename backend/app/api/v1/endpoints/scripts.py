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
from app.models.script import (
    ImprovementScript, 
    ScriptGenerationJob, 
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
    cluster_result_id: str = Field(..., description="クラスタリング結果ID")
    failure_conversations: List[Dict[str, Any]] = Field(default=[], description="分析対象失敗会話")
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
        job_id = f"script_gen_{uuid.uuid4().hex[:8]}"
        
        # ジョブレコード作成
        generation_job = ScriptGenerationJob(
            job_id=job_id,
            input_data={
                "cluster_result_id": request.cluster_result_id,
                "failure_conversations": request.failure_conversations,
                "title": request.title,
                "description": request.description
            },
            status="pending"
        )
        
        db.add(generation_job)
        db.commit()
        
        # バックグラウンドで生成処理を実行
        background_tasks.add_task(
            execute_script_generation,
            job_id,
            request.dict(),
            db
        )
        
        return ScriptGenerationResponse(
            job_id=job_id,
            status="pending",
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
        job = db.query(ScriptGenerationJob).filter(
            ScriptGenerationJob.job_id == job_id
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="ジョブが見つかりません")
        
        response = {
            "job_id": job_id,
            "status": job.status,
            "progress_percentage": job.progress_percentage,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        }
        
        if job.status == "completed" and job.result_script_id:
            # 完了時は生成されたスクリプト情報も返却
            script = db.query(ImprovementScript).filter(
                ImprovementScript.id == job.result_script_id
            ).first()
            
            if script:
                response["script"] = {
                    "id": str(script.id),
                    "title": script.title,
                    "version": script.version,
                    "status": script.status,
                    "quality_metrics": script.quality_metrics
                }
        
        elif job.status == "failed":
            response["error_message"] = job.error_message
        
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
        
    except Exception as e:
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
    job_id: str,
    request_data: Dict[str, Any],
    db: Session
):
    """スクリプト生成をバックグラウンドで実行"""
    try:
        import asyncio
        from datetime import datetime
        
        # ジョブ開始
        job = db.query(ScriptGenerationJob).filter(
            ScriptGenerationJob.job_id == job_id
        ).first()
        
        if not job:
            return
        
        job.status = "running"
        job.started_at = datetime.utcnow()
        job.progress_percentage = 10
        db.commit()
        
        # スクリプト生成サービス実行
        generation_service = create_script_generation_service(db)
        
        analysis_data = {
            "cluster_result_id": request_data["cluster_result_id"],
            "failure_conversations": request_data["failure_conversations"]
        }
        
        job.progress_percentage = 30
        db.commit()
        
        # 生成実行
        result = await generation_service.generate_improvement_script(
            analysis_data=analysis_data
        )
        
        job.progress_percentage = 80
        db.commit()
        
        # スクリプト保存
        script = ImprovementScript(
            title=request_data.get("title", f"改善スクリプト {datetime.utcnow().strftime('%Y%m%d_%H%M')}"),
            description=request_data.get("description"),
            version="1.0.0",
            content=result["script"],
            generation_metadata=result["generation_metadata"],
            quality_metrics=result["quality_metrics"],
            cluster_result_id=request_data["cluster_result_id"],
            based_on_failure_sessions=[
                fc.get("session_id") for fc in request_data["failure_conversations"] 
                if fc.get("session_id")
            ],
            status="review"
        )
        
        db.add(script)
        db.commit()
        
        # ジョブ完了
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.progress_percentage = 100
        job.result_script_id = script.id
        job.token_usage = result["generation_metadata"].get("openai_usage")
        job.cost_estimate = result["generation_metadata"].get("cost_estimate")
        job.processing_time = result["generation_metadata"].get("processing_time")
        
        db.commit()
        
    except Exception as e:
        # エラー処理
        job = db.query(ScriptGenerationJob).filter(
            ScriptGenerationJob.job_id == job_id
        ).first()
        
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()


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