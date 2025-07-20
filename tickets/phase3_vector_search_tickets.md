# フェーズ3: ベクトル化・検索エンジンシステムチケット

## 概要
成功会話のベクトル化、クラスタリング、高精度検索機能を実装するフェーズです。要件定義書の機能F004、F007に対応し、AIスクリプト生成の基盤となる重要なフェーズです。

---

## チケット F3-001: OpenAI Embedding APIベクトル化実装（F004）
**優先度**: 高  
**見積**: 8時間  
**担当者**: バックエンドエンジニア

### 説明
OpenAI text-embedding-3-smallを使用してテキストのベクトル化機能を実装する。

### 要件
- text-embedding-3-small APIとの連携
- 成功会話のみベクトル化（失敗会話は除外）
- チャンク分割処理（512トークン単位）
- バッチ処理対応（性能最適化）

### 受け入れ条件
- [ ] OpenAI Embedding APIが正常に動作する
- [ ] 成功ラベルの会話のみがベクトル化される
- [ ] 長文は512トークン単位で適切に分割される
- [ ] 複数テキストのバッチ処理で50%の高速化を実現
- [ ] 1536次元ベクトルが正しく生成される

### 技術詳細
```python
# 実装対象サービス
- EmbeddingService: OpenAI API呼び出し管理
- TextChunkingService: テキスト分割処理
- BatchProcessingService: バッチ処理最適化

# 処理フロー
1. 成功会話をtranscriptionsテーブルから取得
2. 512トークンでチャンク分割
3. バッチでOpenAI Embedding API呼び出し
4. 1536次元ベクトルをpgvectorに保存

# バッチ処理設定
- 最大20件/バッチ
- 並列処理数: 5
- エラーハンドリング・リトライ機能
```

---

## チケット F3-002: Aurora pgvectorデータベース設計（F004）
**優先度**: 高  
**見積**: 6時間  
**担当者**: データベースエンジニア

### 説明
Aurora PostgreSQL + pgvectorでベクトルデータベースを構築する。

### 要件
- pgvector拡張の有効化
- success_conversation_vectorsテーブル設計
- IVFFLATインデックス最適化
- コサイン類似度検索対応

### 受け入れ条件
- [ ] pgvector拡張が正常に動作する
- [ ] 1536次元ベクトルが適切に保存される
- [ ] IVFFLATインデックスが構築される
- [ ] コサイン類似度検索が5秒以内で完了する
- [ ] 1000件のベクトル検索で80%の高速化を実現

### 技術詳細
```sql
-- テーブル設計
CREATE TABLE success_conversation_vectors (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES counseling_sessions(id),
    chunk_text TEXT NOT NULL,
    embedding vector(1536),  -- pgvector型
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス設定
CREATE INDEX ON success_conversation_vectors 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- 性能最適化設定
SET ivfflat.probes = 10;
```

---

## チケット F3-003: ベクトル類似検索機能実装（F004）
**優先度**: 高  
**見積**: 7時間  
**担当者**: バックエンドエンジニア

### 説明
失敗会話と類似した成功会話をベクトル検索で抽出する機能を実装する。

### 要件
- 失敗会話のベクトル化（一時的）
- コサイン類似度による類似検索
- Top-K（5-20件）結果返却
- 動的フィルタリング機能

### 受け入れ条件
- [ ] 失敗会話から類似成功会話を検索できる
- [ ] コサイン類似度で正確な類似度計算ができる
- [ ] Top-K件数を動的に指定できる
- [ ] 成約率、時期、スタッフでフィルタリングできる
- [ ] 検索結果に類似度スコアが含まれる

### 技術詳細
```python
# 実装対象サービス
- VectorSearchService: ベクトル検索メイン処理
- SimilarityCalculator: 類似度計算
- DynamicFilterService: 動的フィルタリング

# API設計
POST /api/v1/vectors/search-similar
{
    "query_text": "失敗会話のテキスト",
    "top_k": 10,
    "filters": {
        "success_rate_min": 0.7,
        "date_range": ["2024-01-01", "2024-12-31"],
        "counselor_ids": ["counselor_1", "counselor_2"]
    }
}

# PostgreSQL検索クエリ
SELECT *, (embedding <=> %s) as similarity_score
FROM success_conversation_vectors 
WHERE metadata->>'success_rate' >= %s
ORDER BY embedding <=> %s LIMIT %s;
```

