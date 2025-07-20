"""
ベクトル検索・クラスタリング関連のAPIエンドポイント
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.services.embedding_service import embedding_service
from app.services.vector_search_service import create_vector_search_service
from app.services.clustering_service import create_clustering_service
from app.services.representative_extraction_service import create_representative_extraction_service


router = APIRouter()


# Pydanticモデル
class VectorSearchRequest(BaseModel):
    query_text: str = Field(..., description="検索クエリテキスト")
    top_k: int = Field(default=10, ge=1, le=50, description="取得する結果数")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="類似度閾値")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="フィルタ条件")


class FailureToSuccessSearchRequest(BaseModel):
    failure_conversation_text: str = Field(..., description="失敗会話テキスト")
    top_k: int = Field(default=5, ge=1, le=20, description="取得する類似成功例数")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="類似度閾値")
    include_analysis: bool = Field(default=True, description="詳細分析を含めるかどうか")


class ClusteringRequest(BaseModel):
    algorithm: str = Field(default="kmeans", description="クラスタリングアルゴリズム")
    k_range: tuple = Field(default=(2, 15), description="K-meansのクラスタ数範囲")
    auto_select_k: bool = Field(default=True, description="最適クラスタ数の自動決定")
    clustering_params: Optional[Dict[str, Any]] = Field(default=None, description="アルゴリズム固有パラメータ")


class RepresentativeExtractionRequest(BaseModel):
    cluster_result_id: str = Field(..., description="クラスタリング結果ID")
    max_representatives_per_cluster: int = Field(default=3, ge=1, le=10, description="クラスタあたりの最大代表例数")
    min_quality_score: float = Field(default=0.5, ge=0.0, le=1.0, description="最小品質スコア")


class EmbeddingRequest(BaseModel):
    texts: List[str] = Field(..., description="ベクトル化するテキストリスト")
    include_metadata: bool = Field(default=True, description="メタデータを含めるかどうか")


# レスポンスモデル
class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    processing_time: float
    query_info: Dict[str, Any]


class ClusteringResponse(BaseModel):
    cluster_result_id: str
    algorithm: str
    cluster_count: int
    silhouette_score: float
    cluster_assignments: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]


class RepresentativeExtractionResponse(BaseModel):
    cluster_result_id: str
    representatives: List[Dict[str, Any]]
    summary: Dict[str, Any]


@router.post("/search", response_model=VectorSearchResponse)
async def search_similar_conversations(
    request: VectorSearchRequest,
    db: Session = Depends(get_db)
):
    """類似する成功会話を検索"""
    try:
        import time
        start_time = time.time()
        
        # 検索クエリをベクトル化
        query_embedding = await embedding_service.embed_conversation_for_search(
            request.query_text, "search"
        )
        
        # ベクトル検索実行
        search_service = create_vector_search_service(db)
        results = await search_service.search_similar_success_conversations(
            query_embedding=query_embedding,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            filters=request.filters
        )
        
        processing_time = time.time() - start_time
        
        return VectorSearchResponse(
            results=results,
            total=len(results),
            processing_time=processing_time,
            query_info={
                "query_text": request.query_text,
                "embedding_dimensions": len(query_embedding),
                "filters_applied": request.filters or {}
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ベクトル検索エラー: {str(e)}")


@router.post("/search-failure-to-success")
async def search_failure_to_success_mappings(
    request: FailureToSuccessSearchRequest,
    db: Session = Depends(get_db)
):
    """失敗会話から類似する成功会話を検索し、改善ヒントを生成"""
    try:
        search_service = create_vector_search_service(db)
        result = await search_service.search_similar_for_failure_conversation(
            failure_conversation_text=request.failure_conversation_text,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            include_analysis=request.include_analysis
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"失敗→成功検索エラー: {str(e)}")


@router.post("/clustering", response_model=ClusteringResponse)
async def perform_clustering(
    request: ClusteringRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """成功会話ベクトルのクラスタリング実行"""
    try:
        clustering_service = create_clustering_service(db)
        result = await clustering_service.perform_clustering(
            algorithm=request.algorithm,
            k_range=request.k_range,
            auto_select_k=request.auto_select_k,
            clustering_params=request.clustering_params
        )
        
        # バックグラウンドで代表例抽出を実行
        background_tasks.add_task(
            extract_representatives_background,
            db, result['cluster_result_id']
        )
        
        return ClusteringResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"クラスタリングエラー: {str(e)}")


@router.post("/extract-representatives", response_model=RepresentativeExtractionResponse)
async def extract_cluster_representatives(
    request: RepresentativeExtractionRequest,
    db: Session = Depends(get_db)
):
    """クラスタ代表例の抽出"""
    try:
        extraction_service = create_representative_extraction_service(db)
        result = await extraction_service.extract_cluster_representatives(
            cluster_result_id=request.cluster_result_id,
            max_representatives_per_cluster=request.max_representatives_per_cluster,
            min_quality_score=request.min_quality_score
        )
        
        return RepresentativeExtractionResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"代表例抽出エラー: {str(e)}")


@router.post("/embed")
async def embed_texts(
    request: EmbeddingRequest,
    db: Session = Depends(get_db)
):
    """テキストのベクトル化"""
    try:
        if len(request.texts) > 100:
            raise HTTPException(status_code=400, detail="一度に処理できるテキストは100件までです")
        
        results = await embedding_service.embed_texts_with_chunking(
            texts=request.texts,
            include_metadata=request.include_metadata
        )
        
        return {
            "embeddings": results,
            "total_chunks": len(results),
            "dimensions": len(results[0]['embedding']) if results else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ベクトル化エラー: {str(e)}")


@router.get("/clustering/{cluster_result_id}/representatives")
async def get_representatives_for_script_generation(
    cluster_result_id: str,
    max_total_representatives: int = 8,
    db: Session = Depends(get_db)
):
    """スクリプト生成用の最適化された代表例セットを取得"""
    try:
        extraction_service = create_representative_extraction_service(db)
        representatives = await extraction_service.get_representatives_for_script_generation(
            cluster_result_id=cluster_result_id,
            max_total_representatives=max_total_representatives
        )
        
        return {
            "representatives": representatives,
            "total": len(representatives),
            "cluster_result_id": cluster_result_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"代表例取得エラー: {str(e)}")


@router.get("/clustering/results")
async def get_clustering_results(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """クラスタリング結果の一覧取得"""
    try:
        from app.models.vector import ClusterResult
        
        results = db.query(ClusterResult).order_by(
            ClusterResult.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "results": [
                {
                    "id": str(result.id),
                    "algorithm": result.algorithm,
                    "cluster_count": result.cluster_count,
                    "silhouette_score": result.silhouette_score,
                    "created_at": result.created_at,
                    "parameters": result.parameters
                }
                for result in results
            ],
            "total": db.query(ClusterResult).count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"クラスタリング結果取得エラー: {str(e)}")


@router.delete("/clustering/{cluster_result_id}")
async def delete_clustering_result(
    cluster_result_id: str,
    db: Session = Depends(get_db)
):
    """クラスタリング結果の削除"""
    try:
        from app.models.vector import ClusterResult, ClusterAssignment, ClusterRepresentative
        
        # 関連データを削除
        db.query(ClusterRepresentative).filter(
            ClusterRepresentative.cluster_result_id == cluster_result_id
        ).delete()
        
        db.query(ClusterAssignment).filter(
            ClusterAssignment.cluster_result_id == cluster_result_id
        ).delete()
        
        result = db.query(ClusterResult).filter(
            ClusterResult.id == cluster_result_id
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="クラスタリング結果が見つかりません")
        
        db.delete(result)
        db.commit()
        
        return {"message": "クラスタリング結果を削除しました", "cluster_result_id": cluster_result_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"削除エラー: {str(e)}")


# バックグラウンドタスク
async def extract_representatives_background(db: Session, cluster_result_id: str):
    """代表例抽出をバックグラウンドで実行"""
    try:
        extraction_service = create_representative_extraction_service(db)
        await extraction_service.extract_cluster_representatives(
            cluster_result_id=cluster_result_id,
            max_representatives_per_cluster=3,
            min_quality_score=0.5
        )
    except Exception as e:
        print(f"バックグラウンド代表例抽出エラー: {e}")  # ログに記録


# ヘルスチェック
@router.get("/health")
async def health_check():
    """ベクトル検索サービスのヘルスチェック"""
    return {
        "status": "healthy",
        "service": "vector-search",
        "features": [
            "embedding",
            "similarity_search", 
            "clustering",
            "representative_extraction"
        ]
    }