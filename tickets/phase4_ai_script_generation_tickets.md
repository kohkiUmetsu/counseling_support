# フェーズ4: AI分析・スクリプト生成システムチケット

## 概要
ベクトル検索結果を活用してGPT-4oで高品質なカウンセリングスクリプトを生成するフェーズです。要件定義書の機能F005、F008（メインコア機能）に対応します。

---

## チケット F4-001: 代表成功会話抽出・選別ロジック（F005）
**優先度**: 高  
**見積**: 8時間  
**担当者**: データサイエンティスト

### 説明
クラスタリング結果から各成功パターンの代表例を自動抽出し、GPT-4o入力用の高品質データセットを構築する。

### 要件
- クラスタごとの代表成功会話抽出
- 代表例の品質スコア算出
- 網羅性を確保する選別アルゴリズム
- 5-10件の最適な代表例選出

### 受け入れ条件
- [ ] 各クラスタから高品質な代表例が抽出される
- [ ] 代表例の品質スコア（重心距離、成約率、長さ等）が算出される
- [ ] 全成功パターンを網羅する代表例セットが選出される
- [ ] 代表例数が5-10件の最適範囲に収まる
- [ ] 選出ロジックの説明性が確保される

### 技術詳細
```python
# 実装対象サービス
- RepresentativeSelector: 代表例選別メイン処理
- QualityScorer: 品質スコア算出
- CoverageAnalyzer: 網羅性分析

# 品質スコア算出要素
class QualityScorer:
    def calculate_score(self, conversation):
        # 1. 重心距離スコア（クラスタ代表性）
        centroid_score = 1 - conversation['distance_to_centroid']
        
        # 2. 成約率スコア
        success_rate_score = conversation['success_rate']
        
        # 3. 長さスコア（適切な長さ）
        length_score = self.calculate_length_score(conversation['text'])
        
        # 4. 新規性スコア（既存代表例との差分）
        novelty_score = self.calculate_novelty(conversation, existing_representatives)
        
        # 重み付き合計
        total_score = (
            centroid_score * 0.3 +
            success_rate_score * 0.3 +
            length_score * 0.2 +
            novelty_score * 0.2
        )
        return total_score

# 網羅性確保アルゴリズム
def ensure_coverage(clusters, max_representatives=10):
    selected = []
    covered_clusters = set()
    
    # 各クラスタから最低1つ選出
    for cluster_id in clusters:
        best_candidate = select_best_from_cluster(cluster_id)
        selected.append(best_candidate)
        covered_clusters.add(cluster_id)
    
    # 残り枠で品質の高い追加代表例を選出
    remaining_slots = max_representatives - len(selected)
    additional_candidates = select_additional_representatives(clusters, remaining_slots)
    selected.extend(additional_candidates)
    
    return selected
```

---

## チケット F4-002: 失敗対応成功例検索機能（F005）
**優先度**: 高  
**見積**: 6時間  
**担当者**: バックエンドエンジニア

### 説明
失敗会話と意味的に類似した成功会話をベクトル検索で発見し、「似た状況で成功した例」を抽出する。

### 要件
- 失敗会話のベクトル化（一時的）
- 類似度の高い成功会話の検索
- 状況の類似性判定
- 成功要因の差分分析

### 受け入れ条件
- [ ] 失敗会話から類似状況の成功例が検索される
- [ ] 類似度スコア0.7以上の成功例が抽出される
- [ ] 失敗と成功の差分要因が特定される
- [ ] 検索結果に改善ヒントが含まれる
- [ ] 複数の失敗パターンに対応できる

### 技術詳細
```python
# 実装対象サービス
- FailureToSuccessMapper: 失敗→成功マッピング
- SituationAnalyzer: 状況類似性分析
- DifferenceAnalyzer: 差分要因分析

class FailureToSuccessMapper:
    def find_similar_successes(self, failure_conversation):
        # 1. 失敗会話のベクトル化
        failure_vector = self.embedding_service.embed_text(failure_conversation['text'])
        
        # 2. 類似成功会話検索
        similar_successes = self.vector_search_service.search_similar(
            query_vector=failure_vector,
            threshold=0.7,
            top_k=10,
            filters={'success_label': True}
        )
        
        # 3. 状況類似性の詳細分析
        analyzed_results = []
        for success in similar_successes:
            situation_similarity = self.analyze_situation_similarity(
                failure_conversation, success
            )
            success_factors = self.extract_success_factors(
                failure_conversation, success
            )
            
            analyzed_results.append({
                'success_conversation': success,
                'similarity_score': success['similarity_score'],
                'situation_similarity': situation_similarity,
                'key_differences': success_factors,
                'improvement_hints': self.generate_improvement_hints(success_factors)
            })
        
        return analyzed_results
    
    def analyze_situation_similarity(self, failure, success):
        # 状況要素の抽出・比較
        # - 顧客の悩み・ニーズ
        # - 提案されたプラン
        # - 会話のフェーズ
        # - 顧客の反応パターン
        pass
```