---

## チケット F3-004: K-means/HDBSCANクラスタリング実装（F007）
**優先度**: 高  
**見積**: 10時間  
**担当者**: データサイエンティスト

### 説明
成功会話のベクトルをクラスタリングして成功パターンを分類する機能を実装する。

### 要件
- K-meansとHDBSCANアルゴリズム対応
- クラスタ数の自動決定
- scikit-learn並列処理活用
- 500件のクラスタリングを30秒以内で完了

### 受け入れ条件
- [ ] K-meansクラスタリングが正常動作する
- [ ] HDBSCANクラスタリングが正常動作する
- [ ] 最適なクラスタ数が自動決定される
- [ ] 並列処理で30%の高速化を実現
- [ ] クラスタリング結果がDBに保存される

### 技術詳細
```python
# 実装対象サービス
- ClusteringService: クラスタリングメイン処理
- OptimalClustersDetector: 最適クラスタ数決定
- ClusterAnalyzer: クラスタ分析・可視化

# クラスタリングアルゴリズム
from sklearn.cluster import KMeans, HDBSCAN
from sklearn.metrics import silhouette_score

# K-means実装
def kmeans_clustering(vectors, k_range=(2, 15)):
    best_score = -1
    best_k = 2
    for k in range(*k_range):
        kmeans = KMeans(n_clusters=k, n_jobs=-1)
        labels = kmeans.fit_predict(vectors)
        score = silhouette_score(vectors, labels)
        if score > best_score:
            best_score = score
            best_k = k
    return best_k, kmeans

# HDBSCAN実装
def hdbscan_clustering(vectors):
    clusterer = HDBSCAN(min_cluster_size=5, metric='cosine')
    labels = clusterer.fit_predict(vectors)
    return clusterer, labels
```

---

## チケット F3-005: 代表成功会話抽出機能（F007）
**優先度**: 高  
**見積**: 6時間  
**担当者**: データサイエンティスト

### 説明
各クラスタの重心に最も近い成功会話を代表例として自動選出する機能を実装する。

### 要件
- クラスタ重心計算
- 重心との距離最小会話抽出
- 代表例の品質評価
- 各クラスタから1-3件の代表例抽出

### 受け入れ条件
- [ ] 各クラスタの重心が正確に計算される
- [ ] 重心に最も近い会話が代表例として選出される
- [ ] 代表例の品質スコアが算出される
- [ ] クラスタごとに1-3件の代表例が抽出される
- [ ] 代表例情報がDBに保存される

### 技術詳細
```python
# 実装対象サービス
- RepresentativeExtractor: 代表例抽出メイン処理
- CentroidCalculator: 重心計算
- QualityScorer: 代表例品質評価

# 代表例抽出アルゴリズム
def extract_representatives(cluster_vectors, cluster_labels, texts):
    representatives = []
    for cluster_id in np.unique(cluster_labels):
        cluster_mask = cluster_labels == cluster_id
        cluster_vectors_subset = cluster_vectors[cluster_mask]
        cluster_texts = texts[cluster_mask]
        
        # 重心計算
        centroid = np.mean(cluster_vectors_subset, axis=0)
        
        # 重心との距離計算
        distances = cosine_distances([centroid], cluster_vectors_subset)[0]
        
        # 最も近い会話を代表例として選出
        representative_idx = np.argmin(distances)
        representatives.append({
            'cluster_id': cluster_id,
            'text': cluster_texts[representative_idx],
            'distance_to_centroid': distances[representative_idx],
            'quality_score': calculate_quality_score(...)
        })
    
    return representatives
```

---

