"""
pgvector を使用したベクトル類似検索サービス
"""
import logging
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import text, and_, or_
from sqlalchemy.orm import Session
import numpy as np

from app.models.vector import SuccessConversationVector, ClusterAssignment
from app.models.session import CounselingSession
from app.services.embedding_service import embedding_service


logger = logging.getLogger(__name__)


class VectorSearchService:
    """pgvectorを使用したベクトル類似検索サービス"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def search_similar_success_conversations(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        similarity_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        類似する成功会話を検索
        
        Args:
            query_embedding: 検索クエリのベクトル
            top_k: 取得する結果数
            similarity_threshold: 類似度の閾値（0-1）
            filters: フィルタ条件
                - success_rate_min: 最小成約率
                - date_range: [start_date, end_date]
                - counselor_names: カウンセラー名のリスト
                
        Returns:
            [
                {
                    'session_id': 'uuid',
                    'chunk_text': 'テキスト',
                    'similarity_score': 0.85,
                    'metadata': {...},
                    'session_info': {
                        'counselor_name': 'name',
                        'created_at': datetime,
                        'success_rate': 0.8
                    }
                },
                ...
            ]
        """
        try:
            # ベクトル検索クエリを構築
            query_vector = f"[{','.join(map(str, query_embedding))}]"
            
            # 基本のSQLクエリ
            base_query = """
            SELECT 
                scv.session_id,
                scv.chunk_text,
                scv.metadata,
                (1 - (scv.embedding <=> %s::vector)) as similarity_score,
                cs.counselor_name,
                cs.created_at,
                cs.is_success
            FROM success_conversation_vectors scv
            JOIN counseling_sessions cs ON scv.session_id = cs.id
            WHERE cs.is_success = true
            """
            
            params = [query_vector]
            
            # フィルタ条件を追加
            if filters:
                if filters.get('date_range'):
                    start_date, end_date = filters['date_range']
                    base_query += " AND cs.created_at BETWEEN %s AND %s"
                    params.extend([start_date, end_date])
                
                if filters.get('counselor_names'):
                    counselor_list = filters['counselor_names']
                    placeholders = ', '.join(['%s'] * len(counselor_list))
                    base_query += f" AND cs.counselor_name IN ({placeholders})"
                    params.extend(counselor_list)
            
            # 類似度フィルタと並び替え
            base_query += f"""
            AND (1 - (scv.embedding <=> %s::vector)) >= %s
            ORDER BY scv.embedding <=> %s::vector
            LIMIT %s
            """
            params.extend([query_vector, similarity_threshold, query_vector, top_k])
            
            # クエリ実行
            result = self.db.execute(text(base_query), params)
            rows = result.fetchall()
            
            # 結果の整形
            search_results = []
            for row in rows:
                search_results.append({
                    'session_id': str(row.session_id),
                    'chunk_text': row.chunk_text,
                    'similarity_score': float(row.similarity_score),
                    'metadata': row.metadata or {},
                    'session_info': {
                        'counselor_name': row.counselor_name,
                        'created_at': row.created_at,
                        'is_success': row.is_success
                    }
                })
            
            logger.info(f"類似検索完了: {len(search_results)}件取得")
            return search_results
            
        except Exception as e:
            logger.error(f"ベクトル検索エラー: {e}")
            raise
    
    async def search_similar_for_failure_conversation(
        self,
        failure_conversation_text: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        include_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        失敗会話から類似する成功会話を検索し、改善ヒントを生成
        
        Args:
            failure_conversation_text: 失敗会話のテキスト
            top_k: 取得する類似成功例の数
            similarity_threshold: 類似度閾値
            include_analysis: 詳細分析を含めるかどうか
            
        Returns:
            {
                'failure_analysis': {
                    'text': 'failure text',
                    'embedding_vector': [0.1, 0.2, ...],
                    'token_count': 256
                },
                'similar_successes': [
                    {
                        'session_id': 'uuid',
                        'chunk_text': 'success text',
                        'similarity_score': 0.85,
                        'improvement_hints': ['hint1', 'hint2'],
                        'key_differences': ['diff1', 'diff2']
                    },
                    ...
                ],
                'analysis_summary': {
                    'total_found': 5,
                    'avg_similarity': 0.78,
                    'top_improvement_areas': ['area1', 'area2']
                }
            }
        """
        try:
            # 1. 失敗会話をベクトル化
            failure_embedding = await embedding_service.embed_conversation_for_search(
                failure_conversation_text, "failure"
            )
            
            # 2. 類似成功会話を検索
            similar_successes = await self.search_similar_success_conversations(
                query_embedding=failure_embedding,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # 3. 詳細分析（オプション）
            analysis_summary = None
            if include_analysis and similar_successes:
                analysis_summary = self._analyze_failure_to_success_patterns(
                    failure_conversation_text,
                    similar_successes
                )
                
                # 各成功例に改善ヒントを追加
                for success in similar_successes:
                    success['improvement_hints'] = self._generate_improvement_hints(
                        failure_conversation_text,
                        success['chunk_text']
                    )
                    success['key_differences'] = self._identify_key_differences(
                        failure_conversation_text,
                        success['chunk_text']
                    )
            
            return {
                'failure_analysis': {
                    'text': failure_conversation_text,
                    'embedding_vector': failure_embedding,
                    'token_count': embedding_service.count_tokens(failure_conversation_text)
                },
                'similar_successes': similar_successes,
                'analysis_summary': analysis_summary
            }
            
        except Exception as e:
            logger.error(f"失敗→成功マッピング検索エラー: {e}")
            raise
    
    def _analyze_failure_to_success_patterns(
        self,
        failure_text: str,
        success_examples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """失敗→成功パターンの分析"""
        if not success_examples:
            return {
                'total_found': 0,
                'avg_similarity': 0.0,
                'top_improvement_areas': []
            }
        
        # 平均類似度計算
        similarities = [ex['similarity_score'] for ex in success_examples]
        avg_similarity = sum(similarities) / len(similarities)
        
        # 改善領域の特定（簡易版）
        improvement_areas = []
        for success in success_examples:
            # 成功例から改善領域を抽出（キーワードベース）
            success_keywords = self._extract_keywords(success['chunk_text'])
            failure_keywords = self._extract_keywords(failure_text)
            
            missing_keywords = set(success_keywords) - set(failure_keywords)
            improvement_areas.extend(list(missing_keywords))
        
        # 頻出する改善領域をトップとして選出
        from collections import Counter
        improvement_counter = Counter(improvement_areas)
        top_improvement_areas = [area for area, count in improvement_counter.most_common(5)]
        
        return {
            'total_found': len(success_examples),
            'avg_similarity': round(avg_similarity, 3),
            'top_improvement_areas': top_improvement_areas,
            'similarity_distribution': {
                'min': min(similarities),
                'max': max(similarities),
                'median': sorted(similarities)[len(similarities)//2]
            }
        }
    
    def _generate_improvement_hints(self, failure_text: str, success_text: str) -> List[str]:
        """改善ヒントの生成（簡易版）"""
        hints = []
        
        # キーワードベースの簡易分析
        success_keywords = set(self._extract_keywords(success_text))
        failure_keywords = set(self._extract_keywords(failure_text))
        
        missing_important_words = success_keywords - failure_keywords
        
        # 美容脱毛業界特有のキーワードをチェック
        important_keywords = {
            '効果': 'より具体的な効果の説明を含める',
            '料金': '料金体系の明確な説明を追加',
            '安心': '顧客の不安を軽減する表現を使用',
            '体験': '体験談や事例を活用',
            '相談': '相談しやすい雰囲気作りを重視'
        }
        
        for keyword in missing_important_words:
            if keyword in important_keywords:
                hints.append(important_keywords[keyword])
        
        # デフォルトヒント
        if not hints:
            hints.append('成功例のトーンや構成を参考にしてみてください')
        
        return hints[:3]  # 最大3つのヒント
    
    def _identify_key_differences(self, failure_text: str, success_text: str) -> List[str]:
        """主要な差分の特定（簡易版）"""
        differences = []
        
        # 長さの差
        failure_length = len(failure_text)
        success_length = len(success_text)
        
        if success_length > failure_length * 1.5:
            differences.append('成功例はより詳細な説明を含んでいます')
        elif success_length < failure_length * 0.7:
            differences.append('成功例はより簡潔で要点を絞った構成です')
        
        # トーンの違い（簡易分析）
        positive_words = ['安心', '効果', '満足', '信頼', '安全']
        success_positive_count = sum(word in success_text for word in positive_words)
        failure_positive_count = sum(word in failure_text for word in positive_words)
        
        if success_positive_count > failure_positive_count:
            differences.append('成功例はよりポジティブな表現を使用しています')
        
        return differences
    
    def _extract_keywords(self, text: str) -> List[str]:
        """簡易キーワード抽出"""
        import re
        
        # 日本語の名詞・形容詞を簡易抽出
        # 実際の実装では MeCab などの形態素解析を使用
        keywords = re.findall(r'[ぁ-んァ-ヶー一-龠]{2,}', text)
        
        # ストップワード除去
        stop_words = {'です', 'ます', 'ある', 'いる', 'する', 'なる', 'れる', 'られる'}
        keywords = [word for word in keywords if word not in stop_words]
        
        return list(set(keywords))  # 重複除去


class SimilarityCalculator:
    """類似度計算ユーティリティ"""
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """コサイン類似度計算"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def euclidean_distance(vec1: List[float], vec2: List[float]) -> float:
        """ユークリッド距離計算"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        return np.linalg.norm(vec1_np - vec2_np)


# ユーティリティ関数
def create_vector_search_service(db: Session) -> VectorSearchService:
    """VectorSearchServiceのファクトリー関数"""
    return VectorSearchService(db)