---

## チケット F4-003: 高品質プロンプト構築エンジン（F005）
**優先度**: 高  
**見積**: 10時間  
**担当者**: AI/LLMエンジニア

### 説明
代表成功会話と失敗対応成功例を組み合わせ、GPT-4oに送信する最適化されたプロンプトを自動構築する。

### 要件
- プロンプトテンプレートの設計
- 成功例・失敗例の構造化
- コンテキストサイズ最適化（40%コスト削減目標）
- 生成品質の向上

### 受け入れ条件
- [ ] 代表成功会話が効果的にプロンプトに組み込まれる
- [ ] 失敗→成功のマッピングが明確に示される
- [ ] プロンプトサイズが最適化されコストが40%削減される
- [ ] 生成されるスクリプトの品質が向上する
- [ ] プロンプトの再利用性が確保される

### 技術詳細
```python
# プロンプト構築テンプレート
class HighQualityPromptBuilder:
    def build_script_generation_prompt(self, representative_successes, failure_to_success_mappings, failure_conversations):
        prompt = f"""
# カウンセリングスクリプト改善分析タスク

## 目標
過去の成功事例と失敗事例の分析から、高成約率を実現する改善スクリプトを生成してください。

## 成功パターン分析（クラスタリング結果）

{self._format_success_patterns(representative_successes)}

## 失敗→成功の改善パターン

{self._format_failure_to_success_patterns(failure_to_success_mappings)}

## 分析対象の失敗事例

{self._format_failure_cases(failure_conversations)}

## 出力要求

1. **成功パターン別共通要因**
   - 各クラスタの特徴と有効性の分析
   - 共通する成功要素の抽出

2. **失敗→成功への具体的改善ポイント**
   - 失敗事例の問題点特定
   - 類似状況での成功要因との比較
   - 具体的な改善提案

3. **改善スクリプト生成**
   - オープニング、ニーズ確認、提案、クロージングの各フェーズ
   - 成功事例から抽出した効果的な言い回し
   - 失敗要因を回避する構成

4. **実用的な改善ポイント**
   - すぐに実践できる具体的なアドバイス
   - 成功事例の言い回し例の引用

## 制約条件
- 美容脱毛業界のカウンセリングに特化
- 成約率向上を最優先目標
- 実際の会話で自然に使える表現
- 強引な営業ではなく顧客の納得を重視
"""
        return prompt
    
    def _format_success_patterns(self, representatives):
        formatted = ""
        for i, rep in enumerate(representatives, 1):
            formatted += f"""
### 成功パターン{i}: {rep['cluster_name']}
- **代表例**: {rep['text'][:500]}...
- **成約率**: {rep['success_rate']:.1%}
- **特徴**: {rep['characteristics']}
"""
        return formatted
    
    def optimize_token_count(self, prompt, max_tokens=15000):
        # トークン数最適化
        # - 重要度に基づく情報の優先順位付け
        # - 冗長な表現の削除
        # - 構造化による効率的な情報提示
        pass
```

---

## チケット F4-004: GPT-4o統合・スクリプト生成実行（F005）
**優先度**: 高  
**見積**: 8時間  
**担当者**: バックエンドエンジニア

### 説明
構築されたプロンプトをGPT-4oに送信し、高品質な改善スクリプトを生成する機能を実装する。

### 要件
- OpenAI GPT-4o APIとの連携
- プロンプト最適化とトークン管理
- 生成結果の構造化・パース
- エラーハンドリング・リトライ機能

### 受け入れ条件
- [ ] GPT-4o APIで安定してスクリプトが生成される
- [ ] 生成時間が5分以内で完了する
- [ ] 生成結果がMarkdown形式で構造化される
- [ ] API制限やエラーに対する適切なリトライ機能がある
- [ ] 生成コストが予算内に収まる

