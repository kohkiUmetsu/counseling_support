from typing import List, Dict, Any, Optional, Tuple
import asyncio
import time
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import redis
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.core.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)

class VectorSearchOptimizationService:
    """
    ベクトル検索のパフォーマンス最適化サービス
    - クエリキャッシュ
    - 並列処理
    - インデックス最適化
    - メモリ使用量最適化
    """
    
    def __init__(self):
        self.redis_client = self._init_redis()
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.cache_ttl = 3600  # 1時間
        self.batch_size = 100
        
    def _init_redis(self) -> Optional[redis.Redis]:
        """Redisクライアントの初期化"""
        try:
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                return redis.from_url(settings.REDIS_URL, decode_responses=True)
            else:
                # Redis未設定の場合はキャッシュなしで動作
                logger.warning("Redis未設定のため、キャッシュ機能は無効です")
                return None
        except Exception as e:
            logger.error(f"Redis接続エラー: {e}")
            return None
    
    async def optimized_vector_search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.7,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        最適化されたベクトル検索
        
        Args:
            query_vector: クエリベクトル
            top_k: 取得件数
            filters: フィルタ条件
            similarity_threshold: 類似度閾値
            use_cache: キャッシュ使用フラグ
            
        Returns:
            検索結果リスト
        """
        start_time = time.time()
        
        try:
            # キャッシュキーの生成
            cache_key = self._generate_cache_key(query_vector, top_k, filters, similarity_threshold)
            
            # キャッシュからの取得を試行
            if use_cache and self.redis_client:
                cached_result = await self._get_from_cache(cache_key)
                if cached_result:
                    logger.info(f"キャッシュヒット - 検索時間: {time.time() - start_time:.3f}秒")
                    return cached_result
            
            # データベース検索実行
            search_results = await self._execute_optimized_search(
                query_vector, top_k, filters, similarity_threshold
            )
            
            # 結果をキャッシュに保存
            if use_cache and self.redis_client:
                await self._save_to_cache(cache_key, search_results)
            
            search_time = time.time() - start_time
            logger.info(f"最適化検索完了 - {len(search_results)}件取得、実行時間: {search_time:.3f}秒")
            
            return search_results
            
        except Exception as e:
            logger.error(f"最適化ベクトル検索でエラー: {e}")
            raise
    
    async def _execute_optimized_search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """最適化されたデータベース検索の実行"""
        
        # クエリの最適化
        optimized_query = self._build_optimized_query(filters, similarity_threshold)
        
        # データベース接続とクエリ実行
        db = next(get_db())
        try:
            # pgvectorの最適化設定
            await self._set_pgvector_optimization(db)
            
            # メインクエリ実行
            result = db.execute(
                text(optimized_query),
                {
                    "query_vector": query_vector.tolist(),
                    "top_k": top_k,
                    "similarity_threshold": similarity_threshold,
                    **self._prepare_filter_params(filters)
                }
            )
            
            # 結果の処理と構造化
            raw_results = result.fetchall()
            return self._process_search_results(raw_results)
            
        finally:
            db.close()
    
    def _build_optimized_query(
        self,
        filters: Optional[Dict[str, Any]],
        similarity_threshold: float
    ) -> str:
        """最適化されたSQLクエリの構築"""
        
        base_query = """
        SELECT 
            v.id,
            v.session_id,
            v.chunk_text,
            v.metadata,
            v.created_at,
            (v.embedding <=> :query_vector) as similarity_score
        FROM success_conversation_vectors v
        """
        
        # フィルタ条件の追加
        where_conditions = ["(v.embedding <=> :query_vector) <= :similarity_threshold"]
        
        if filters:
            if filters.get('success_rate_min'):
                where_conditions.append("(v.metadata->>'success_rate')::float >= :success_rate_min")
            
            if filters.get('date_range'):
                where_conditions.append("v.created_at BETWEEN :date_start AND :date_end")
            
            if filters.get('counselor_ids'):
                where_conditions.append("v.metadata->>'counselor_id' = ANY(:counselor_ids)")
        
        where_clause = " WHERE " + " AND ".join(where_conditions)
        
        # 最適化されたORDER BYとLIMIT
        order_limit = """
        ORDER BY v.embedding <=> :query_vector
        LIMIT :top_k
        """
        
        return base_query + where_clause + order_limit
    
    async def _set_pgvector_optimization(self, db: Session):
        """pgvectorの最適化設定"""
        try:
            # IVFFLATインデックスの最適化パラメータ設定
            db.execute(text("SET ivfflat.probes = 10"))
            
            # 並列処理の有効化
            db.execute(text("SET max_parallel_workers_per_gather = 4"))
            
            # ワークメモリの最適化
            db.execute(text("SET work_mem = '256MB'"))
            
            db.commit()
            
        except Exception as e:
            logger.warning(f"pgvector最適化設定でエラー: {e}")
    
    def _prepare_filter_params(self, filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """フィルタパラメータの準備"""
        params = {}
        
        if filters:
            if filters.get('success_rate_min'):
                params['success_rate_min'] = filters['success_rate_min']
            
            if filters.get('date_range'):
                params['date_start'] = filters['date_range'][0]
                params['date_end'] = filters['date_range'][1]
            
            if filters.get('counselor_ids'):
                params['counselor_ids'] = filters['counselor_ids']
        
        return params
    
    def _process_search_results(self, raw_results) -> List[Dict[str, Any]]:
        """検索結果の処理と構造化"""
        processed_results = []
        
        for row in raw_results:
            processed_results.append({
                "id": str(row.id),
                "session_id": str(row.session_id),
                "text": row.chunk_text,
                "metadata": row.metadata,
                "similarity_score": float(row.similarity_score),
                "created_at": row.created_at.isoformat()
            })
        
        return processed_results
    
    async def batch_vector_search(
        self,
        query_vectors: List[np.ndarray],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        複数ベクトルの並列バッチ検索
        
        Args:
            query_vectors: クエリベクトルのリスト
            top_k: 各クエリの取得件数
            filters: フィルタ条件
            
        Returns:
            各クエリの検索結果リスト
        """
        start_time = time.time()
        
        try:
            # バッチサイズでチャンク分割
            chunks = [
                query_vectors[i:i + self.batch_size] 
                for i in range(0, len(query_vectors), self.batch_size)
            ]
            
            all_results = []
            
            for chunk in chunks:
                # 並列実行用のタスク作成
                tasks = [
                    self.optimized_vector_search(
                        query_vector=vector,
                        top_k=top_k,
                        filters=filters,
                        use_cache=True
                    )
                    for vector in chunk
                ]
                
                # 並列実行
                chunk_results = await asyncio.gather(*tasks)
                all_results.extend(chunk_results)
            
            total_time = time.time() - start_time
            logger.info(f"バッチ検索完了 - {len(query_vectors)}件のクエリ、実行時間: {total_time:.3f}秒")
            
            return all_results
            
        except Exception as e:
            logger.error(f"バッチベクトル検索でエラー: {e}")
            raise
    
    def _generate_cache_key(
        self,
        query_vector: np.ndarray,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        similarity_threshold: float
    ) -> str:
        """キャッシュキーの生成"""
        
        # ベクトルのハッシュ化（メモリ効率を考慮して先頭部分のみ使用）
        vector_hash = hashlib.md5(query_vector[:100].tobytes()).hexdigest()[:16]
        
        # フィルタのハッシュ化
        filter_str = json.dumps(filters or {}, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
        
        return f"vector_search:{vector_hash}:{top_k}:{similarity_threshold}:{filter_hash}"
    
    async def _get_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """キャッシュからの取得"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.warning(f"キャッシュ取得エラー: {e}")
            return None
    
    async def _save_to_cache(self, cache_key: str, data: List[Dict[str, Any]]):
        """キャッシュへの保存"""
        try:
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(data, ensure_ascii=False)
            )
        except Exception as e:
            logger.warning(f"キャッシュ保存エラー: {e}")
    
    async def optimize_database_indices(self, db: Session):
        """データベースインデックスの最適化"""
        try:
            logger.info("データベースインデックス最適化開始")
            
            # VACUUMによるインデックス最適化
            db.execute(text("VACUUM ANALYZE success_conversation_vectors"))
            
            # インデックス統計の更新
            db.execute(text("ANALYZE success_conversation_vectors"))
            
            # IVFFLATインデックスの再構築（必要に応じて）
            index_health_query = text("""
                SELECT schemaname, tablename, attname, n_distinct, correlation
                FROM pg_stats 
                WHERE tablename = 'success_conversation_vectors'
                AND attname = 'embedding'
            """)
            
            index_stats = db.execute(index_health_query).fetchone()
            
            if index_stats and abs(index_stats.correlation) < 0.1:
                logger.info("インデックス再構築が必要と判定")
                # 注意: 本番環境では慎重に実行
                # db.execute(text("REINDEX INDEX success_conversation_vectors_embedding_idx"))
            
            db.commit()
            logger.info("データベースインデックス最適化完了")
            
        except Exception as e:
            logger.error(f"インデックス最適化でエラー: {e}")
            db.rollback()
            raise
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンスメトリクスの取得"""
        
        cache_stats = {"cache_enabled": False}
        if self.redis_client:
            try:
                info = self.redis_client.info()
                cache_stats = {
                    "cache_enabled": True,
                    "cache_hits": info.get("keyspace_hits", 0),
                    "cache_misses": info.get("keyspace_misses", 0),
                    "memory_usage": info.get("used_memory_human", "Unknown")
                }
            except Exception as e:
                logger.warning(f"Redis統計取得エラー: {e}")
        
        return {
            "optimization_features": {
                "query_cache": self.redis_client is not None,
                "parallel_processing": True,
                "batch_processing": True,
                "index_optimization": True
            },
            "configuration": {
                "cache_ttl": self.cache_ttl,
                "batch_size": self.batch_size,
                "thread_pool_workers": self.thread_pool._max_workers
            },
            "cache_statistics": cache_stats
        }
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """キャッシュのクリア"""
        if not self.redis_client:
            return
        
        try:
            if pattern:
                keys = self.redis_client.keys(f"vector_search:{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"{len(keys)}件のキャッシュエントリをクリア")
            else:
                keys = self.redis_client.keys("vector_search:*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"全キャッシュ({len(keys)}件)をクリア")
                    
        except Exception as e:
            logger.error(f"キャッシュクリアでエラー: {e}")
            raise