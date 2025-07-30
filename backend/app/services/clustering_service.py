"""
K-means/HDBSCAN を使用したクラスタリングサービス
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.cluster import KMeans, HDBSCAN
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.vector import (
    SuccessConversationVector,
    ClusterResult,
    ClusterAssignment,
    ClusterRepresentative
)


logger = logging.getLogger(__name__)


class ClusteringService:
    """成功会話ベクトルのクラスタリングサービス"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def perform_clustering(
        self,
        algorithm: str = "kmeans",
        k_range: Tuple[int, int] = (2, 15),
        auto_select_k: bool = True,
        clustering_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        成功会話ベクトルのクラスタリング実行
        
        Args:
            algorithm: 'kmeans' or 'hdbscan'
            k_range: K-meansの場合のクラスタ数範囲
            auto_select_k: 最適クラスタ数の自動決定
            clustering_params: アルゴリズム固有のパラメータ
            
        Returns:
            {
                'cluster_result_id': 'uuid',
                'algorithm': 'kmeans',
                'cluster_count': 5,
                'silhouette_score': 0.65,
                'cluster_assignments': [...],
                'cluster_centroids': [...],
                'performance_metrics': {...}
            }
        """
        try:
            # 1. 成功会話ベクトルを取得
            vectors_data = self._get_success_vectors()
            if len(vectors_data) < 2:
                raise ValueError("クラスタリングには最低2つの成功会話ベクトルが必要です")
            
            vectors = np.array([item['embedding'] for item in vectors_data])
            vector_ids = [item['id'] for item in vectors_data]
            
            logger.info(f"クラスタリング対象: {len(vectors)}件のベクトル")
            
            # 2. アルゴリズムに応じてクラスタリング実行
            if algorithm == "kmeans":
                clustering_result = await self._perform_kmeans_clustering(
                    vectors, k_range, auto_select_k, clustering_params
                )
            elif algorithm == "hdbscan":
                clustering_result = await self._perform_hdbscan_clustering(
                    vectors, clustering_params
                )
            else:
                raise ValueError(f"サポートされていないアルゴリズム: {algorithm}")
            
            # 3. 結果をデータベースに保存
            cluster_result_id = await self._save_clustering_result(
                algorithm=algorithm,
                cluster_count=clustering_result['cluster_count'],
                parameters=clustering_result['parameters'],
                silhouette_score=clustering_result['silhouette_score'],
                labels=clustering_result['labels'],
                vector_ids=vector_ids,
                centroids=clustering_result.get('centroids')
            )
            
            return {
                'cluster_result_id': str(cluster_result_id),
                'algorithm': algorithm,
                'cluster_count': clustering_result['cluster_count'],
                'silhouette_score': clustering_result['silhouette_score'],
                'cluster_assignments': clustering_result['assignments'],
                'cluster_centroids': clustering_result.get('centroids'),
                'performance_metrics': clustering_result['performance_metrics']
            }
            
        except Exception as e:
            logger.error(f"クラスタリング実行エラー: {e}")
            raise
    
    def _get_success_vectors(self) -> List[Dict[str, Any]]:
        """成功会話ベクトルを取得"""
        query = self.db.query(SuccessConversationVector).filter(
            SuccessConversationVector.is_success == True
        ).all()
        
        return [
            {
                'id': str(vector.id),
                'session_id': str(vector.session_id),
                'embedding': vector.embedding,
                'text': vector.chunk_text
            }
            for vector in query
        ]
    
    async def _perform_kmeans_clustering(
        self,
        vectors: np.ndarray,
        k_range: Tuple[int, int],
        auto_select_k: bool,
        params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """K-meansクラスタリング実行"""
        
        # デフォルトパラメータ
        default_params = {
            'n_init': 10,
            'max_iter': 300,
            'random_state': 42
        }
        if params:
            default_params.update(params)
        
        best_k = k_range[0]
        best_score = -1
        best_model = None
        scores_by_k = {}
        
        if auto_select_k:
            # 最適なクラスタ数を探索
            logger.info(f"最適クラスタ数探索中: {k_range[0]}-{k_range[1]}")
            
            for k in range(k_range[0], min(k_range[1] + 1, len(vectors))):
                kmeans = KMeans(n_clusters=k, **default_params)
                labels = kmeans.fit_predict(vectors)
                
                # シルエット係数で評価
                if len(set(labels)) > 1:  # クラスタが複数ある場合のみ
                    silhouette_avg = float(silhouette_score(vectors, labels))
                    scores_by_k[k] = silhouette_avg
                    
                    if silhouette_avg > best_score:
                        best_score = silhouette_avg
                        best_k = k
                        best_model = kmeans
                        
                    logger.info(f"K={k}: シルエット係数={silhouette_avg:.3f}")
        else:
            # 指定されたクラスタ数で実行
            best_k = k_range[0]
            best_model = KMeans(n_clusters=best_k, **default_params)
            labels = best_model.fit_predict(vectors)
            best_score = silhouette_score(vectors, labels) if len(set(labels)) > 1 else 0
        
        # 最終的なクラスタリング結果
        final_labels = best_model.fit_predict(vectors)
        centroids = best_model.cluster_centers_
        
        # 各ベクトルの重心からの距離を計算
        distances_to_centroids = []
        for i, (vector, label) in enumerate(zip(vectors, final_labels)):
            label = int(label)  # numpyスカラーをintに変換
            if label >= 0:  # 有効なクラスタ
                centroid = centroids[label]
                distance = np.linalg.norm(vector - centroid)
                distances_to_centroids.append(distance)
            else:
                distances_to_centroids.append(float('inf'))
        
        # パフォーマンスメトリクス
        performance_metrics = {
            'silhouette_score': best_score,
            'inertia': best_model.inertia_,
            'n_iter': best_model.n_iter_,
            'scores_by_k': scores_by_k
        }
        
        if len(set(final_labels)) > 1:
            performance_metrics['calinski_harabasz_score'] = calinski_harabasz_score(
                vectors, final_labels
            )
        
        # クラスタ割り当て情報
        assignments = []
        for i, (label, distance) in enumerate(zip(final_labels, distances_to_centroids)):
            assignments.append({
                'vector_index': i,
                'cluster_label': int(label),
                'distance_to_centroid': float(distance)
            })
        
        return {
            'cluster_count': best_k,
            'labels': final_labels.tolist(),
            'centroids': centroids.tolist(),
            'silhouette_score': best_score,
            'parameters': default_params,
            'assignments': assignments,
            'performance_metrics': performance_metrics
        }
    
    async def _perform_hdbscan_clustering(
        self,
        vectors: np.ndarray,
        params: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """HDBSCANクラスタリング実行"""
        
        # デフォルトパラメータ
        default_params = {
            'min_cluster_size': max(5, len(vectors) // 10),  # 動的に調整
            'min_samples': 3,
            'metric': 'cosine',
            'cluster_selection_epsilon': 0.0,
            'alpha': 1.0
        }
        if params:
            default_params.update(params)
        
        logger.info(f"HDBSCAN実行中: パラメータ={default_params}")
        
        # HDBSCANクラスタリング実行
        clusterer = HDBSCAN(**default_params)
        cluster_labels = clusterer.fit_predict(vectors)
        
        # ノイズ（-1ラベル）を除いたクラスタ数
        unique_labels = set(cluster_labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        
        # シルエット係数計算（ノイズを除く）
        silhouette_avg = 0.0
        if n_clusters > 1:
            valid_indices = cluster_labels >= 0
            if np.sum(valid_indices) > 1:
                silhouette_avg = float(silhouette_score(
                    vectors[valid_indices], 
                    cluster_labels[valid_indices]
                ))
        
        # 各ベクトルの所属クラスタ重心からの距離を計算
        distances_to_centroids = []
        cluster_centroids = {}
        
        # 各クラスタの重心を計算
        for label in unique_labels:
            if int(label) >= 0:  # ノイズではない
                cluster_vectors = vectors[cluster_labels == label]
                centroid = np.mean(cluster_vectors, axis=0)
                cluster_centroids[label] = centroid
        
        # 各ベクトルの重心からの距離
        for i, label in enumerate(cluster_labels):
            label = int(label)  # numpyスカラーをintに変換
            if label >= 0 and label in cluster_centroids:
                distance = np.linalg.norm(vectors[i] - cluster_centroids[label])
                distances_to_centroids.append(distance)
            else:
                distances_to_centroids.append(float('inf'))  # ノイズ
        
        # パフォーマンスメトリクス
        performance_metrics = {
            'silhouette_score': silhouette_avg,
            'n_clusters': n_clusters,
            'n_noise': np.sum(cluster_labels == -1),
            'cluster_persistence': clusterer.cluster_persistence_.tolist() if hasattr(clusterer, 'cluster_persistence_') else None
        }
        
        # クラスタ割り当て情報
        assignments = []
        for i, (label, distance) in enumerate(zip(cluster_labels, distances_to_centroids)):
            assignments.append({
                'vector_index': i,
                'cluster_label': int(label),
                'distance_to_centroid': float(distance)
            })
        
        return {
            'cluster_count': n_clusters,
            'labels': cluster_labels.tolist(),
            'centroids': [centroid.tolist() for centroid in cluster_centroids.values()],
            'silhouette_score': silhouette_avg,
            'parameters': default_params,
            'assignments': assignments,
            'performance_metrics': performance_metrics
        }
    
    async def _save_clustering_result(
        self,
        algorithm: str,
        cluster_count: int,
        parameters: Dict[str, Any],
        silhouette_score: float,
        labels: List[int],
        vector_ids: List[str],
        centroids: Optional[List[List[float]]] = None
    ) -> uuid.UUID:
        """クラスタリング結果をデータベースに保存"""
        
        try:
            logger.info(f"💾 Saving clustering result - algorithm: {algorithm}, clusters: {cluster_count}")
            logger.info(f"📊 Labels type: {type(labels)}, length: {len(labels) if hasattr(labels, '__len__') else 'no length'}")
            logger.info(f"📋 Labels preview: {labels[:5] if len(labels) >= 5 else labels}")
            logger.info(f"🎯 Centroids type: {type(centroids)}, shape: {centroids.shape if hasattr(centroids, 'shape') else 'no shape'}")
            # ClusterResultを保存
            cluster_result = ClusterResult(
                algorithm=algorithm,
                cluster_count=cluster_count,
                parameters=parameters,
                silhouette_score=silhouette_score
            )
            self.db.add(cluster_result)
            self.db.flush()  # IDを取得するため
            
            # ClusterAssignmentを一括保存
            logger.info(f"🔄 Processing {len(labels)} cluster assignments")
            assignments = []
            for i, (vector_id, label) in enumerate(zip(vector_ids, labels)):
                logger.debug(f"Processing assignment {i}: vector_id={vector_id}, label={label} (type: {type(label)})")
                # numpyスカラーをPythonのintに変換
                label = int(label)
                
                # 重心からの距離を計算（centroids が利用可能な場合）
                distance_to_centroid = None
                logger.debug(f"Checking centroids: centroids={centroids is not None}, label={label}, label >= 0: {label >= 0}")
                if centroids is not None and label >= 0 and label < len(centroids):
                    vector_embedding = self.db.query(SuccessConversationVector.embedding).filter(
                        SuccessConversationVector.id == vector_id
                    ).scalar()
                    
                    if vector_embedding is not None:
                        centroid = np.array(centroids[label])
                        vector_np = np.array(vector_embedding)
                        distance_to_centroid = float(np.linalg.norm(vector_np - centroid))
                
                assignment = ClusterAssignment(
                    vector_id=vector_id,
                    cluster_result_id=cluster_result.id,
                    cluster_label=label,
                    distance_to_centroid=distance_to_centroid
                )
                assignments.append(assignment)
            
            self.db.add_all(assignments)
            self.db.commit()
            
            logger.info(f"クラスタリング結果保存完了: {cluster_result.id}")
            return cluster_result.id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"クラスタリング結果保存エラー: {e}")
            raise


class OptimalClustersDetector:
    """最適クラスタ数決定ユーティリティ"""
    
    @staticmethod
    def elbow_method(vectors: np.ndarray, k_range: Tuple[int, int]) -> Dict[str, Any]:
        """エルボー法による最適クラスタ数決定"""
        inertias = []
        k_values = list(range(k_range[0], min(k_range[1] + 1, len(vectors))))
        
        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(vectors)
            inertias.append(kmeans.inertia_)
        
        # エルボーポイントを自動検出
        if len(inertias) >= 3:
            # 二次微分を計算してエルボーポイントを検出
            second_derivatives = []
            for i in range(1, len(inertias) - 1):
                second_deriv = inertias[i-1] - 2*inertias[i] + inertias[i+1]
                second_derivatives.append(second_deriv)
            
            # 最大の二次微分を持つ点をエルボーとする
            if second_derivatives:
                elbow_index = second_derivatives.index(max(second_derivatives)) + 1
                optimal_k = k_values[elbow_index]
            else:
                optimal_k = k_values[len(k_values)//2]  # デフォルト
        else:
            optimal_k = k_values[0]
        
        return {
            'optimal_k': optimal_k,
            'k_values': k_values,
            'inertias': inertias,
            'second_derivatives': second_derivatives if len(inertias) >= 3 else []
        }
    
    @staticmethod
    def gap_statistic(vectors: np.ndarray, k_range: Tuple[int, int], n_refs: int = 10) -> Dict[str, Any]:
        """Gap統計による最適クラスタ数決定"""
        from sklearn.cluster import KMeans
        import random
        
        gaps = []
        k_values = list(range(k_range[0], min(k_range[1] + 1, len(vectors))))
        
        for k in k_values:
            # 実データのクラスタリング
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(vectors)
            real_inertia = kmeans.inertia_
            
            # 参照データ（ランダム）のクラスタリング
            ref_inertias = []
            for _ in range(n_refs):
                # 実データの範囲内でランダムデータを生成
                min_vals = vectors.min(axis=0)
                max_vals = vectors.max(axis=0)
                random_data = np.random.uniform(min_vals, max_vals, vectors.shape)
                
                ref_kmeans = KMeans(n_clusters=k, random_state=random.randint(0, 1000))
                ref_kmeans.fit(random_data)
                ref_inertias.append(ref_kmeans.inertia_)
            
            # Gap値計算
            mean_ref_inertia = np.mean(ref_inertias)
            gap = np.log(mean_ref_inertia) - np.log(real_inertia)
            gaps.append(gap)
        
        # 最適クラスタ数は最大のGap値を持つk
        optimal_k = k_values[gaps.index(max(gaps))]
        
        return {
            'optimal_k': optimal_k,
            'k_values': k_values,
            'gaps': gaps
        }


# ユーティリティ関数
def create_clustering_service(vector_db: Session) -> ClusteringService:
    """ClusteringServiceのファクトリー関数"""
    return ClusteringService(vector_db)