### 技術詳細
```python
# 実装対象サービス
- ScriptGenerationService: スクリプト生成メイン処理
- OpenAIClient: GPT-4o API連携
- ResponseParser: 生成結果パース・構造化

class ScriptGenerationService:
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.prompt_builder = HighQualityPromptBuilder()
        self.response_parser = ResponseParser()
    
    async def generate_improvement_script(self, analysis_data):
        try:
            # 1. プロンプト構築
            prompt = self.prompt_builder.build_script_generation_prompt(
                representative_successes=analysis_data['representatives'],
                failure_to_success_mappings=analysis_data['failure_mappings'],
                failure_conversations=analysis_data['failures']
            )
            
            # 2. GPT-4o API呼び出し
            response = await self.openai_client.generate_completion(
                prompt=prompt,
                model="gpt-4o",
                max_tokens=4000,
                temperature=0.7,
                timeout=300  # 5分
            )
            
            # 3. レスポンス構造化
            structured_script = self.response_parser.parse_script_response(response)
            
            # 4. 品質検証
            quality_metrics = self.validate_script_quality(structured_script)
            
            return {
                'script': structured_script,
                'quality_metrics': quality_metrics,
                'generation_metadata': {
                    'prompt_tokens': response['usage']['prompt_tokens'],
                    'completion_tokens': response['usage']['completion_tokens'],
                    'cost': self.calculate_cost(response['usage']),
                    'generation_time': response['processing_time']
                }
            }
            
        except Exception as e:
            # エラーハンドリング・リトライ
            return await self.handle_generation_error(e, analysis_data)

# レスポンス構造化
class ResponseParser:
    def parse_script_response(self, raw_response):
        # Markdown構造の解析
        sections = self.extract_sections(raw_response)
        
        return {
            'opening': sections.get('オープニング'),
            'needs_assessment': sections.get('ニーズ確認'),
            'solution_proposal': sections.get('ソリューション提案'),
            'closing': sections.get('クロージング'),
            'success_factors': sections.get('成功要因'),
            'improvement_points': sections.get('改善ポイント'),
            'specific_phrases': sections.get('効果的な言い回し')
        }
```

---

## チケット F4-005: スクリプト品質分析・検証（F008）
**優先度**: 高  
**見積**: 7時間  
**担当者**: データサイエンティスト

### 説明
生成されたスクリプトの品質を定量的に評価・検証する機能を実装する。

### 要件
- カバレッジ分析（成功パターン網羅率）
- 新規性スコア（過去スクリプトとの差分）
- 成功要素マッチング率算出
- 推奨信頼度算出

### 受け入れ条件
- [ ] 成功パターンの網羅率が数値化される
- [ ] 過去スクリプトとの差分が定量化される
- [ ] 成功要素の含有率が算出される
- [ ] 推奨信頼度スコアが算出される
- [ ] 品質メトリクスがダッシュボードで確認できる

### 技術詳細
```python
# 実装対象サービス
- ScriptQualityAnalyzer: 品質分析メイン処理
- CoverageAnalyzer: カバレッジ分析
- NoveltyScorer: 新規性評価
- ReliabilityCalculator: 信頼度算出

class ScriptQualityAnalyzer:
    def analyze_script_quality(self, generated_script, base_data):
        metrics = {}
        
        # 1. カバレッジ分析
        coverage_analysis = self.analyze_coverage(generated_script, base_data['success_patterns'])
        metrics['coverage'] = {
            'pattern_coverage_rate': coverage_analysis['coverage_percentage'],
            'covered_patterns': coverage_analysis['covered_patterns'],
            'missing_patterns': coverage_analysis['missing_patterns'],
            'coverage_score': coverage_analysis['normalized_score']
        }
        
        # 2. 新規性スコア
        novelty_analysis = self.calculate_novelty(generated_script, base_data['historical_scripts'])
        metrics['novelty'] = {
            'novelty_score': novelty_analysis['score'],
            'unique_elements': novelty_analysis['unique_elements'],
            'similarity_to_past': novelty_analysis['past_similarity'],
            'innovation_areas': novelty_analysis['innovation_areas']
        }
        
        # 3. 成功要素マッチング率
        success_matching = self.analyze_success_element_matching(generated_script, base_data['success_elements'])
        metrics['success_matching'] = {
            'matching_rate': success_matching['rate'],
            'matched_elements': success_matching['matched'],
            'missing_elements': success_matching['missing'],
            'element_strength': success_matching['strength_scores']
        }
        
        # 4. 推奨信頼度
        reliability = self.calculate_reliability(base_data['source_quality'])
        metrics['reliability'] = {
            'confidence_score': reliability['confidence'],
            'data_quality_score': reliability['data_quality'],
            'sample_size_adequacy': reliability['sample_adequacy'],
            'recommendation_strength': reliability['strength']
        }
        
        # 5. 総合品質スコア
        metrics['overall_quality'] = self.calculate_overall_quality(metrics)
        
        return metrics
    
    def analyze_coverage(self, script, success_patterns):
        # 成功パターンがスクリプトに含まれているかチェック
        covered_patterns = []
        for pattern in success_patterns:
            if self.is_pattern_covered(script, pattern):
                covered_patterns.append(pattern)
        
        coverage_percentage = len(covered_patterns) / len(success_patterns) * 100
        return {
            'coverage_percentage': coverage_percentage,
            'covered_patterns': covered_patterns,
            'missing_patterns': [p for p in success_patterns if p not in covered_patterns],
            'normalized_score': min(coverage_percentage / 80, 1.0)  # 80%を満点とする
        }
```

