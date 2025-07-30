"""
GPT-4o統合・スクリプト生成実行サービス
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime
import uuid
from openai import AsyncOpenAI
import tiktoken

from app.core.config import settings
from app.services.prompt_builder_service import create_prompt_builder
from app.services.vector_search_service import create_vector_search_service
from app.services.representative_extraction_service import create_representative_extraction_service
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


class ScriptGenerationService:
    """スクリプト生成メインサービス"""
    
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.prompt_builder = create_prompt_builder()
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.model = "gpt-4o"
        
    async def generate_improvement_script(
        self,
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        改善スクリプト生成のメイン処理
        
        Args:
            analysis_data: {
                'cluster_result_id': 'uuid',
                'failure_conversations': [...],
                'filters': {...}
            }
            
        Returns:
            {
                'script': {生成されたスクリプト構造},
                'quality_metrics': {品質メトリクス},
                'generation_metadata': {生成メタデータ}
            }
        """
        try:
            start_time = datetime.utcnow()
            generation_id = str(uuid.uuid4())
            
            logger.info(f"スクリプト生成開始: {generation_id}")
            
            # 1. データ準備
            prepared_data = await self._prepare_generation_data(analysis_data)
            
            # 2. プロンプト構築
            prompt_result = self.prompt_builder.build_script_generation_prompt(
                representative_successes=prepared_data['representatives'],
                failure_to_success_mappings=prepared_data['failure_mappings'],
                failure_conversations=prepared_data['failures']
            )
            
            # 3. GPT-4o API呼び出し
            generation_result = await self._generate_with_gpt4o(
                prompt=prompt_result['prompt'],
                generation_id=generation_id
            )
            
            # 4. レスポンス構造化
            structured_script = self._parse_script_response(generation_result['content'])
            
            # 5. 品質検証
            quality_metrics = await self._validate_script_quality(
                structured_script,
                prepared_data
            )
            
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # 6. 結果構築
            result = {
                'script': structured_script,
                'quality_metrics': quality_metrics,
                'generation_metadata': {
                    'generation_id': generation_id,
                    'prompt_metadata': prompt_result['metadata'],
                    'openai_usage': generation_result['usage'],
                    'processing_time': processing_time,
                    'cost_estimate': self._calculate_cost(generation_result['usage']),
                    'created_at': end_time.isoformat(),
                    'model': self.model
                }
            }
            
            logger.info(f"スクリプト生成完了: {generation_id} ({processing_time:.1f}s)")
            return result
            
        except Exception as e:
            logger.error(f"スクリプト生成エラー: {e}")
            raise ScriptGenerationError(f"スクリプト生成に失敗しました: {str(e)}")
    
    async def _prepare_generation_data(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成用データの準備"""
        
        cluster_result_id = analysis_data.get('cluster_result_id')
        failure_conversations = analysis_data.get('failure_conversations', [])
        filters = analysis_data.get('filters', {})
        
        # 代表例取得
        extraction_service = create_representative_extraction_service(self.db)
        representatives = await extraction_service.get_representatives_for_script_generation(
            cluster_result_id=cluster_result_id,
            max_total_representatives=8
        )
        
        # 失敗→成功マッピング生成
        failure_mappings = []
        if failure_conversations:
            search_service = create_vector_search_service(self.db)
            
            for failure in failure_conversations:
                mapping = await search_service.search_similar_for_failure_conversation(
                    failure_conversation_text=failure['text'],
                    top_k=3,
                    similarity_threshold=0.7,
                    include_analysis=True
                )
                failure_mappings.append(mapping)
        
        return {
            'representatives': representatives,
            'failure_mappings': failure_mappings,
            'failures': failure_conversations
        }
    
    async def _generate_with_gpt4o(
        self, 
        prompt: str, 
        generation_id: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """GPT-4o APIでの生成実行"""
        
        for attempt in range(max_retries):
            try:
                logger.info(f"GPT-4o API呼び出し: 試行{attempt + 1}/{max_retries}")
                
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "あなたは美容脱毛業界の専門カウンセリングアドバイザーです。データに基づいて実用的で効果的な改善スクリプトを生成してください。"
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=4000,
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1
                )
                
                if response.choices and response.choices[0].message.content:
                    return {
                        'content': response.choices[0].message.content,
                        'usage': {
                            'prompt_tokens': response.usage.prompt_tokens,
                            'completion_tokens': response.usage.completion_tokens,
                            'total_tokens': response.usage.total_tokens
                        },
                        'model': response.model,
                        'finish_reason': response.choices[0].finish_reason
                    }
                else:
                    raise ScriptGenerationError("GPT-4oから有効なレスポンスを取得できませんでした")
                    
            except Exception as e:
                logger.warning(f"GPT-4o API試行{attempt + 1}失敗: {e}")
                
                if attempt == max_retries - 1:
                    raise ScriptGenerationError(f"GPT-4o API呼び出しが{max_retries}回失敗しました: {str(e)}")
                
                # 指数バックオフで待機
                await asyncio.sleep(2 ** attempt)
        
        raise ScriptGenerationError("GPT-4o API呼び出しに失敗しました")
    
    def _parse_script_response(self, raw_response: str) -> Dict[str, Any]:
        """GPT-4oレスポンスの構造化"""
        
        try:
            # Markdownセクションの抽出
            sections = self._extract_markdown_sections(raw_response)
            
            # 構造化されたスクリプトデータを構築
            structured_script = {
                'success_factors_analysis': sections.get('成功パターン別共通要因分析', ''),
                'improvement_points': sections.get('失敗→成功への具体的改善ポイント', ''),
                'counseling_script': {
                    'opening': self._extract_script_phase(sections, 'オープニング'),
                    'needs_assessment': self._extract_script_phase(sections, 'ニーズ確認'),
                    'solution_proposal': self._extract_script_phase(sections, 'ソリューション提案'),
                    'closing': self._extract_script_phase(sections, 'クロージング')
                },
                'practical_improvements': sections.get('実用的な改善ポイント', ''),
                'expected_effects': sections.get('期待される効果', ''),
                'detailed_analysis': sections.get('詳細分析レポート', ''),
                'raw_content': raw_response,
                'parsed_at': datetime.utcnow().isoformat()
            }
            
            return structured_script
            
        except Exception as e:
            logger.error(f"レスポンス構造化エラー: {e}")
            
            # フォールバック: 最小限の構造化
            return {
                'raw_content': raw_response,
                'parsed_at': datetime.utcnow().isoformat(),
                'parsing_error': str(e),
                'counseling_script': {
                    'opening': '',
                    'needs_assessment': '',
                    'solution_proposal': '',
                    'closing': ''
                }
            }
    
    def _extract_markdown_sections(self, text: str) -> Dict[str, str]:
        """Markdownセクションを抽出"""
        
        sections = {}
        current_section = None
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            # ヘッダー行の検出（### または ## で始まる）
            header_match = re.match(r'^#{2,3}\s+(.+)', line.strip())
            
            if header_match:
                # 前のセクションを保存
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # 新しいセクション開始
                current_section = header_match.group(1).strip()
                current_content = []
            else:
                # セクション内容を追加
                if current_section:
                    current_content.append(line)
        
        # 最後のセクションを保存
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_script_phase(self, sections: Dict[str, str], phase_name: str) -> str:
        """特定のスクリプトフェーズを抽出"""
        
        # フェーズ名のバリエーションを考慮
        phase_variations = {
            'オープニング': ['オープニング', 'A. オープニング', '#### A. オープニング'],
            'ニーズ確認': ['ニーズ確認', 'B. ニーズ確認', '#### B. ニーズ確認'],
            'ソリューション提案': ['ソリューション提案', 'C. ソリューション提案', '#### C. ソリューション提案'],
            'クロージング': ['クロージング', 'D. クロージング', '#### D. クロージング']
        }
        
        # 改善カウンセリングスクリプトセクション内を検索
        script_section = sections.get('改善カウンセリングスクリプト', '')
        
        if phase_name in phase_variations:
            for variation in phase_variations[phase_name]:
                # セクション内で該当フェーズを検索
                phase_content = self._extract_subsection(script_section, variation)
                if phase_content:
                    return phase_content
        
        return ''
    
    def _extract_subsection(self, text: str, subsection_name: str) -> str:
        """テキスト内から特定のサブセクションを抽出"""
        
        lines = text.split('\n')
        in_target_section = False
        content_lines = []
        
        for line in lines:
            # サブセクションの開始を検出
            if subsection_name in line and ('####' in line or '**' in line):
                in_target_section = True
                continue
            
            # 次のサブセクション開始で終了
            if in_target_section and ('####' in line or (line.startswith('**') and line.endswith('**'))):
                break
            
            # 対象セクション内のコンテンツを収集
            if in_target_section:
                content_lines.append(line)
        
        return '\n'.join(content_lines).strip()
    
    async def _validate_script_quality(
        self, 
        script: Dict[str, Any], 
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """スクリプト品質の検証"""
        
        quality_metrics = {
            'completeness_score': self._calculate_completeness_score(script),
            'content_quality_score': self._calculate_content_quality_score(script),
            'structure_score': self._calculate_structure_score(script),
            'actionability_score': self._calculate_actionability_score(script),
            'overall_quality': 0.0,
            'validation_details': {},
            'validated_at': datetime.utcnow().isoformat()
        }
        
        # 総合品質スコア計算
        quality_metrics['overall_quality'] = (
            quality_metrics['completeness_score'] * 0.3 +
            quality_metrics['content_quality_score'] * 0.3 +
            quality_metrics['structure_score'] * 0.2 +
            quality_metrics['actionability_score'] * 0.2
        )
        
        return quality_metrics
    
    def _calculate_completeness_score(self, script: Dict[str, Any]) -> float:
        """完全性スコア計算"""
        required_sections = [
            'success_factors_analysis',
            'improvement_points', 
            'counseling_script',
            'practical_improvements'
        ]
        
        present_sections = sum(
            1 for section in required_sections 
            if script.get(section) and len(str(script[section]).strip()) > 50
        )
        
        return present_sections / len(required_sections)
    
    def _calculate_content_quality_score(self, script: Dict[str, Any]) -> float:
        """コンテンツ品質スコア計算"""
        
        # 重要キーワードの含有チェック
        important_keywords = [
            '成約率', '顧客', 'カウンセリング', '脱毛', '効果', '料金', 
            '相談', '安心', '体験', '提案', '改善', '具体的'
        ]
        
        all_content = ' '.join([
            str(script.get('success_factors_analysis', '')),
            str(script.get('improvement_points', '')),
            str(script.get('practical_improvements', ''))
        ])
        
        keyword_score = sum(
            keyword in all_content for keyword in important_keywords
        ) / len(important_keywords)
        
        # 長さの適切性チェック
        total_length = len(all_content)
        length_score = min(1.0, total_length / 2000) if total_length > 500 else 0.5
        
        return (keyword_score + length_score) / 2
    
    def _calculate_structure_score(self, script: Dict[str, Any]) -> float:
        """構造スコア計算"""
        counseling_script = script.get('counseling_script', {})
        
        # 各フェーズの存在チェック
        phases = ['opening', 'needs_assessment', 'solution_proposal', 'closing']
        present_phases = sum(
            1 for phase in phases 
            if counseling_script.get(phase) and len(str(counseling_script[phase]).strip()) > 30
        )
        
        return present_phases / len(phases)
    
    def _calculate_actionability_score(self, script: Dict[str, Any]) -> float:
        """実行可能性スコア計算"""
        
        # 具体的な表現の有無チェック
        actionable_indicators = [
            '具体的', '例えば', 'ポイント', 'コツ', '方法', 'テクニック',
            '言い回し', '表現', 'アプローチ', '話し方'
        ]
        
        practical_content = str(script.get('practical_improvements', ''))
        
        indicator_score = sum(
            indicator in practical_content for indicator in actionable_indicators
        ) / len(actionable_indicators)
        
        return indicator_score
    
    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        """生成コストの計算（USD）"""
        
        # GPT-4o価格（2024年7月時点の想定価格）
        input_cost_per_1k = 0.03  # $0.03 per 1K input tokens
        output_cost_per_1k = 0.06  # $0.06 per 1K output tokens
        
        input_cost = (usage.get('prompt_tokens', 0) / 1000) * input_cost_per_1k
        output_cost = (usage.get('completion_tokens', 0) / 1000) * output_cost_per_1k
        
        return round(input_cost + output_cost, 4)


class ScriptGenerationError(Exception):
    """スクリプト生成関連のエラー"""
    pass


class ResponseParser:
    """レスポンス解析専用クラス"""
    
    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """セクション抽出の高度な処理"""
        # より高度な解析ロジックが必要な場合はここで実装
        pass
    
    @staticmethod
    def validate_script_structure(script: Dict[str, Any]) -> bool:
        """スクリプト構造の妥当性検証"""
        required_keys = ['counseling_script', 'improvement_points']
        return all(key in script for key in required_keys)


# ユーティリティ関数
def create_script_generation_service(db: Session) -> ScriptGenerationService:
    """ScriptGenerationServiceのファクトリー関数"""
    return ScriptGenerationService(db)