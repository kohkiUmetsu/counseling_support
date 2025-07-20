"""
高品質プロンプト構築エンジン
GPT-4o用の最適化されたプロンプトを自動生成
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import tiktoken
from datetime import datetime
import json

from app.core.config import settings


logger = logging.getLogger(__name__)


class HighQualityPromptBuilder:
    """GPT-4o用高品質プロンプト構築サービス"""
    
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.max_prompt_tokens = 15000  # GPT-4oのコンテキスト制限を考慮
        self.target_completion_tokens = 4000  # 生成スクリプトの想定トークン数
        
    def build_script_generation_prompt(
        self,
        representative_successes: List[Dict[str, Any]],
        failure_to_success_mappings: List[Dict[str, Any]],
        failure_conversations: List[Dict[str, Any]],
        generation_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        スクリプト生成用の最適化プロンプトを構築
        
        Args:
            representative_successes: クラスタ代表成功例
            failure_to_success_mappings: 失敗→成功マッピング
            failure_conversations: 分析対象失敗会話
            generation_config: 生成設定
            
        Returns:
            {
                'prompt': 'プロンプト文字列',
                'metadata': {
                    'token_count': 12500,
                    'optimization_applied': True,
                    'sections': {...}
                }
            }
        """
        try:
            # デフォルト設定
            config = generation_config or {}
            focus_areas = config.get('focus_areas', ['opening', 'needs_assessment', 'solution_proposal', 'closing'])
            target_success_rate = config.get('target_success_rate', 0.8)
            include_detailed_analysis = config.get('include_detailed_analysis', True)
            
            # プロンプトセクションを構築
            sections = self._build_prompt_sections(
                representative_successes=representative_successes,
                failure_to_success_mappings=failure_to_success_mappings,
                failure_conversations=failure_conversations,
                focus_areas=focus_areas,
                target_success_rate=target_success_rate,
                include_detailed_analysis=include_detailed_analysis
            )
            
            # 初期プロンプト組み立て
            initial_prompt = self._assemble_prompt(sections)
            initial_token_count = self._count_tokens(initial_prompt)
            
            # トークン数最適化
            if initial_token_count > self.max_prompt_tokens:
                logger.info(f"プロンプト最適化実行: {initial_token_count} -> 目標{self.max_prompt_tokens}")
                optimized_sections = self._optimize_prompt_sections(
                    sections, 
                    target_tokens=self.max_prompt_tokens
                )
                final_prompt = self._assemble_prompt(optimized_sections)
                optimization_applied = True
            else:
                final_prompt = initial_prompt
                optimization_applied = False
            
            final_token_count = self._count_tokens(final_prompt)
            
            return {
                'prompt': final_prompt,
                'metadata': {
                    'token_count': final_token_count,
                    'initial_token_count': initial_token_count,
                    'optimization_applied': optimization_applied,
                    'cost_reduction_rate': (initial_token_count - final_token_count) / initial_token_count if optimization_applied else 0,
                    'sections': {section: self._count_tokens(content) for section, content in sections.items()},
                    'generation_config': config,
                    'created_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"プロンプト構築エラー: {e}")
            raise
    
    def _build_prompt_sections(
        self,
        representative_successes: List[Dict[str, Any]],
        failure_to_success_mappings: List[Dict[str, Any]],
        failure_conversations: List[Dict[str, Any]],
        focus_areas: List[str],
        target_success_rate: float,
        include_detailed_analysis: bool
    ) -> Dict[str, str]:
        """プロンプトの各セクションを構築"""
        
        sections = {}
        
        # システムプロンプト（役割定義）
        sections['system'] = self._build_system_prompt(target_success_rate)
        
        # 成功パターン分析セクション
        sections['success_patterns'] = self._format_success_patterns(representative_successes)
        
        # 失敗→成功マッピングセクション  
        sections['failure_to_success'] = self._format_failure_to_success_patterns(failure_to_success_mappings)
        
        # 分析対象失敗事例セクション
        sections['target_failures'] = self._format_failure_cases(failure_conversations, focus_areas)
        
        # 出力要求セクション
        sections['output_requirements'] = self._build_output_requirements(focus_areas, include_detailed_analysis)
        
        # 制約条件・品質ガイドライン
        sections['constraints'] = self._build_constraints_and_guidelines()
        
        return sections
    
    def _build_system_prompt(self, target_success_rate: float) -> str:
        """システムプロンプト（役割定義）を構築"""
        return f"""あなたは美容脱毛業界のカウンセリング専門家として、過去の成功・失敗事例を分析し、成約率{target_success_rate:.0%}以上を目標とする改善スクリプトを生成する専門AIです。

## あなたの専門性
- 美容脱毛業界での豊富なカウンセリング経験
- 顧客心理と成約要因の深い理解
- データドリブンな改善提案スキル
- 実用的で自然な会話スクリプト作成能力

## 分析アプローチ
1. クラスタリングされた成功パターンの特徴抽出
2. 失敗→成功の転換要因分析
3. 顧客ニーズと効果的な対応方法の特定
4. 実践的で即効性のある改善案提示"""
    
    def _format_success_patterns(self, representatives: List[Dict[str, Any]]) -> str:
        """成功パターンを整形"""
        if not representatives:
            return "## 成功パターン分析\n分析に十分な成功事例データがありません。"
        
        formatted = "## 成功パターン分析（クラスタリング結果）\n\n"
        
        for i, rep in enumerate(representatives, 1):
            cluster_label = rep.get('cluster_label', i-1)
            text = rep.get('text', '')
            quality_score = rep.get('quality_score', 0)
            characteristics = rep.get('cluster_characteristics', {})
            session_info = rep.get('session_info', {})
            
            # テキストを適切な長さに調整
            display_text = self._truncate_text(text, max_length=300)
            
            formatted += f"""### 成功パターン{i} (クラスタ{cluster_label})
**品質スコア**: {quality_score:.2f}
**特徴**: {characteristics.get('characteristics', '特徴分析中')}
**代表例**:
```
{display_text}
```
**カウンセラー**: {session_info.get('counselor_name', '不明')}
**共通キーワード**: {', '.join(characteristics.get('common_keywords', [])[:5])}

"""
        
        return formatted
    
    def _format_failure_to_success_patterns(self, mappings: List[Dict[str, Any]]) -> str:
        """失敗→成功マッピングを整形"""
        if not mappings:
            return "## 失敗→成功の改善パターン\n対応する改善パターンが見つかりませんでした。"
        
        formatted = "## 失敗→成功の改善パターン\n\n"
        
        for i, mapping in enumerate(mappings, 1):
            failure_info = mapping.get('failure_analysis', {})
            similar_successes = mapping.get('similar_successes', [])
            
            if similar_successes:
                best_success = similar_successes[0]  # 最も類似度の高い成功例
                
                formatted += f"""### 改善パターン{i}
**失敗事例の特徴**:
- テキスト: {self._truncate_text(failure_info.get('text', ''), 200)}
- 問題要因: {', '.join(best_success.get('key_differences', []))}

**類似成功事例** (類似度: {best_success.get('similarity_score', 0):.2f}):
```
{self._truncate_text(best_success.get('chunk_text', ''), 250)}
```

**改善ヒント**:
{self._format_improvement_hints(best_success.get('improvement_hints', []))}

"""
        
        return formatted
    
    def _format_failure_cases(self, failures: List[Dict[str, Any]], focus_areas: List[str]) -> str:
        """分析対象失敗事例を整形"""
        if not failures:
            return "## 分析対象の失敗事例\n分析対象の失敗事例が指定されていません。"
        
        formatted = "## 分析対象の失敗事例\n\n"
        formatted += f"**改善フォーカス領域**: {', '.join(focus_areas)}\n\n"
        
        for i, failure in enumerate(failures, 1):
            text = failure.get('text', '')
            metadata = failure.get('metadata', {})
            
            formatted += f"""### 失敗事例{i}
**会話内容**:
```
{self._truncate_text(text, 400)}
```
**メタデータ**: カウンセラー: {metadata.get('counselor_name', '不明')}, 時期: {metadata.get('date', '不明')}

"""
        
        return formatted
    
    def _build_output_requirements(self, focus_areas: List[str], include_detailed_analysis: bool) -> str:
        """出力要求セクションを構築"""
        
        base_requirements = """## 出力要求

以下の構造で改善スクリプトを生成してください:

### 1. 成功パターン別共通要因分析
各クラスタの特徴と有効性を分析し、共通する成功要素を抽出してください。

### 2. 失敗→成功への具体的改善ポイント
- 失敗事例の根本的問題点
- 類似状況での成功要因との詳細比較
- すぐに実践できる具体的改善提案

### 3. 改善カウンセリングスクリプト
以下のフェーズ別に実用的なスクリプトを作成:

"""
        
        # フォーカス領域に応じたスクリプト要求を追加
        phase_mapping = {
            'opening': '#### A. オープニング\n- 信頼関係構築の言い回し\n- 効果的な導入トーク\n- 緊張緩和テクニック',
            'needs_assessment': '#### B. ニーズ確認\n- 的確な質問技法\n- 潜在ニーズの引き出し方\n- 共感的傾聴のポイント',
            'solution_proposal': '#### C. ソリューション提案\n- 顧客ニーズに合わせた提案方法\n- 効果的な価値訴求\n- 不安解消のアプローチ',
            'closing': '#### D. クロージング\n- 自然な契約導入\n- 決断サポート技法\n- 次ステップの明確化'
        }
        
        for area in focus_areas:
            if area in phase_mapping:
                base_requirements += phase_mapping[area] + "\n\n"
        
        base_requirements += """### 4. 実用的な改善ポイント
- 即座に実践できる具体的なアドバイス
- 成功事例からの効果的な言い回し例
- 避けるべき表現や行動

### 5. 期待される効果
- 想定される成約率改善度
- 顧客満足度向上ポイント
- 長期的な効果予測"""

        if include_detailed_analysis:
            base_requirements += """

### 6. 詳細分析レポート
- 統計的根拠とデータ裏付け
- リスク要因と対策
- 継続的改善のための指標"""
        
        return base_requirements
    
    def _build_constraints_and_guidelines(self) -> str:
        """制約条件とガイドラインを構築"""
        return """## 制約条件・品質ガイドライン

### 業界特化要件
- 美容脱毛業界のカウンセリングに特化した内容
- 法的コンプライアンス（医療広告ガイドライン等）遵守
- 業界用語の適切な使用

### 成約率重視
- 成約率向上を最優先目標とする
- 顧客の納得感を重視した自然な流れ
- 強引な営業手法は避ける

### 実用性重視
- 実際の会話で自然に使える表現
- カウンセラーが覚えやすい構成
- 即座に実践可能な具体性

### 品質基準
- 根拠となるデータへの言及
- 段階的で論理的な構成
- 明確で分かりやすい言葉遣い
- 顧客視点での価値提示

### 出力形式
- Markdown形式での構造化
- 具体例と抽象的概念のバランス
- セクション間の一貫性維持"""
    
    def _assemble_prompt(self, sections: Dict[str, str]) -> str:
        """セクションを組み立ててプロンプトを作成"""
        prompt_parts = [
            sections.get('system', ''),
            "",
            sections.get('success_patterns', ''),
            "",  
            sections.get('failure_to_success', ''),
            "",
            sections.get('target_failures', ''),
            "",
            sections.get('output_requirements', ''),
            "",
            sections.get('constraints', '')
        ]
        
        return "\n".join(prompt_parts)
    
    def _optimize_prompt_sections(
        self, 
        sections: Dict[str, str], 
        target_tokens: int
    ) -> Dict[str, str]:
        """プロンプトセクションのトークン数最適化"""
        
        # 各セクションの重要度（削減優先度：低い順）
        importance_order = [
            'constraints',      # 1. 制約条件（ある程度削減可能）
            'failure_to_success',  # 2. 失敗→成功マッピング
            'success_patterns',    # 3. 成功パターン（重要だが圧縮可能）
            'target_failures',     # 4. 分析対象（重要）
            'output_requirements', # 5. 出力要求（重要）
            'system'              # 6. システム（最重要）
        ]
        
        current_tokens = sum(self._count_tokens(content) for content in sections.values())
        target_reduction = current_tokens - target_tokens
        
        if target_reduction <= 0:
            return sections
        
        optimized_sections = sections.copy()
        
        # 段階的に最適化
        for section_name in importance_order:
            if section_name not in optimized_sections:
                continue
                
            current_section_tokens = self._count_tokens(optimized_sections[section_name])
            
            # セクションごとの削減率を調整
            if section_name == 'constraints':
                reduction_rate = 0.3  # 30%削減
            elif section_name == 'failure_to_success':
                reduction_rate = 0.2  # 20%削減
            elif section_name == 'success_patterns':
                reduction_rate = 0.25  # 25%削減
            else:
                reduction_rate = 0.15  # 15%削減
            
            target_section_tokens = int(current_section_tokens * (1 - reduction_rate))
            
            optimized_sections[section_name] = self._truncate_to_token_limit(
                optimized_sections[section_name], 
                target_section_tokens
            )
            
            # 目標に達したかチェック
            new_total = sum(self._count_tokens(content) for content in optimized_sections.values())
            if new_total <= target_tokens:
                break
        
        return optimized_sections
    
    def _count_tokens(self, text: str) -> int:
        """テキストのトークン数をカウント"""
        return len(self.encoding.encode(text))
    
    def _truncate_to_token_limit(self, text: str, max_tokens: int) -> str:
        """指定トークン数に切り詰め"""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """テキストを指定文字数で切り詰め"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def _format_improvement_hints(self, hints: List[str]) -> str:
        """改善ヒントをフォーマット"""
        if not hints:
            return "具体的な改善ヒントを分析中です。"
        
        formatted_hints = []
        for i, hint in enumerate(hints, 1):
            formatted_hints.append(f"  {i}. {hint}")
        
        return "\n".join(formatted_hints)


class PromptTemplateManager:
    """プロンプトテンプレート管理"""
    
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, str]:
        """デフォルトテンプレートを読み込み"""
        return {
            'basic_script_generation': """
# カウンセリングスクリプト改善タスク

あなたは美容脱毛業界の専門カウンセラーとして、以下の成功・失敗事例を分析し、改善スクリプトを生成してください。

{success_patterns}

{failure_analysis}

{output_requirements}

{constraints}
""",
            'focused_improvement': """
# 特定領域集中改善タスク

以下の{focus_area}に特化した改善スクリプトを生成してください。

{context_data}

{specific_requirements}
""",
            'rapid_optimization': """
# 高速最適化タスク

成約率向上に直結する即効性の高い改善ポイントを特定し、実用的なスクリプトを生成してください。

{key_patterns}

{improvement_targets}
"""
        }
    
    def get_template(self, template_name: str) -> str:
        """テンプレートを取得"""
        return self.templates.get(template_name, self.templates['basic_script_generation'])
    
    def customize_template(
        self, 
        template_name: str, 
        customizations: Dict[str, str]
    ) -> str:
        """テンプレートをカスタマイズ"""
        template = self.get_template(template_name)
        
        for placeholder, value in customizations.items():
            template = template.replace(f"{{{placeholder}}}", value)
        
        return template


# ユーティリティ関数
def create_prompt_builder() -> HighQualityPromptBuilder:
    """PromptBuilderのファクトリー関数"""
    return HighQualityPromptBuilder()

def create_template_manager() -> PromptTemplateManager:
    """TemplateManagerのファクトリー関数"""
    return PromptTemplateManager()