---

## チケット F4-006: スクリプト生成実行・管理API（F005）
**優先度**: 中  
**見積**: 5時間  
**担当者**: バックエンドエンジニア

### 説明
スクリプト生成の実行・管理・履歴管理機能をAPIで実装する。

### 要件
- 手動生成実行API
- 生成状況監視API
- 履歴管理・バージョン管理
- 生成設定カスタマイズ

### 受け入れ条件
- [ ] 手動でスクリプト生成を実行できる
- [ ] 生成進捗をリアルタイムで確認できる
- [ ] 過去の生成履歴を確認できる
- [ ] 生成設定をカスタマイズできる
- [ ] 生成結果の比較ができる

### 技術詳細
```python
# API設計
POST /api/v1/scripts/generate  # スクリプト生成実行
GET /api/v1/scripts/generate/{job_id}/status  # 生成状況確認
GET /api/v1/scripts/history  # 生成履歴取得
GET /api/v1/scripts/{script_id}  # 特定スクリプト取得
POST /api/v1/scripts/{script_id}/activate  # スクリプト有効化

# リクエスト例
{
    "generation_config": {
        "include_failure_analysis": true,
        "max_representatives": 8,
        "cluster_count_range": [3, 10],
        "similarity_threshold": 0.7,
        "focus_areas": ["opening", "closing"],
        "target_success_rate": 0.8
    },
    "data_filters": {
        "date_range": ["2024-01-01", "2024-12-31"],
        "counselor_ids": ["counselor_1", "counselor_2"],
        "success_rate_min": 0.6
    }
}

# レスポンス例
{
    "job_id": "gen_20240120_001",
    "status": "completed",
    "script": {
        "content": {...},
        "quality_metrics": {...}
    },
    "execution_summary": {
        "total_success_conversations": 150,
        "clusters_identified": 6,
        "representatives_selected": 8,
        "generation_time": 287,
        "cost": 12.45
    }
}
```

---

## チケット F4-007: 継続学習・モデル改善機能
**優先度**: 低  
**見積**: 8時間  
**担当者**: AI/MLエンジニア

### 説明
新しい成功/失敗事例の蓄積に応じてモデルと生成品質を継続的に改善する機能を実装する。

### 要件
- 新規データでのモデル更新
- 生成品質の継続監視
- A/Bテスト機能
- フィードバックループ構築

### 受け入れ条件
- [ ] 新規データが自動的にモデルに反映される
- [ ] 生成品質が継続的に監視される
- [ ] 複数スクリプトのA/Bテストが可能
- [ ] 実成約率のフィードバックが反映される
- [ ] モデル性能の向上が確認できる

### 技術詳細
```python
# 継続学習パイプライン
class ContinuousLearningPipeline:
    def __init__(self):
        self.model_updater = ModelUpdater()
        self.quality_monitor = QualityMonitor()
        self.ab_tester = ABTester()
    
    def update_with_new_data(self, new_conversations):
        # 1. 新規データの品質検証
        validated_data = self.validate_new_data(new_conversations)
        
        # 2. ベクトル化・クラスタリング更新
        self.update_vector_clusters(validated_data)
        
        # 3. 代表例の再選出
        new_representatives = self.reselect_representatives()
        
        # 4. 生成品質の比較評価
        quality_comparison = self.compare_generation_quality(new_representatives)
        
        # 5. 改善が確認できた場合のみ更新
        if quality_comparison['improvement_confirmed']:
            self.deploy_updated_model(new_representatives)
        
        return quality_comparison
```

---

## フェーズ4完了条件
- [ ] 全チケットが完了している
- [ ] 代表成功会話の自動抽出が正常動作する
- [ ] 失敗会話から類似成功例の検索が機能する
- [ ] 高品質プロンプトの自動構築が動作する
- [ ] GPT-4oでの安定したスクリプト生成が可能
- [ ] スクリプト品質の定量的評価が機能する
- [ ] 生成コストが40%削減される
- [ ] 生成時間が5分以内で完了する
- [ ] 品質メトリクス（カバレッジ、新規性、信頼度）が正常表示される