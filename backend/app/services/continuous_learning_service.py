from typing import List, Dict, Any, Optional, Tuple
import asyncio
import uuid
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import logging

from app.database import get_db
from app.models.session import CounselingSession
from app.models.vector import SuccessConversationVector
from app.services.embedding_service import EmbeddingService
from app.services.clustering_service import ClusteringService
from app.services.representative_extraction_service import RepresentativeExtractionService
from app.services.script_generation_service import ScriptGenerationService
from app.services.script_quality_analyzer import ScriptQualityAnalyzer

logger = logging.getLogger(__name__)

class ContinuousLearningService:
    """
    継続学習・モデル改善サービス
    新しい成功/失敗事例の蓄積に応じてモデルと生成品質を継続的に改善
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.clustering_service = ClusteringService()
        self.representative_service = RepresentativeExtractionService()
        self.script_service = ScriptGenerationService()
        self.quality_analyzer = ScriptQualityAnalyzer()
        
        # 学習パラメータ
        self.min_new_conversations = 10  # 更新に必要な最小新規会話数
        self.quality_improvement_threshold = 0.05  # 品質改善の最小閾値
        self.learning_interval_days = 7  # 学習実行間隔
        
    async def check_learning_trigger(self, db: Session) -> Dict[str, Any]:
        """
        継続学習の実行条件をチェック
        
        Returns:
            学習実行の判定結果と詳細情報
        """
        try:
            logger.info("継続学習トリガーチェック開始")
            
            # 前回の学習実行日時を取得
            last_learning_date = await self._get_last_learning_date(db)
            
            # 新規会話データの確認
            new_conversations = await self._get_new_conversations_since(db, last_learning_date)
            
            # 品質メトリクスの推移確認
            quality_trend = await self._analyze_quality_trend(db)
            
            # 実行条件の判定
            should_trigger = self._evaluate_learning_trigger(
                new_conversations, quality_trend, last_learning_date
            )
            
            trigger_info = {
                "should_trigger": should_trigger["trigger"],
                "trigger_reasons": should_trigger["reasons"],
                "new_conversations_count": len(new_conversations),
                "last_learning_date": last_learning_date,
                "quality_trend": quality_trend,
                "next_scheduled_learning": last_learning_date + timedelta(days=self.learning_interval_days) if last_learning_date else None
            }
            
            logger.info(f"学習トリガーチェック完了 - 実行判定: {should_trigger['trigger']}")
            return trigger_info
            
        except Exception as e:
            logger.error(f"学習トリガーチェックでエラー: {e}")
            raise
    
    async def execute_continuous_learning(
        self, 
        db: Session,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """
        継続学習の実行
        
        Args:
            db: データベースセッション
            force_update: 強制更新フラグ
            
        Returns:
            学習実行結果
        """
        learning_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            logger.info(f"継続学習開始 - ID: {learning_id}")
            
            if not force_update:
                trigger_check = await self.check_learning_trigger(db)
                if not trigger_check["should_trigger"]:
                    return {
                        "learning_id": learning_id,
                        "status": "skipped",
                        "reason": "学習実行条件を満たしていません",
                        "trigger_info": trigger_check
                    }
            
            # ベースライン品質の取得
            baseline_quality = await self._get_current_model_quality(db)
            
            # 新規データの取得と検証
            new_data = await self._collect_and_validate_new_data(db)
            
            # ベクトル化とクラスタリングの更新
            updated_vectors = await self._update_vector_clusters(db, new_data)
            
            # 代表例の再選出
            new_representatives = await self._reselect_representatives(db, updated_vectors)
            
            # テストスクリプトの生成と品質評価
            test_results = await self._generate_and_evaluate_test_scripts(
                db, new_representatives, baseline_quality
            )
            
            # 品質改善が確認された場合のモデル更新
            learning_results = await self._finalize_learning_results(
                db, learning_id, test_results, baseline_quality
            )
            
            # 学習履歴の記録
            await self._record_learning_history(db, learning_id, learning_results)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"継続学習完了 - ID: {learning_id}, 実行時間: {execution_time:.1f}秒")
            
            return {
                "learning_id": learning_id,
                "status": "completed",
                "execution_time": execution_time,
                "results": learning_results
            }
            
        except Exception as e:
            logger.error(f"継続学習でエラー - ID: {learning_id}: {e}")
            await self._record_learning_error(db, learning_id, str(e))
            raise
    
    async def _get_last_learning_date(self, db: Session) -> Optional[datetime]:
        """最後の学習実行日時を取得"""
        # 学習履歴テーブルから最新の実行日時を取得
        # 実装では学習履歴テーブルが必要
        return datetime.now() - timedelta(days=8)  # 仮の実装
    
    async def _get_new_conversations_since(
        self, 
        db: Session, 
        since_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """指定日時以降の新規会話を取得"""
        
        if not since_date:
            since_date = datetime.now() - timedelta(days=30)
        
        query = db.query(CounselingSession).filter(
            and_(
                CounselingSession.created_at >= since_date,
                CounselingSession.success_label.isnot(None)
            )
        ).order_by(desc(CounselingSession.created_at))
        
        sessions = query.all()
        
        return [
            {
                "session_id": session.id,
                "transcription": session.transcription,
                "success_label": session.success_label,
                "success_rate": session.success_rate,
                "created_at": session.created_at,
                "counselor_id": session.counselor_id
            }
            for session in sessions
        ]
    
    async def _analyze_quality_trend(self, db: Session) -> Dict[str, Any]:
        """品質メトリクスの推移分析"""
        
        # 過去の生成スクリプトの品質推移を分析
        # 実装では品質履歴テーブルが必要
        
        return {
            "trend": "stable",  # improving, stable, declining
            "recent_average_quality": 0.75,
            "quality_variance": 0.05,
            "decline_period_days": 0
        }
    
    def _evaluate_learning_trigger(
        self,
        new_conversations: List[Dict[str, Any]],
        quality_trend: Dict[str, Any],
        last_learning_date: Optional[datetime]
    ) -> Dict[str, Any]:
        """学習実行条件の評価"""
        
        trigger_reasons = []
        should_trigger = False
        
        # 新規データ量による判定
        if len(new_conversations) >= self.min_new_conversations:
            trigger_reasons.append(f"新規会話数が閾値を超過: {len(new_conversations)}件")
            should_trigger = True
        
        # 品質低下による判定
        if quality_trend["trend"] == "declining" and quality_trend["decline_period_days"] >= 3:
            trigger_reasons.append("品質低下が継続的に観測")
            should_trigger = True
        
        # 定期実行による判定
        if last_learning_date and (datetime.now() - last_learning_date).days >= self.learning_interval_days:
            trigger_reasons.append("定期実行間隔に達した")
            should_trigger = True
        
        # 初回実行判定
        if not last_learning_date:
            trigger_reasons.append("初回学習実行")
            should_trigger = True
        
        return {
            "trigger": should_trigger,
            "reasons": trigger_reasons
        }
    
    async def _get_current_model_quality(self, db: Session) -> Dict[str, float]:
        """現在のモデル品質ベースラインを取得"""
        
        # 現在の代表例でテストスクリプトを生成し品質を測定
        current_representatives = await self._get_current_representatives(db)
        
        if not current_representatives:
            return {"overall_quality": 0.5, "coverage": 0.5, "novelty": 0.5}
        
        # サンプル失敗会話での品質測定
        sample_failures = await self._get_sample_failure_conversations(db)
        
        quality_scores = []
        for failure in sample_failures[:5]:  # サンプル数を制限
            try:
                test_script = await self.script_service.generate_improvement_script({
                    "representatives": current_representatives,
                    "failure_mappings": [],
                    "failures": [failure]
                })
                
                quality_metrics = self.quality_analyzer.analyze_script_quality(
                    test_script["script"], 
                    {"success_patterns": current_representatives}
                )
                quality_scores.append(quality_metrics["overall_quality"])
                
            except Exception as e:
                logger.warning(f"ベースライン品質測定でエラー: {e}")
                continue
        
        baseline_quality = np.mean(quality_scores) if quality_scores else 0.5
        
        return {
            "overall_quality": baseline_quality,
            "coverage": baseline_quality * 0.9,  # 簡略化
            "novelty": baseline_quality * 1.1
        }
    
    async def _collect_and_validate_new_data(self, db: Session) -> Dict[str, List[Dict[str, Any]]]:
        """新規データの収集と検証"""
        
        last_learning_date = await self._get_last_learning_date(db)
        new_conversations = await self._get_new_conversations_since(db, last_learning_date)
        
        # データ品質の検証
        validated_conversations = []
        for conv in new_conversations:
            if self._validate_conversation_quality(conv):
                validated_conversations.append(conv)
        
        # 成功/失敗の分類
        success_conversations = [c for c in validated_conversations if c["success_label"]]
        failure_conversations = [c for c in validated_conversations if not c["success_label"]]
        
        logger.info(f"新規データ検証完了 - 成功: {len(success_conversations)}件, 失敗: {len(failure_conversations)}件")
        
        return {
            "success_conversations": success_conversations,
            "failure_conversations": failure_conversations,
            "total_validated": len(validated_conversations)
        }
    
    def _validate_conversation_quality(self, conversation: Dict[str, Any]) -> bool:
        """会話データの品質検証"""
        
        text = conversation.get("transcription", "")
        
        # 基本的な品質チェック
        if len(text.strip()) < 100:  # 最小文字数
            return False
        
        if conversation.get("success_rate") is None:
            return False
        
        # 文字化けや異常なパターンのチェック
        if len(set(text)) < 10:  # 文字種が少なすぎる
            return False
        
        return True
    
    async def _update_vector_clusters(
        self, 
        db: Session, 
        new_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """新規データを含めたベクトル化とクラスタリングの更新"""
        
        success_conversations = new_data["success_conversations"]
        
        if not success_conversations:
            return {"status": "no_new_success_data"}
        
        # 新規成功会話のベクトル化
        new_vectors = []
        for conv in success_conversations:
            try:
                vector = await self.embedding_service.embed_text(conv["transcription"])
                new_vectors.append({
                    "vector": vector,
                    "conversation": conv
                })
            except Exception as e:
                logger.warning(f"ベクトル化でエラー: {e}")
                continue
        
        # 既存ベクトルと結合してクラスタリング更新
        existing_vectors = await self._get_existing_vectors(db)
        all_vectors = existing_vectors + new_vectors
        
        # クラスタリング実行
        clustering_result = self.clustering_service.perform_clustering(
            [v["vector"] for v in all_vectors],
            method="kmeans"
        )
        
        return {
            "status": "updated",
            "new_vectors_count": len(new_vectors),
            "total_vectors_count": len(all_vectors),
            "clustering_result": clustering_result
        }
    
    async def _reselect_representatives(
        self, 
        db: Session, 
        updated_vectors: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """更新されたクラスタリング結果から代表例を再選出"""
        
        if updated_vectors["status"] != "updated":
            return await self._get_current_representatives(db)
        
        clustering_result = updated_vectors["clustering_result"]
        
        representatives = self.representative_service.extract_representatives(
            clustering_result["cluster_vectors"],
            clustering_result["cluster_labels"],
            [v["conversation"] for v in clustering_result["conversations"]]
        )
        
        return representatives
    
    async def _generate_and_evaluate_test_scripts(
        self,
        db: Session,
        new_representatives: List[Dict[str, Any]],
        baseline_quality: Dict[str, float]
    ) -> Dict[str, Any]:
        """テストスクリプトの生成と品質評価"""
        
        sample_failures = await self._get_sample_failure_conversations(db)
        
        test_results = []
        
        for failure in sample_failures[:3]:  # テスト数を制限
            try:
                # 新しい代表例でスクリプト生成
                test_script = await self.script_service.generate_improvement_script({
                    "representatives": new_representatives,
                    "failure_mappings": [],
                    "failures": [failure]
                })
                
                # 品質評価
                quality_metrics = self.quality_analyzer.analyze_script_quality(
                    test_script["script"],
                    {"success_patterns": new_representatives}
                )
                
                test_results.append({
                    "failure_id": failure.get("session_id"),
                    "script": test_script,
                    "quality_metrics": quality_metrics
                })
                
            except Exception as e:
                logger.warning(f"テストスクリプト生成でエラー: {e}")
                continue
        
        # 品質改善の評価
        if test_results:
            avg_new_quality = np.mean([r["quality_metrics"]["overall_quality"] for r in test_results])
            quality_improvement = avg_new_quality - baseline_quality["overall_quality"]
        else:
            avg_new_quality = 0.5
            quality_improvement = 0
        
        return {
            "test_scripts": test_results,
            "average_quality": avg_new_quality,
            "quality_improvement": quality_improvement,
            "improvement_confirmed": quality_improvement >= self.quality_improvement_threshold
        }
    
    async def _finalize_learning_results(
        self,
        db: Session,
        learning_id: str,
        test_results: Dict[str, Any],
        baseline_quality: Dict[str, float]
    ) -> Dict[str, Any]:
        """学習結果の確定処理"""
        
        if test_results["improvement_confirmed"]:
            # 改善が確認された場合、新しいモデルをデプロイ
            deployment_result = await self._deploy_updated_model(db, test_results)
            
            return {
                "action_taken": "model_updated",
                "quality_improvement": test_results["quality_improvement"],
                "baseline_quality": baseline_quality["overall_quality"],
                "new_quality": test_results["average_quality"],
                "deployment_result": deployment_result
            }
        else:
            return {
                "action_taken": "no_update",
                "quality_improvement": test_results["quality_improvement"],
                "reason": "品質改善が閾値を下回る",
                "threshold": self.quality_improvement_threshold
            }
    
    async def _deploy_updated_model(self, db: Session, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """更新されたモデルのデプロイ"""
        
        # 実際の実装では、新しい代表例をデータベースに保存し、
        # アクティブなモデルとして設定する処理が必要
        
        logger.info("更新されたモデルをデプロイ")
        
        return {
            "status": "deployed",
            "timestamp": datetime.now().isoformat(),
            "version": f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    
    async def _record_learning_history(
        self, 
        db: Session, 
        learning_id: str, 
        results: Dict[str, Any]
    ):
        """学習履歴の記録"""
        
        # 実装では学習履歴テーブルへの保存が必要
        logger.info(f"学習履歴を記録 - ID: {learning_id}")
    
    async def _record_learning_error(self, db: Session, learning_id: str, error_message: str):
        """学習エラーの記録"""
        
        logger.error(f"学習エラーを記録 - ID: {learning_id}, エラー: {error_message}")
    
    async def _get_current_representatives(self, db: Session) -> List[Dict[str, Any]]:
        """現在アクティブな代表例を取得"""
        
        # 仮の実装
        return [
            {
                "cluster_id": 1,
                "text": "サンプル成功会話1",
                "success_rate": 0.85,
                "characteristics": "丁寧な説明"
            },
            {
                "cluster_id": 2,
                "text": "サンプル成功会話2",
                "success_rate": 0.90,
                "characteristics": "顧客の不安解消"
            }
        ]
    
    async def _get_sample_failure_conversations(self, db: Session) -> List[Dict[str, Any]]:
        """サンプル失敗会話を取得"""
        
        query = db.query(CounselingSession).filter(
            CounselingSession.success_label == False
        ).limit(10)
        
        sessions = query.all()
        
        return [
            {
                "session_id": session.id,
                "transcription": session.transcription,
                "success_rate": session.success_rate or 0
            }
            for session in sessions
        ]
    
    async def _get_existing_vectors(self, db: Session) -> List[Dict[str, Any]]:
        """既存のベクトルデータを取得"""
        
        vectors = db.query(SuccessConversationVector).limit(100).all()
        
        return [
            {
                "vector": np.array(vector.embedding),
                "conversation": {
                    "session_id": vector.session_id,
                    "text": vector.chunk_text,
                    "metadata": vector.metadata
                }
            }
            for vector in vectors
        ]
    
    async def get_learning_status(self, db: Session) -> Dict[str, Any]:
        """継続学習の状況取得"""
        
        trigger_check = await self.check_learning_trigger(db)
        
        return {
            "continuous_learning_enabled": True,
            "last_learning_date": trigger_check["last_learning_date"],
            "next_scheduled_learning": trigger_check["next_scheduled_learning"],
            "new_conversations_count": trigger_check["new_conversations_count"],
            "quality_trend": trigger_check["quality_trend"],
            "learning_trigger_status": trigger_check["should_trigger"],
            "configuration": {
                "min_new_conversations": self.min_new_conversations,
                "quality_improvement_threshold": self.quality_improvement_threshold,
                "learning_interval_days": self.learning_interval_days
            }
        }