## チケット F3-006: 異常検出・特殊成功例識別（F007）
**優先度**: 中  
**見積**: 5時間  
**担当者**: データサイエンティスト

### 説明
一般的な成功パターンから外れた特殊成功例を識別する機能を実装する。

### 要件
- Isolation ForestまたはLocal Outlier Factor使用
- 異常度スコア算出
- 特殊成功例の詳細分析
- 異常検出結果の可視化

### 受け入れ条件
- [ ] 一般的成功パターンから外れた例が検出される
- [ ] 異常度スコアが適切に算出される
- [ ] 特殊成功例の特徴が分析される
- [ ] 異常検出結果が可視化される
- [ ] 特殊例情報がDBに保存される

### 技術詳細
```python
# 異常検出アルゴリズム
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

class AnomalyDetector:
    def __init__(self, method='isolation_forest'):
        if method == 'isolation_forest':
            self.detector = IsolationForest(contamination=0.1)
        elif method == 'lof':
            self.detector = LocalOutlierFactor(contamination=0.1)
    
    def detect_anomalies(self, vectors):
        anomaly_scores = self.detector.fit_predict(vectors)
        outlier_indices = np.where(anomaly_scores == -1)[0]
        return outlier_indices, anomaly_scores
```

---

## チケット F3-007: ベクトル検索API実装
**優先度**: 中  
**見積**: 4時間  
**担当者**: バックエンドエンジニア

### 説明
ベクトル検索機能のRESTful APIを実装する。

### 要件
- 類似検索API
- クラスタリング実行API
- 代表例取得API
- パフォーマンスモニタリング

### 受け入れ条件
- [ ] 類似検索APIが正常動作する
- [ ] クラスタリング実行APIが正常動作する
- [ ] 代表例取得APIが正常動作する
- [ ] API実行時間が適切に記録される
- [ ] エラーハンドリングが適切に実装される

### 技術詳細
```python
# API設計
# 類似検索
POST /api/v1/vectors/search
# クラスタリング実行
POST /api/v1/vectors/clustering
# 代表例取得
GET /api/v1/vectors/representatives
# 異常検出
POST /api/v1/vectors/anomaly-detection

# レスポンス例
{
  "results": [
    {
      "session_id": "uuid",
      "similarity_score": 0.95,
      "text": "成功会話テキスト",
      "metadata": {...}
    }
  ],
  "total": 15,
  "processing_time": 2.3
}
```

---

## チケット F3-008: ベクトル検索パフォーマンス最適化
**優先度**: 中  
**見積**: 6時間  
**担当者**: バックエンドエンジニア

### 説明
ベクトル検索のパフォーマンスを最適化する。

### 要件
- インデックス最適化
- クエリキャッシュ実装
- 並列処理対応
- メモリ使用量最適化

### 受け入れ条件
- [ ] 検索速度が80%向上する
- [ ] クエリキャッシュが正常動作する
- [ ] 並列処理で複数検索が高速化される
- [ ] メモリ使用量が30%削減される
- [ ] 大量データでも安定動作する

### 技術詳細
```python
# パフォーマンス最適化項目
1. pgvectorインデックス最適化
   - IVFFLATパラメータ調整
   - 定期的なVACUUM実行

2. Redisキャッシュ実装
   - 検索結果の一時保存
   - TTL設定による自動削除

3. バッチ処理最適化
   - 複数検索の並列実行
   - メモリプール管理

4. データベース接続最適化
   - コネクションプール管理
   - 読み取り専用レプリカ活用
```

---

## フェーズ3完了条件
- [ ] 全チケットが完了している
- [ ] 成功会話のベクトル化が正常動作する
- [ ] pgvectorでの高速検索が機能する
- [ ] クラスタリングによる成功パターン分類が動作する
- [ ] 代表成功会話の自動抽出が機能する
- [ ] 失敗会話から類似成功会話の検索が可能
- [ ] 異常検出で特殊成功例が識別される
- [ ] ベクトル検索APIが安定動作する
- [ ] 性能要件（検索5秒以内、クラスタリング30秒以内）を満たす