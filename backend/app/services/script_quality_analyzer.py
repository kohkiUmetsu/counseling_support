"""
スクリプト品質分析・検証サービス
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import re
from collections import Counter
import json

from app.services.embedding_service import embedding_service


logger = logging.getLogger(__name__)


class ScriptQualityAnalyzer:
    """スクリプト品質分析メインクラス"""
    
    def __init__(self):
        self.coverage_analyzer = CoverageAnalyzer()
        self.novelty_scorer = NoveltyScorer()
        self.reliability_calculator = ReliabilityCalculator()
        self.content_analyzer = ContentAnalyzer()
    
    async def analyze_script_quality(
        self, 
        generated_script: Dict[str, Any], 
        base_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成されたスクリプトの包括的品質分析
        
        Args:
            generated_script: 生成スクリプトデータ
            base_data: {
                'success_patterns': [...],
                'historical_scripts': [...],
                'success_elements': [...],
                'source_quality': {...}
            }
            
        Returns:
            {
                'coverage': {...},
                'novelty': {...},
                'success_matching': {...},
                'reliability': {...},
                'content_quality': {...},
                'overall_quality': float,
                'detailed_analysis': {...}
            }
        """
        try:
            metrics = {}
            
            # 1. カバレッジ分析
            coverage_analysis = await self.coverage_analyzer.analyze_coverage(
                generated_script, base_data.get('success_patterns', [])
            )
            metrics['coverage'] = coverage_analysis
            
            # 2. 新規性スコア
            novelty_analysis = await self.novelty_scorer.calculate_novelty(
                generated_script, base_data.get('historical_scripts', [])
            )
            metrics['novelty'] = novelty_analysis
            
            # 3. 成功要素マッチング率
            success_matching = await self._analyze_success_element_matching(
                generated_script, base_data.get('success_elements', [])
            )
            metrics['success_matching'] = success_matching
            
            # 4. 推奨信頼度
            reliability = self.reliability_calculator.calculate_reliability(
                base_data.get('source_quality', {})
            )
            metrics['reliability'] = reliability
            
            # 5. コンテンツ品質
            content_quality = self.content_analyzer.analyze_content_quality(
                generated_script
            )
            metrics['content_quality'] = content_quality
            
            # 6. 詳細分析
            detailed_analysis = await self._generate_detailed_analysis(
                generated_script, metrics, base_data
            )
            metrics['detailed_analysis'] = detailed_analysis
            
            # 7. 総合品質スコア
            overall_quality = self._calculate_overall_quality(metrics)
            metrics['overall_quality'] = overall_quality
            
            # メタデータ追加
            metrics['analysis_metadata'] = {
                'analyzed_at': datetime.utcnow().isoformat(),
                'analyzer_version': '1.0.0',
                'analysis_duration': 0.0  # 実際の測定値に置き換え
            }
            
            logger.info(f"スクリプト品質分析完了: 総合スコア{overall_quality:.2f}")
            return metrics
            
        except Exception as e:
            logger.error(f"スクリプト品質分析エラー: {e}")
            raise
    
    async def _analyze_success_element_matching(
        self, 
        script: Dict[str, Any], 
        success_elements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """成功要素マッチング率分析"""
        
        if not success_elements:
            return {
                'matching_rate': 0.0,
                'matched_elements': [],
                'missing_elements': [],
                'element_strength': {}
            }
        
        # スクリプト全体のテキストを結合
        script_text = self._extract_all_text_from_script(script)
        
        matched_elements = []
        missing_elements = []
        element_strength = {}
        
        for element in success_elements:
            element_name = element.get('name', '')
            element_keywords = element.get('keywords', [])
            element_patterns = element.get('patterns', [])
            
            # キーワードマッチング
            keyword_matches = sum(
                1 for keyword in element_keywords 
                if keyword.lower() in script_text.lower()
            )
            keyword_match_rate = keyword_matches / len(element_keywords) if element_keywords else 0
            
            # パターンマッチング
            pattern_matches = sum(
                1 for pattern in element_patterns
                if re.search(pattern, script_text, re.IGNORECASE)
            )
            pattern_match_rate = pattern_matches / len(element_patterns) if element_patterns else 0
            
            # 要素強度計算
            element_strength_score = (keyword_match_rate + pattern_match_rate) / 2
            element_strength[element_name] = element_strength_score
            
            # マッチング判定（閾値0.3以上）
            if element_strength_score >= 0.3:
                matched_elements.append({
                    'name': element_name,
                    'strength': element_strength_score,
                    'keyword_matches': keyword_matches,
                    'pattern_matches': pattern_matches
                })
            else:
                missing_elements.append({
                    'name': element_name,
                    'strength': element_strength_score,
                    'recommendations': element.get('improvement_suggestions', [])
                })
        
        matching_rate = len(matched_elements) / len(success_elements)
        
        return {
            'matching_rate': matching_rate,
            'matched_elements': matched_elements,
            'missing_elements': missing_elements,
            'element_strength': element_strength,
            'total_elements_analyzed': len(success_elements)
        }
    
    def _extract_all_text_from_script(self, script: Dict[str, Any]) -> str:
        """スクリプトからすべてのテキストを抽出"""
        texts = []
        
        # 各セクションからテキストを抽出
        text_fields = [
            'success_factors_analysis',
            'improvement_points',
            'practical_improvements',
            'expected_effects'
        ]
        
        for field in text_fields:
            if field in script and script[field]:
                texts.append(str(script[field]))
        
        # カウンセリングスクリプトの各フェーズ
        counseling_script = script.get('counseling_script', {})
        for phase in ['opening', 'needs_assessment', 'solution_proposal', 'closing']:
            if phase in counseling_script and counseling_script[phase]:
                texts.append(str(counseling_script[phase]))
        
        return ' '.join(texts)
    
    async def _generate_detailed_analysis(
        self,
        script: Dict[str, Any],
        metrics: Dict[str, Any],
        base_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """詳細分析レポート生成"""
        
        # 強みと弱みの特定
        strengths = []
        weaknesses = []
        recommendations = []
        
        # カバレッジ分析から強み・弱みを抽出
        coverage = metrics.get('coverage', {})
        if coverage.get('coverage_percentage', 0) > 75:
            strengths.append("成功パターンの網羅性が高い")
        else:
            weaknesses.append("成功パターンのカバレッジが不足")
            recommendations.append("不足している成功パターンの要素を追加する")
        
        # 新規性分析から評価
        novelty = metrics.get('novelty', {})
        if novelty.get('novelty_score', 0) > 0.6:
            strengths.append("既存スクリプトとの差別化ができている")
        elif novelty.get('novelty_score', 0) < 0.3:
            weaknesses.append("既存スクリプトとの類似性が高すぎる")
            recommendations.append("より独創的なアプローチを検討する")
        
        # 成功要素マッチングから評価
        success_matching = metrics.get('success_matching', {})
        if success_matching.get('matching_rate', 0) > 0.7:
            strengths.append("重要な成功要素が適切に含まれている")
        else:
            weaknesses.append("重要な成功要素の取り込みが不十分")
            missing_elements = success_matching.get('missing_elements', [])
            for element in missing_elements[:3]:  # 上位3つの欠落要素
                recommendations.append(f"{element['name']}要素の強化を検討")
        
        # コンテンツ品質から評価
        content_quality = metrics.get('content_quality', {})
        if content_quality.get('readability_score', 0) > 0.7:
            strengths.append("読みやすく理解しやすい構成")
        
        if content_quality.get('actionability_score', 0) > 0.7:
            strengths.append("実践的で具体的な内容")
        else:
            weaknesses.append("具体性や実践性に改善の余地がある")
            recommendations.append("より具体的な例やテクニックを追加する")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'recommendations': recommendations,
            'key_insights': self._generate_key_insights(metrics),
            'improvement_priority': self._calculate_improvement_priority(metrics),
            'comparable_scripts': self._find_comparable_scripts(script, base_data)
        }
    
    def _generate_key_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """主要洞察の生成"""
        insights = []
        
        overall_quality = metrics.get('overall_quality', 0)
        
        if overall_quality > 0.8:
            insights.append("高品質なスクリプトが生成されており、即座に実用可能です")
        elif overall_quality > 0.6:
            insights.append("良好な品質のスクリプトですが、一部改善の余地があります")
        else:
            insights.append("品質向上のためのさらなる改善が必要です")
        
        # 各メトリクスから洞察を抽出
        coverage = metrics.get('coverage', {})
        if coverage.get('coverage_percentage', 0) > 80:
            insights.append("成功パターンの網羅性に優れており、多様な顧客ニーズに対応可能")
        
        novelty = metrics.get('novelty', {})
        if novelty.get('novelty_score', 0) > 0.7:
            insights.append("創新性が高く、競合他社との差別化が期待できます")
        
        return insights
    
    def _calculate_improvement_priority(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """改善優先度の計算"""
        
        priorities = []
        
        # 各メトリクスの改善インパクトを評価
        coverage_score = metrics.get('coverage', {}).get('coverage_percentage', 0) / 100
        novelty_score = metrics.get('novelty', {}).get('novelty_score', 0)
        matching_score = metrics.get('success_matching', {}).get('matching_rate', 0)
        content_score = metrics.get('content_quality', {}).get('overall_score', 0)
        
        metrics_impact = [
            {
                'area': 'カバレッジ向上',
                'current_score': coverage_score,
                'improvement_potential': 1 - coverage_score,
                'impact_weight': 0.3,
                'priority_score': (1 - coverage_score) * 0.3
            },
            {
                'area': '成功要素強化',
                'current_score': matching_score,
                'improvement_potential': 1 - matching_score,
                'impact_weight': 0.35,
                'priority_score': (1 - matching_score) * 0.35
            },
            {
                'area': 'コンテンツ品質向上',
                'current_score': content_score,
                'improvement_potential': 1 - content_score,
                'impact_weight': 0.25,
                'priority_score': (1 - content_score) * 0.25
            },
            {
                'area': '新規性向上',
                'current_score': novelty_score,
                'improvement_potential': 1 - novelty_score,
                'impact_weight': 0.1,
                'priority_score': (1 - novelty_score) * 0.1
            }
        ]
        
        # 優先度順にソート
        priorities = sorted(metrics_impact, key=lambda x: x['priority_score'], reverse=True)
        
        return priorities
    
    def _find_comparable_scripts(
        self, 
        script: Dict[str, Any], 
        base_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """比較可能なスクリプトを検索"""
        
        # 実装では、過去のスクリプトとの類似度を計算して
        # 比較対象となるスクリプトを特定
        # ここでは簡易版として空リストを返す
        
        return []
    
    def _calculate_overall_quality(self, metrics: Dict[str, Any]) -> float:
        """総合品質スコア計算"""
        
        # 各メトリクスの重み付け
        weights = {
            'coverage': 0.25,
            'success_matching': 0.30,
            'content_quality': 0.25,
            'novelty': 0.15,
            'reliability': 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric_name, weight in weights.items():
            metric_data = metrics.get(metric_name, {})
            
            # メトリクスごとの正規化されたスコアを取得
            if metric_name == 'coverage':
                score = metric_data.get('coverage_percentage', 0) / 100
            elif metric_name == 'success_matching':
                score = metric_data.get('matching_rate', 0)
            elif metric_name == 'content_quality':
                score = metric_data.get('overall_score', 0)
            elif metric_name == 'novelty':
                score = metric_data.get('novelty_score', 0)
            elif metric_name == 'reliability':
                score = metric_data.get('confidence_score', 0)
            else:
                continue
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0


class CoverageAnalyzer:
    """カバレッジ分析専用クラス"""
    
    async def analyze_coverage(
        self, 
        script: Dict[str, Any], 
        success_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """成功パターンカバレッジ分析"""
        
        if not success_patterns:
            return {
                'coverage_percentage': 0.0,
                'covered_patterns': [],
                'missing_patterns': [],
                'coverage_details': {}
            }
        
        script_text = self._extract_script_text(script)
        
        covered_patterns = []
        missing_patterns = []
        coverage_details = {}
        
        for pattern in success_patterns:
            pattern_name = pattern.get('name', pattern.get('cluster_label', 'Unknown'))
            keywords = pattern.get('keywords', [])
            characteristics = pattern.get('characteristics', [])
            
            # パターンカバレッジの判定
            is_covered = await self._is_pattern_covered(script_text, pattern)
            coverage_score = await self._calculate_pattern_coverage_score(script_text, pattern)
            
            coverage_details[pattern_name] = {
                'covered': is_covered,
                'coverage_score': coverage_score,
                'matching_elements': self._find_matching_elements(script_text, keywords)
            }
            
            if is_covered:
                covered_patterns.append({
                    'name': pattern_name,
                    'coverage_score': coverage_score,
                    'key_elements': keywords[:3]  # 上位3要素
                })
            else:
                missing_patterns.append({
                    'name': pattern_name,
                    'missing_elements': [k for k in keywords if k.lower() not in script_text.lower()],
                    'suggestions': pattern.get('improvement_suggestions', [])
                })
        
        coverage_percentage = (len(covered_patterns) / len(success_patterns)) * 100
        
        return {
            'coverage_percentage': coverage_percentage,
            'covered_patterns': covered_patterns,
            'missing_patterns': missing_patterns,
            'coverage_details': coverage_details,
            'total_patterns_analyzed': len(success_patterns)
        }
    
    def _extract_script_text(self, script: Dict[str, Any]) -> str:
        """スクリプトからテキストを抽出"""
        texts = []
        
        # 各セクションからテキストを抽出
        for key, value in script.items():
            if isinstance(value, str):
                texts.append(value)
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        texts.append(sub_value)
        
        return ' '.join(texts)
    
    async def _is_pattern_covered(self, script_text: str, pattern: Dict[str, Any]) -> bool:
        """パターンがカバーされているかを判定"""
        
        keywords = pattern.get('keywords', [])
        if not keywords:
            return False
        
        # キーワードの50%以上が含まれていればカバーされているとみなす
        matching_keywords = sum(
            1 for keyword in keywords 
            if keyword.lower() in script_text.lower()
        )
        
        coverage_threshold = 0.5
        return (matching_keywords / len(keywords)) >= coverage_threshold
    
    async def _calculate_pattern_coverage_score(
        self, 
        script_text: str, 
        pattern: Dict[str, Any]
    ) -> float:
        """パターンカバレッジスコア計算"""
        
        keywords = pattern.get('keywords', [])
        if not keywords:
            return 0.0
        
        matching_keywords = sum(
            1 for keyword in keywords 
            if keyword.lower() in script_text.lower()
        )
        
        return matching_keywords / len(keywords)
    
    def _find_matching_elements(self, script_text: str, keywords: List[str]) -> List[str]:
        """マッチングした要素を特定"""
        return [
            keyword for keyword in keywords 
            if keyword.lower() in script_text.lower()
        ]


class NoveltyScorer:
    """新規性スコア計算クラス"""
    
    async def calculate_novelty(
        self, 
        script: Dict[str, Any], 
        historical_scripts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """新規性スコア計算"""
        
        if not historical_scripts:
            return {
                'novelty_score': 1.0,
                'unique_elements': [],
                'similarity_to_past': 0.0,
                'innovation_areas': []
            }
        
        current_script_text = self._extract_script_text(script)
        
        # 過去スクリプトとの類似度計算
        similarities = []
        for historical_script in historical_scripts:
            historical_text = self._extract_script_text(historical_script)
            similarity = await self._calculate_text_similarity(current_script_text, historical_text)
            similarities.append(similarity)
        
        max_similarity = max(similarities) if similarities else 0.0
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        # 新規性スコア（最大類似度から算出）
        novelty_score = 1.0 - max_similarity
        
        # ユニークな要素の特定
        unique_elements = await self._identify_unique_elements(current_script_text, historical_scripts)
        
        # 革新領域の特定
        innovation_areas = self._identify_innovation_areas(script, historical_scripts)
        
        return {
            'novelty_score': novelty_score,
            'unique_elements': unique_elements,
            'similarity_to_past': avg_similarity,
            'max_similarity': max_similarity,
            'innovation_areas': innovation_areas,
            'comparison_count': len(historical_scripts)
        }
    
    def _extract_script_text(self, script: Dict[str, Any]) -> str:
        """スクリプトテキスト抽出"""
        # CoverageAnalyzerと同じロジック
        texts = []
        for key, value in script.items():
            if isinstance(value, str):
                texts.append(value)
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        texts.append(sub_value)
        return ' '.join(texts)
    
    async def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """テキスト間の類似度計算"""
        
        # 簡易版：共通単語の割合
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        common_words = words1.intersection(words2)
        total_words = words1.union(words2)
        
        return len(common_words) / len(total_words)
    
    async def _identify_unique_elements(
        self, 
        current_text: str, 
        historical_scripts: List[Dict[str, Any]]
    ) -> List[str]:
        """ユニークな要素の特定"""
        
        current_words = set(current_text.lower().split())
        
        # 過去スクリプトの全単語を収集
        historical_words = set()
        for script in historical_scripts:
            historical_text = self._extract_script_text(script)
            historical_words.update(historical_text.lower().split())
        
        # 現在のスクリプト固有の要素
        unique_words = current_words - historical_words
        
        # 意味のある単語のみ抽出（長さ3文字以上）
        meaningful_unique = [word for word in unique_words if len(word) >= 3]
        
        return meaningful_unique[:10]  # 上位10個
    
    def _identify_innovation_areas(
        self, 
        script: Dict[str, Any], 
        historical_scripts: List[Dict[str, Any]]
    ) -> List[str]:
        """革新領域の特定"""
        
        # 簡易版：新しいアプローチや手法を示すキーワード
        innovation_keywords = [
            '新しい', '革新的', '独自', '画期的', '効果的', '改善された',
            'アプローチ', '手法', 'テクニック', '戦略'
        ]
        
        script_text = self._extract_script_text(script)
        found_innovations = [
            keyword for keyword in innovation_keywords 
            if keyword in script_text
        ]
        
        return found_innovations


class ReliabilityCalculator:
    """推奨信頼度計算クラス"""
    
    def calculate_reliability(self, source_quality: Dict[str, Any]) -> Dict[str, Any]:
        """推奨信頼度計算"""
        
        # データ品質スコア
        data_quality_score = self._calculate_data_quality_score(source_quality)
        
        # サンプルサイズ適切性
        sample_adequacy = self._calculate_sample_adequacy(source_quality)
        
        # 統計的信頼性
        statistical_reliability = self._calculate_statistical_reliability(source_quality)
        
        # 総合信頼度
        confidence_score = (
            data_quality_score * 0.4 +
            sample_adequacy * 0.3 +
            statistical_reliability * 0.3
        )
        
        # 推奨強度
        recommendation_strength = self._determine_recommendation_strength(confidence_score)
        
        return {
            'confidence_score': confidence_score,
            'data_quality_score': data_quality_score,
            'sample_size_adequacy': sample_adequacy,
            'statistical_reliability': statistical_reliability,
            'recommendation_strength': recommendation_strength,
            'reliability_factors': self._identify_reliability_factors(source_quality)
        }
    
    def _calculate_data_quality_score(self, source_quality: Dict[str, Any]) -> float:
        """データ品質スコア計算"""
        
        # データの完全性、一貫性、正確性を評価
        completeness = source_quality.get('completeness', 0.8)
        consistency = source_quality.get('consistency', 0.8)
        accuracy = source_quality.get('accuracy', 0.8)
        
        return (completeness + consistency + accuracy) / 3
    
    def _calculate_sample_adequacy(self, source_quality: Dict[str, Any]) -> float:
        """サンプルサイズ適切性計算"""
        
        sample_size = source_quality.get('sample_size', 0)
        
        # サンプルサイズに基づく適切性評価
        if sample_size >= 100:
            return 1.0
        elif sample_size >= 50:
            return 0.8
        elif sample_size >= 20:
            return 0.6
        elif sample_size >= 10:
            return 0.4
        else:
            return 0.2
    
    def _calculate_statistical_reliability(self, source_quality: Dict[str, Any]) -> float:
        """統計的信頼性計算"""
        
        # 成功率の分布、信頼区間などから信頼性を評価
        success_rate_variance = source_quality.get('success_rate_variance', 0.1)
        confidence_interval_width = source_quality.get('confidence_interval_width', 0.2)
        
        # 分散が小さく、信頼区間が狭いほど信頼性が高い
        variance_score = max(0, 1 - success_rate_variance * 2)
        interval_score = max(0, 1 - confidence_interval_width)
        
        return (variance_score + interval_score) / 2
    
    def _determine_recommendation_strength(self, confidence_score: float) -> str:
        """推奨強度の決定"""
        
        if confidence_score >= 0.8:
            return "高信頼度推奨"
        elif confidence_score >= 0.6:
            return "中程度推奨"
        elif confidence_score >= 0.4:
            return "条件付き推奨"
        else:
            return "要注意・要検証"
    
    def _identify_reliability_factors(self, source_quality: Dict[str, Any]) -> List[str]:
        """信頼性要因の特定"""
        
        factors = []
        
        if source_quality.get('sample_size', 0) >= 50:
            factors.append("十分なサンプルサイズ")
        
        if source_quality.get('data_recency', 0) <= 30:  # 30日以内
            factors.append("最新データに基づく分析")
        
        if source_quality.get('success_rate_variance', 1) < 0.1:
            factors.append("安定した成功率パターン")
        
        if source_quality.get('counselor_diversity', 0) >= 3:
            factors.append("複数カウンセラーからのデータ")
        
        return factors


class ContentAnalyzer:
    """コンテンツ品質分析クラス"""
    
    def analyze_content_quality(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """コンテンツ品質の包括的分析"""
        
        script_text = self._extract_all_text(script)
        
        # 読みやすさスコア
        readability_score = self._calculate_readability_score(script_text)
        
        # 実行可能性スコア
        actionability_score = self._calculate_actionability_score(script)
        
        # 構造品質スコア
        structure_score = self._calculate_structure_score(script)
        
        # 専門性スコア
        expertise_score = self._calculate_expertise_score(script_text)
        
        # 総合コンテンツスコア
        overall_score = (
            readability_score * 0.25 +
            actionability_score * 0.30 +
            structure_score * 0.25 +
            expertise_score * 0.20
        )
        
        return {
            'overall_score': overall_score,
            'readability_score': readability_score,
            'actionability_score': actionability_score,
            'structure_score': structure_score,
            'expertise_score': expertise_score,
            'content_metrics': self._calculate_content_metrics(script_text),
            'improvement_suggestions': self._generate_content_improvements(
                readability_score, actionability_score, structure_score, expertise_score
            )
        }
    
    def _extract_all_text(self, script: Dict[str, Any]) -> str:
        """すべてのテキストを抽出"""
        texts = []
        for key, value in script.items():
            if isinstance(value, str):
                texts.append(value)
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, str):
                        texts.append(sub_value)
        return ' '.join(texts)
    
    def _calculate_readability_score(self, text: str) -> float:
        """読みやすさスコア計算"""
        
        if not text:
            return 0.0
        
        # 文の長さ、単語の複雑さなどを評価
        sentences = text.split('。')
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # 適切な文の長さ（10-20語）を基準にスコア化
        if 10 <= avg_sentence_length <= 20:
            length_score = 1.0
        elif avg_sentence_length < 10:
            length_score = avg_sentence_length / 10
        else:
            length_score = max(0.3, 20 / avg_sentence_length)
        
        return length_score
    
    def _calculate_actionability_score(self, script: Dict[str, Any]) -> float:
        """実行可能性スコア計算"""
        
        actionable_indicators = [
            '具体的', '例えば', 'ポイント', 'コツ', '方法', 'テクニック',
            '言い回し', '表現', 'アプローチ', '話し方', '手順', 'ステップ'
        ]
        
        script_text = self._extract_all_text(script)
        
        indicator_count = sum(
            script_text.count(indicator) for indicator in actionable_indicators
        )
        
        # テキスト長に対する指標の密度
        text_length = len(script_text.split())
        if text_length == 0:
            return 0.0
        
        density = indicator_count / text_length * 100
        
        # 密度に基づくスコア（2-5%が理想）
        if 2 <= density <= 5:
            return 1.0
        elif density < 2:
            return density / 2
        else:
            return max(0.5, 5 / density)
    
    def _calculate_structure_score(self, script: Dict[str, Any]) -> float:
        """構造品質スコア計算"""
        
        # 必須セクションの存在確認
        required_sections = [
            'success_factors_analysis',
            'improvement_points',
            'counseling_script',
            'practical_improvements'
        ]
        
        present_sections = sum(
            1 for section in required_sections 
            if section in script and script[section] and len(str(script[section]).strip()) > 30
        )
        
        # カウンセリングスクリプトの各フェーズ確認
        counseling_script = script.get('counseling_script', {})
        required_phases = ['opening', 'needs_assessment', 'solution_proposal', 'closing']
        
        present_phases = sum(
            1 for phase in required_phases
            if phase in counseling_script and counseling_script[phase] and len(str(counseling_script[phase]).strip()) > 20
        )
        
        section_score = present_sections / len(required_sections)
        phase_score = present_phases / len(required_phases)
        
        return (section_score + phase_score) / 2
    
    def _calculate_expertise_score(self, text: str) -> float:
        """専門性スコア計算"""
        
        # 美容脱毛業界の専門用語
        expert_terms = [
            '脱毛', '美容', 'カウンセリング', '成約', '顧客', 'クライアント',
            'レーザー', '光脱毛', 'IPL', '医療', '施術', '契約', '料金プラン',
            'カウンセラー', 'エステ', 'サロン', 'クリニック'
        ]
        
        expert_count = sum(
            text.count(term) for term in expert_terms
        )
        
        words = text.split()
        if not words:
            return 0.0
        
        # 専門用語の密度
        density = expert_count / len(words) * 100
        
        # 1-3%の密度が理想的
        if 1 <= density <= 3:
            return 1.0
        elif density < 1:
            return density
        else:
            return max(0.6, 3 / density)
    
    def _calculate_content_metrics(self, text: str) -> Dict[str, Any]:
        """コンテンツメトリクス計算"""
        
        words = text.split()
        sentences = text.split('。')
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'character_count': len(text),
            'paragraph_count': text.count('\n\n') + 1
        }
    
    def _generate_content_improvements(
        self, 
        readability: float, 
        actionability: float, 
        structure: float, 
        expertise: float
    ) -> List[str]:
        """コンテンツ改善提案生成"""
        
        suggestions = []
        
        if readability < 0.7:
            suggestions.append("文章をより簡潔で読みやすくする")
        
        if actionability < 0.7:
            suggestions.append("具体的な実践方法やテクニックを追加する")
        
        if structure < 0.7:
            suggestions.append("構造を整理し、欠落セクションを補完する")
        
        if expertise < 0.7:
            suggestions.append("業界専門用語を適切に使用し、専門性を向上させる")
        
        return suggestions


# ユーティリティ関数
def create_script_quality_analyzer() -> ScriptQualityAnalyzer:
    """ScriptQualityAnalyzerのファクトリー関数"""
    return ScriptQualityAnalyzer()