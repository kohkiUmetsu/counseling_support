"""
クラスタ代表例抽出サービス
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid
from collections import Counter

from app.models.vector import (
    SuccessConversationVector,
    ClusterResult,
    ClusterAssignment,
    ClusterRepresentative,
    AnomalyDetectionResult
)
from app.models.session import CounselingSession
from app.services.embedding_service import embedding_service


logger = logging.getLogger(__name__)


class RepresentativeExtractionService:
    """クラスタ代表例抽出サービス"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def extract_cluster_representatives(
        self,
        cluster_result_id: str,
        max_representatives_per_cluster: int = 3,
        min_quality_score: float = 0.5
    ) -> Dict[str, Any]:
        """
        各クラスタから代表例を抽出
        
        Args:
            cluster_result_id: クラスタリング結果ID
            max_representatives_per_cluster: クラスタあたりの最大代表例数
            min_quality_score: 最小品質スコア閾値
            
        Returns:
            {
                'cluster_result_id': 'uuid',
                'representatives': [
                    {
                        'cluster_label': 0,
                        'representatives': [
                            {
                                'vector_id': 'uuid',
                                'quality_score': 0.85,
                                'distance_to_centroid': 0.12,
                                'is_primary': True,
                                'text': 'representative text',
                                'session_info': {...}
                            },
                            ...
                        ]
                    },
                    ...
                ],
                'summary': {
                    'total_clusters': 5,
                    'total_representatives': 12,
                    'avg_quality_score': 0.73
                }
            }
        """
        try:
            # 1. クラスタリング結果を取得
            cluster_result = self.db.query(ClusterResult).filter(
                ClusterResult.id == cluster_result_id
            ).first()
            
            if not cluster_result:
                raise ValueError(f"クラスタリング結果が見つかりません: {cluster_result_id}")
            
            # 2. 各クラスタの代表例を抽出
            cluster_representatives = []
            total_quality_scores = []
            
            # クラスタごとに処理
            unique_labels = self.db.query(ClusterAssignment.cluster_label).filter(
                ClusterAssignment.cluster_result_id == cluster_result_id,
                ClusterAssignment.cluster_label >= 0  # ノイズ(-1)を除外
            ).distinct().all()
            
            for (cluster_label,) in unique_labels:
                representatives = await self._extract_representatives_for_cluster(
                    cluster_result_id=cluster_result_id,
                    cluster_label=cluster_label,
                    max_representatives=max_representatives_per_cluster,
                    min_quality_score=min_quality_score
                )
                
                if representatives:
                    cluster_representatives.append({
                        'cluster_label': cluster_label,
                        'representatives': representatives
                    })
                    
                    # 品質スコアを収集
                    for rep in representatives:
                        total_quality_scores.append(rep['quality_score'])
            
            # 3. 結果をデータベースに保存
            await self._save_representatives_to_db(cluster_result_id, cluster_representatives)
            
            # 4. サマリー情報作成
            summary = {
                'total_clusters': len(cluster_representatives),
                'total_representatives': sum(len(cluster['representatives']) for cluster in cluster_representatives),
                'avg_quality_score': np.mean(total_quality_scores) if total_quality_scores else 0.0
            }
            
            logger.info(f"代表例抽出完了: {summary}")
            
            return {
                'cluster_result_id': cluster_result_id,
                'representatives': cluster_representatives,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"代表例抽出エラー: {e}")
            raise
    
    async def _extract_representatives_for_cluster(
        self,
        cluster_result_id: str,
        cluster_label: int,
        max_representatives: int,
        min_quality_score: float
    ) -> List[Dict[str, Any]]:
        """特定クラスタの代表例を抽出"""
        
        # クラスタ内のベクトルを取得
        cluster_vectors = self.db.query(
            ClusterAssignment,
            SuccessConversationVector,
            CounselingSession
        ).join(
            SuccessConversationVector, ClusterAssignment.vector_id == SuccessConversationVector.id
        ).join(
            CounselingSession, SuccessConversationVector.session_id == CounselingSession.id
        ).filter(
            ClusterAssignment.cluster_result_id == cluster_result_id,
            ClusterAssignment.cluster_label == cluster_label
        ).all()
        
        if not cluster_vectors:
            return []
        
        # 品質スコアを計算
        candidates = []
        for assignment, vector, session in cluster_vectors:
            quality_score = await self._calculate_quality_score(
                vector=vector,
                session=session,
                distance_to_centroid=assignment.distance_to_centroid
            )
            
            if quality_score >= min_quality_score:
                candidates.append({
                    'vector_id': str(vector.id),
                    'quality_score': quality_score,
                    'distance_to_centroid': assignment.distance_to_centroid or 0.0,
                    'text': vector.chunk_text,
                    'session_info': {
                        'session_id': str(session.id),
                        'counselor_name': session.counselor_name,
                        'created_at': session.created_at,
                        'is_success': session.is_success
                    },
                    'vector': vector,
                    'session': session
                })
        
        # 品質スコア順にソートして上位を選択
        candidates.sort(key=lambda x: x['quality_score'], reverse=True)
        selected_representatives = candidates[:max_representatives]
        
        # 最高品質の代表例をプライマリに設定
        if selected_representatives:
            selected_representatives[0]['is_primary'] = True
            for rep in selected_representatives[1:]:
                rep['is_primary'] = False
        
        # 不要なオブジェクトを削除（シリアライゼーション用）
        for rep in selected_representatives:
            del rep['vector']
            del rep['session']
        
        return selected_representatives
    
    async def _calculate_quality_score(
        self,
        vector: SuccessConversationVector,
        session: CounselingSession,
        distance_to_centroid: Optional[float]
    ) -> float:
        """代表例の品質スコアを算出"""
        
        score_components = {}
        
        # 1. クラスタ代表性スコア（重心距離）
        if distance_to_centroid is not None:
            # 距離が小さいほど高スコア（正規化）
            centroid_score = max(0, 1 - (distance_to_centroid / 2.0))  # 0-1に正規化
            score_components['centroid_proximity'] = centroid_score
        else:
            score_components['centroid_proximity'] = 0.5  # デフォルト
        
        # 2. 成約率スコア（セッションが成功の場合は満点）
        success_score = 1.0 if session.is_success else 0.0
        score_components['success_rate'] = success_score
        
        # 3. テキスト長さスコア（適切な長さ）
        text_length = len(vector.chunk_text)
        length_score = self._calculate_length_score(text_length)
        score_components['text_length'] = length_score
        
        # 4. 新規性スコア（他の代表例との差分）
        novelty_score = await self._calculate_novelty_score(vector)
        score_components['novelty'] = novelty_score
        
        # 5. コンテンツ品質スコア（キーワード密度など）
        content_score = self._calculate_content_quality_score(vector.chunk_text)
        score_components['content_quality'] = content_score
        
        # 重み付き合計
        weights = {
            'centroid_proximity': 0.25,
            'success_rate': 0.30,
            'text_length': 0.15,
            'novelty': 0.15,
            'content_quality': 0.15
        }
        
        total_score = sum(
            score_components[component] * weights[component]
            for component in weights
        )
        
        return min(1.0, max(0.0, total_score))  # 0-1の範囲に制限
    
    def _calculate_length_score(self, text_length: int) -> float:
        """テキスト長さスコア計算"""
        # 理想的な長さを設定（100-500文字）
        ideal_min = 100
        ideal_max = 500
        
        if ideal_min <= text_length <= ideal_max:
            return 1.0
        elif text_length < ideal_min:
            return max(0.3, text_length / ideal_min)
        else:  # text_length > ideal_max
            excess_penalty = min(0.7, (text_length - ideal_max) / ideal_max)
            return max(0.3, 1.0 - excess_penalty)
    
    async def _calculate_novelty_score(self, target_vector: SuccessConversationVector) -> float:
        """新規性スコア計算（既存代表例との類似度から算出）"""
        
        # 既存の代表例を取得
        existing_representatives = self.db.query(
            ClusterRepresentative, SuccessConversationVector
        ).join(
            SuccessConversationVector, ClusterRepresentative.vector_id == SuccessConversationVector.id
        ).filter(
            ClusterRepresentative.is_primary == True
        ).all()
        
        if not existing_representatives:
            return 1.0  # 既存代表例がない場合は最高スコア
        
        # 各既存代表例との類似度を計算
        similarities = []
        target_embedding = np.array(target_vector.embedding)
        
        for rep, vector in existing_representatives:
            if vector.id != target_vector.id:  # 自分自身を除外
                existing_embedding = np.array(vector.embedding)
                
                # コサイン類似度計算
                similarity = np.dot(target_embedding, existing_embedding) / (
                    np.linalg.norm(target_embedding) * np.linalg.norm(existing_embedding)
                )
                similarities.append(similarity)
        
        if not similarities:
            return 1.0
        
        # 最大類似度から新規性を算出（類似度が低いほど新規性が高い）
        max_similarity = max(similarities)
        novelty_score = 1.0 - max_similarity
        
        return max(0.0, novelty_score)
    
    def _calculate_content_quality_score(self, text: str) -> float:
        """コンテンツ品質スコア計算"""
        
        # 美容脱毛業界の重要キーワード
        important_keywords = [
            '効果', '料金', '安心', '体験', '相談', '無料', 'カウンセリング',
            '脱毛', '痛み', '期間', '回数', '保証', '技術', '安全'
        ]
        
        # ポジティブキーワード
        positive_keywords = [
            '満足', '安心', '効果的', '快適', '信頼', '安全', '丁寧',
            '親切', '分かりやすい', 'おすすめ'
        ]
        
        # ネガティブキーワード（減点要素）
        negative_keywords = [
            '痛い', '高い', '不安', '心配', '迷う', '悩む'
        ]
        
        text_lower = text.lower()
        
        # キーワード密度計算
        important_count = sum(keyword in text for keyword in important_keywords)
        positive_count = sum(keyword in text for keyword in positive_keywords)
        negative_count = sum(keyword in text for keyword in negative_keywords)
        
        # 文字数で正規化
        text_length = len(text)
        important_density = important_count / max(1, text_length / 100)
        positive_density = positive_count / max(1, text_length / 100)
        negative_density = negative_count / max(1, text_length / 100)
        
        # スコア計算
        content_score = (
            important_density * 0.5 +
            positive_density * 0.4 -
            negative_density * 0.1
        )
        
        return min(1.0, max(0.0, content_score))
    
    async def _save_representatives_to_db(
        self,
        cluster_result_id: str,
        cluster_representatives: List[Dict[str, Any]]
    ):
        """代表例をデータベースに保存"""
        
        try:
            # 既存の代表例を削除
            self.db.query(ClusterRepresentative).filter(
                ClusterRepresentative.cluster_result_id == cluster_result_id
            ).delete()
            
            # 新しい代表例を保存
            representatives_to_save = []
            
            for cluster_data in cluster_representatives:
                cluster_label = cluster_data['cluster_label']
                
                for rep_data in cluster_data['representatives']:
                    representative = ClusterRepresentative(
                        cluster_result_id=cluster_result_id,
                        vector_id=rep_data['vector_id'],
                        cluster_label=cluster_label,
                        quality_score=rep_data['quality_score'],
                        distance_to_centroid=rep_data['distance_to_centroid'],
                        is_primary=rep_data['is_primary']
                    )
                    representatives_to_save.append(representative)
            
            self.db.add_all(representatives_to_save)
            self.db.commit()
            
            logger.info(f"代表例をデータベースに保存: {len(representatives_to_save)}件")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"代表例保存エラー: {e}")
            raise
    
    async def get_representatives_for_script_generation(
        self,
        cluster_result_id: str,
        max_total_representatives: int = 8
    ) -> List[Dict[str, Any]]:
        """
        スクリプト生成用の最適化された代表例セットを取得
        
        Args:
            cluster_result_id: クラスタリング結果ID
            max_total_representatives: 最大代表例数
            
        Returns:
            網羅性と品質を両立した代表例リスト
        """
        
        # 各クラスタの主要代表例を取得
        primary_representatives = self.db.query(
            ClusterRepresentative,
            SuccessConversationVector,
            CounselingSession
        ).join(
            SuccessConversationVector, ClusterRepresentative.vector_id == SuccessConversationVector.id
        ).join(
            CounselingSession, SuccessConversationVector.session_id == CounselingSession.id
        ).filter(
            ClusterRepresentative.cluster_result_id == cluster_result_id,
            ClusterRepresentative.is_primary == True
        ).order_by(
            ClusterRepresentative.quality_score.desc()
        ).all()
        
        # 網羅性を確保：各クラスタから最低1つずつ選出
        selected_representatives = []
        covered_clusters = set()
        
        # まず主要代表例から各クラスタ1つずつ
        for rep, vector, session in primary_representatives:
            if rep.cluster_label not in covered_clusters:
                selected_representatives.append({
                    'cluster_label': rep.cluster_label,
                    'vector_id': str(vector.id),
                    'text': vector.chunk_text,
                    'quality_score': rep.quality_score,
                    'session_info': {
                        'counselor_name': session.counselor_name,
                        'created_at': session.created_at
                    },
                    'cluster_characteristics': await self._analyze_cluster_characteristics(
                        cluster_result_id, rep.cluster_label
                    )
                })
                covered_clusters.add(rep.cluster_label)
        
        # 残り枠で高品質な追加代表例を選出
        remaining_slots = max_total_representatives - len(selected_representatives)
        if remaining_slots > 0:
            additional_reps = self.db.query(
                ClusterRepresentative,
                SuccessConversationVector,
                CounselingSession
            ).join(
                SuccessConversationVector, ClusterRepresentative.vector_id == SuccessConversationVector.id
            ).join(
                CounselingSession, SuccessConversationVector.session_id == CounselingSession.id
            ).filter(
                ClusterRepresentative.cluster_result_id == cluster_result_id,
                ClusterRepresentative.is_primary == False
            ).order_by(
                ClusterRepresentative.quality_score.desc()
            ).limit(remaining_slots).all()
            
            for rep, vector, session in additional_reps:
                selected_representatives.append({
                    'cluster_label': rep.cluster_label,
                    'vector_id': str(vector.id),
                    'text': vector.chunk_text,
                    'quality_score': rep.quality_score,
                    'session_info': {
                        'counselor_name': session.counselor_name,
                        'created_at': session.created_at
                    },
                    'cluster_characteristics': await self._analyze_cluster_characteristics(
                        cluster_result_id, rep.cluster_label
                    )
                })
        
        return selected_representatives
    
    async def _analyze_cluster_characteristics(
        self,
        cluster_result_id: str,
        cluster_label: int
    ) -> Dict[str, Any]:
        """クラスタの特徴分析"""
        
        # クラスタ内の全ベクトルを取得
        cluster_vectors = self.db.query(
            SuccessConversationVector
        ).join(
            ClusterAssignment, ClusterAssignment.vector_id == SuccessConversationVector.id
        ).filter(
            ClusterAssignment.cluster_result_id == cluster_result_id,
            ClusterAssignment.cluster_label == cluster_label
        ).all()
        
        if not cluster_vectors:
            return {}
        
        # テキスト分析
        all_texts = [vector.chunk_text for vector in cluster_vectors]
        combined_text = ' '.join(all_texts)
        
        # キーワード抽出
        keywords = self._extract_cluster_keywords(combined_text)
        
        # 統計情報
        text_lengths = [len(text) for text in all_texts]
        
        return {
            'cluster_size': len(cluster_vectors),
            'avg_text_length': np.mean(text_lengths),
            'common_keywords': keywords[:10],  # 上位10キーワード
            'characteristics': self._generate_cluster_description(keywords)
        }
    
    def _extract_cluster_keywords(self, text: str) -> List[str]:
        """クラスタのキーワード抽出（簡易版）"""
        import re
        from collections import Counter
        
        # 日本語の名詞・形容詞を抽出
        keywords = re.findall(r'[ぁ-んァ-ヶー一-龠]{2,}', text)
        
        # ストップワード除去
        stop_words = {
            'です', 'ます', 'ある', 'いる', 'する', 'なる', 'れる', 'られる',
            'こと', 'もの', 'ため', 'よう', 'から', 'まで', 'など'
        }
        
        filtered_keywords = [word for word in keywords if word not in stop_words]
        
        # 頻度順でソート
        keyword_counts = Counter(filtered_keywords)
        return [word for word, count in keyword_counts.most_common()]
    
    def _generate_cluster_description(self, keywords: List[str]) -> str:
        """クラスタの特徴説明生成"""
        if not keywords:
            return "特徴的なキーワードが見つかりませんでした"
        
        top_keywords = keywords[:5]
        
        # キーワードベースで簡易的な特徴説明を生成
        keyword_str = '、'.join(top_keywords)
        return f"主要キーワード: {keyword_str}"


# ユーティリティ関数
def create_representative_extraction_service(db: Session) -> RepresentativeExtractionService:
    """RepresentativeExtractionServiceのファクトリー関数"""
    return RepresentativeExtractionService(db)