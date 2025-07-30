"""
OpenAI Embedding API を使用したベクトル化サービス
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
import openai
from openai import AsyncOpenAI
import numpy as np
import tiktoken

from app.core.config import settings


logger = logging.getLogger(__name__)


class EmbeddingService:
    """OpenAI text-embedding-3-small を使用したテキストベクトル化サービス"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "text-embedding-3-small"
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.max_tokens = 512  # チャンク分割の最大トークン数
        self.batch_size = 20  # バッチ処理のサイズ
        
    def count_tokens(self, text: str) -> int:
        """テキストのトークン数をカウント"""
        return len(self.encoding.encode(text))
    
    def chunk_text(self, text: str, max_tokens: int = None) -> List[str]:
        """テキストを指定トークン数で分割"""
        if max_tokens is None:
            max_tokens = self.max_tokens
            
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
        return chunks
    
    async def embed_text(self, text: str) -> List[float]:
        """単一テキストのベクトル化"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"テキストベクトル化エラー: {e}")
            raise
    
    async def embed_texts_batch(self, texts: List[str]) -> List[List[float]]:
        """複数テキストのバッチベクトル化"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"バッチベクトル化エラー: {e}")
            raise
    
    async def embed_texts_with_chunking(
        self, 
        texts: List[str],
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        長文テキストをチャンク分割してベクトル化
        
        Args:
            texts: ベクトル化するテキストのリスト
            include_metadata: メタデータを含めるかどうか
            
        Returns:
            [
                {
                    'text': 'チャンクテキスト',
                    'embedding': [0.1, 0.2, ...],
                    'metadata': {
                        'original_index': 0,
                        'chunk_index': 0,
                        'total_chunks': 3,
                        'token_count': 256
                    }
                },
                ...
            ]
        """
        all_chunks = []
        chunk_metadata = []
        
        # 1. 全テキストをチャンク分割
        for text_idx, text in enumerate(texts):
            token_count = self.count_tokens(text)
            
            if token_count <= self.max_tokens:
                # トークン数が制限以下の場合はそのまま使用
                all_chunks.append(text)
                if include_metadata:
                    chunk_metadata.append({
                        'original_index': text_idx,
                        'chunk_index': 0,
                        'total_chunks': 1,
                        'token_count': token_count
                    })
            else:
                # チャンク分割が必要
                chunks = self.chunk_text(text)
                all_chunks.extend(chunks)
                
                if include_metadata:
                    for chunk_idx, chunk in enumerate(chunks):
                        chunk_metadata.append({
                            'original_index': text_idx,
                            'chunk_index': chunk_idx,
                            'total_chunks': len(chunks),
                            'token_count': self.count_tokens(chunk)
                        })
        
        # 2. バッチ処理でベクトル化
        embeddings = await self._process_chunks_in_batches(all_chunks)
        
        # 3. 結果の構築
        results = []
        for i, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
            result = {
                'text': chunk,
                'embedding': embedding
            }
            if include_metadata and i < len(chunk_metadata):
                result['metadata'] = chunk_metadata[i]
            results.append(result)
        
        return results
    
    async def _process_chunks_in_batches(self, chunks: List[str]) -> List[List[float]]:
        """チャンクをバッチ処理でベクトル化"""
        all_embeddings = []
        
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            
            try:
                batch_embeddings = await self.embed_texts_batch(batch)
                all_embeddings.extend(batch_embeddings)
                
                # API制限を考慮して少し待機
                if i + self.batch_size < len(chunks):
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"バッチ {i//self.batch_size + 1} の処理エラー: {e}")
                # エラー時は個別処理にフォールバック
                for chunk in batch:
                    try:
                        embedding = await self.embed_text(chunk)
                        all_embeddings.append(embedding)
                        await asyncio.sleep(0.05)
                    except Exception as chunk_error:
                        logger.error(f"個別チャンク処理エラー: {chunk_error}")
                        # エラー時はゼロベクトルで代替
                        all_embeddings.append([0.0] * 1536)
        
        return all_embeddings
    
    async def embed_conversation_for_search(
        self, 
        conversation_text: str,
        conversation_type: str = "failure"
    ) -> List[float]:
        """
        失敗会話など、検索用の一時的なベクトル化
        保存はせず、検索クエリとして使用
        """
        try:
            # 長文の場合は最初のチャンクのみ使用
            if self.count_tokens(conversation_text) > self.max_tokens:
                chunks = self.chunk_text(conversation_text, self.max_tokens)
                search_text = chunks[0]  # 最初のチャンクを代表として使用
            else:
                search_text = conversation_text
                
            embedding = await self.embed_text(search_text)
            logger.info(f"{conversation_type}会話のベクトル化完了: {len(embedding)}次元")
            
            return embedding
            
        except Exception as e:
            logger.error(f"検索用ベクトル化エラー: {e}")
            raise


class TextChunkingService:
    """テキスト分割専用サービス"""
    
    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def smart_chunk_conversation(
        self, 
        conversation_text: str, 
        max_tokens: int = 512,
        overlap_tokens: int = 50
    ) -> List[Dict[str, Any]]:
        """
        会話テキストをスマートに分割
        発話の境界を考慮して分割
        """
        # 簡単な発話分割（カウンセラー/顧客の発話境界で分割）
        sentences = self._split_by_speaker_turns(conversation_text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.encoding.encode(sentence))
            
            if current_tokens + sentence_tokens <= max_tokens:
                current_chunk += sentence + " "
                current_tokens += sentence_tokens
            else:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'token_count': current_tokens
                    })
                
                # 新しいチャンクを開始
                current_chunk = sentence + " "
                current_tokens = sentence_tokens
        
        # 最後のチャンクを追加
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'token_count': current_tokens
            })
        
        return chunks
    
    def _split_by_speaker_turns(self, text: str) -> List[str]:
        """発話ターンで分割（簡易版）"""
        # 実際の実装では、より高度な発話分割ロジックを使用
        import re
        
        # 改行や句読点で分割
        sentences = re.split(r'[。！？\n]+', text)
        return [s.strip() for s in sentences if s.strip()]


# シングルトンインスタンス
embedding_service = EmbeddingService()
chunking_service = TextChunkingService()