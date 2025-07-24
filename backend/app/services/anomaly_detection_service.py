from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_distances
import logging

logger = logging.getLogger(__name__)

class AnomalyDetectionService:
    """
    成功会話の中から異常なパターン（特殊成功例）を検出するサービス
    Isolation ForestとLocal Outlier Factorを使用して、
    一般的な成功パターンから外れた特殊な成功例を識別する
    """
    
    def __init__(self, contamination_rate: float = 0.1):
        """
        Args:
            contamination_rate: 異常とみなすデータの割合（0.05-0.2程度が推奨）
        """
        self.contamination_rate = contamination_rate
        self.isolation_forest = None
        self.lof_detector = None
        self.scaler = StandardScaler()
        
    def detect_anomalies(
        self, 
        conversation_vectors: np.ndarray,
        conversation_metadata: List[Dict[str, Any]],
        method: str = "isolation_forest"
    ) -> Dict[str, Any]:
        """
        成功会話ベクトルから異常例を検出
        
        Args:
            conversation_vectors: 成功会話のベクトル表現 (n_samples, n_features)
            conversation_metadata: 各会話のメタデータ
            method: 検出手法 ("isolation_forest" or "lof")
            
        Returns:
            異常検出結果と詳細分析
        """
        try:
            logger.info(f"異常検出開始: {len(conversation_vectors)}件の成功会話を分析")
            
            # ベクトルの正規化
            normalized_vectors = self.scaler.fit_transform(conversation_vectors)
            
            if method == "isolation_forest":
                anomaly_results = self._isolation_forest_detection(
                    normalized_vectors, conversation_metadata
                )
            elif method == "lof":
                anomaly_results = self._lof_detection(
                    normalized_vectors, conversation_metadata
                )
            else:
                raise ValueError(f"Unknown method: {method}")
            
            # 異常度の詳細分析
            detailed_analysis = self._analyze_anomaly_patterns(
                anomaly_results, conversation_vectors, conversation_metadata
            )
            
            logger.info(f"異常検出完了: {len(anomaly_results['outlier_indices'])}件の特殊成功例を検出")
            
            return {
                "anomaly_results": anomaly_results,
                "detailed_analysis": detailed_analysis,
                "detection_metadata": {
                    "method": method,
                    "contamination_rate": self.contamination_rate,
                    "total_conversations": len(conversation_vectors),
                    "outliers_detected": len(anomaly_results["outlier_indices"])
                }
            }
            
        except Exception as e:
            logger.error(f"異常検出でエラーが発生: {e}")
            raise
    
    def _isolation_forest_detection(
        self, 
        vectors: np.ndarray, 
        metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Isolation Forestによる異常検出"""
        
        self.isolation_forest = IsolationForest(
            contamination=self.contamination_rate,
            random_state=42,
            n_jobs=-1
        )
        
        # 異常予測と異常スコア計算
        anomaly_labels = self.isolation_forest.fit_predict(vectors)
        anomaly_scores = self.isolation_forest.score_samples(vectors)
        
        # 異常例のインデックス抽出
        outlier_indices = np.where(anomaly_labels == -1)[0]
        
        return {
            "outlier_indices": outlier_indices.tolist(),
            "anomaly_scores": anomaly_scores.tolist(),
            "anomaly_labels": anomaly_labels.tolist(),
            "outlier_conversations": [metadata[i] for i in outlier_indices]
        }
    
    def _lof_detection(
        self, 
        vectors: np.ndarray, 
        metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Local Outlier Factorによる異常検出"""
        
        self.lof_detector = LocalOutlierFactor(
            contamination=self.contamination_rate,
            n_neighbors=min(20, len(vectors) // 5),
            n_jobs=-1
        )
        
        # 異常予測
        anomaly_labels = self.lof_detector.fit_predict(vectors)
        
        # LOFスコア取得（負の値：outlier factor）
        lof_scores = -self.lof_detector.negative_outlier_factor_
        
        # 異常例のインデックス抽出
        outlier_indices = np.where(anomaly_labels == -1)[0]
        
        return {
            "outlier_indices": outlier_indices.tolist(),
            "lof_scores": lof_scores.tolist(),
            "anomaly_labels": anomaly_labels.tolist(),
            "outlier_conversations": [metadata[i] for i in outlier_indices]
        }
    
    def _analyze_anomaly_patterns(
        self,
        anomaly_results: Dict[str, Any],
        original_vectors: np.ndarray,
        metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """異常例の詳細パターン分析"""
        
        outlier_indices = anomaly_results["outlier_indices"]
        outlier_conversations = anomaly_results["outlier_conversations"]
        
        if not outlier_indices:
            return {"message": "異常例が検出されませんでした"}
        
        # 正常例と異常例の特徴比較
        normal_indices = [i for i in range(len(metadata)) if i not in outlier_indices]
        normal_metadata = [metadata[i] for i in normal_indices]
        
        # 成約率の比較
        normal_success_rates = [conv.get('success_rate', 0) for conv in normal_metadata if conv.get('success_rate') is not None]
        outlier_success_rates = [conv.get('success_rate', 0) for conv in outlier_conversations if conv.get('success_rate') is not None]
        
        # 会話長の比較
        normal_lengths = [len(conv.get('text', '')) for conv in normal_metadata]
        outlier_lengths = [len(conv.get('text', '')) for conv in outlier_conversations]
        
        # ベクトル空間での距離分析
        centroid = np.mean(original_vectors[normal_indices], axis=0)
        outlier_distances = cosine_distances([centroid], original_vectors[outlier_indices])[0]
        
        # 特殊性の特徴分析
        special_characteristics = self._identify_special_characteristics(outlier_conversations)
        
        return {
            "outlier_count": len(outlier_indices),
            "success_rate_comparison": {
                "normal_avg": np.mean(normal_success_rates) if normal_success_rates else 0,
                "outlier_avg": np.mean(outlier_success_rates) if outlier_success_rates else 0,
                "normal_std": np.std(normal_success_rates) if normal_success_rates else 0,
                "outlier_std": np.std(outlier_success_rates) if outlier_success_rates else 0
            },
            "length_comparison": {
                "normal_avg": np.mean(normal_lengths) if normal_lengths else 0,
                "outlier_avg": np.mean(outlier_lengths) if outlier_lengths else 0,
                "normal_std": np.std(normal_lengths) if normal_lengths else 0,
                "outlier_std": np.std(outlier_lengths) if outlier_lengths else 0
            },
            "distance_analysis": {
                "avg_distance_to_centroid": np.mean(outlier_distances),
                "max_distance_to_centroid": np.max(outlier_distances),
                "min_distance_to_centroid": np.min(outlier_distances)
            },
            "special_characteristics": special_characteristics,
            "outlier_details": [
                {
                    "index": idx,
                    "conversation_id": outlier_conversations[i].get('session_id'),
                    "success_rate": outlier_conversations[i].get('success_rate'),
                    "distance_to_centroid": float(outlier_distances[i]),
                    "text_preview": outlier_conversations[i].get('text', '')[:200] + "..."
                }
                for i, idx in enumerate(outlier_indices)
            ]
        }
    
    def _identify_special_characteristics(
        self, 
        outlier_conversations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """特殊成功例の特徴を分析"""
        
        characteristics = {
            "high_success_outliers": [],
            "low_success_outliers": [],
            "unusual_length_patterns": [],
            "unique_counselor_styles": []
        }
        
        for conv in outlier_conversations:
            success_rate = conv.get('success_rate', 0)
            text_length = len(conv.get('text', ''))
            counselor_id = conv.get('counselor_id')
            
            # 高成約率の特殊例
            if success_rate > 0.9:
                characteristics["high_success_outliers"].append({
                    "conversation_id": conv.get('session_id'),
                    "success_rate": success_rate,
                    "potential_factor": "exceptional_success_pattern"
                })
            
            # 低成約率だが成功とラベルされた例
            if success_rate < 0.5:
                characteristics["low_success_outliers"].append({
                    "conversation_id": conv.get('session_id'),
                    "success_rate": success_rate,
                    "potential_factor": "unusual_success_despite_low_rate"
                })
            
            # 極端な長さパターン
            if text_length > 5000 or text_length < 200:
                characteristics["unusual_length_patterns"].append({
                    "conversation_id": conv.get('session_id'),
                    "text_length": text_length,
                    "pattern": "very_long" if text_length > 5000 else "very_short"
                })
        
        return characteristics
    
    def get_anomaly_insights(self, anomaly_results: Dict[str, Any]) -> Dict[str, str]:
        """異常検出結果から実用的なインサイトを生成"""
        
        analysis = anomaly_results.get("detailed_analysis", {})
        
        insights = []
        
        # 高成約率の特殊例に関するインサイト
        high_success_outliers = analysis.get("special_characteristics", {}).get("high_success_outliers", [])
        if high_success_outliers:
            insights.append(
                f"{len(high_success_outliers)}件の例外的に高い成約率（90%以上）の成功例を発見。"
                "これらの特殊なアプローチ手法を詳細分析することで、新たな成功パターンを発見できる可能性があります。"
            )
        
        # 距離分析に基づくインサイト
        distance_analysis = analysis.get("distance_analysis", {})
        if distance_analysis.get("avg_distance_to_centroid", 0) > 0.3:
            insights.append(
                "検出された特殊成功例は、一般的な成功パターンから大きく離れています。"
                "これらは独自のアプローチや特殊な状況での成功例である可能性があります。"
            )
        
        # 成約率比較に基づくインサイト
        success_comparison = analysis.get("success_rate_comparison", {})
        outlier_avg = success_comparison.get("outlier_avg", 0)
        normal_avg = success_comparison.get("normal_avg", 0)
        
        if outlier_avg > normal_avg * 1.1:
            insights.append(
                "特殊成功例の平均成約率が通常例より高く、革新的なアプローチの可能性があります。"
            )
        elif outlier_avg < normal_avg * 0.9:
            insights.append(
                "特殊成功例の中には成約率は低いが成功とラベルされた例があり、"
                "成約以外の価値（顧客満足度等）を重視した成功パターンの可能性があります。"
            )
        
        return {
            "insights": insights,
            "recommendations": [
                "特殊成功例を個別に詳細分析し、独自の成功要因を特定する",
                "高成約率の特殊例から新しい成功パターンを抽出する",
                "特殊例のアプローチを一般化できるか検討する",
                "異常例から学んだ要素を標準スクリプトに取り入れる"
            ]
        }