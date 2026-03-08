"""
예측 관련 비즈니스 로직
"""
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Prediction
from app.schemas.prediction import (
    TodayPredictionResponse,
    PredictionResponse,
    PredictionHistoryItem,
    PredictionHistoryResponse
)


class PredictionService:
    """예측 서비스"""
    
    # 방향 텍스트 매핑
    DIRECTION_MAP = {
        "UP": "상승 예상",
        "DOWN": "하락 예상",
        "HOLD": "보합 예상"
    }
    
    DIRECTION_TEXT_MAP = {
        "UP": "상승",
        "DOWN": "하락",
        "HOLD": "보합"
    }
    
    @staticmethod
    def get_today_prediction(db: Session) -> Optional[TodayPredictionResponse]:
        """
        오늘의 예측 조회
        - 오늘 또는 가장 최근 예측 반환
        """
        today = date.today()
        
        prediction = db.query(Prediction)\
            .filter(Prediction.prediction_date <= today)\
            .order_by(desc(Prediction.prediction_date))\
            .first()
        
        if not prediction:
            return None
        
        # 신뢰도 계산
        confidence_percent = int(prediction.confidence * 100) if prediction.confidence <= 1 else int(prediction.confidence)
        confidence_stars = min(5, max(1, int(confidence_percent / 20)))
        
        # factors 처리
        key_factors = prediction.key_factors if isinstance(prediction.key_factors, list) else []
        risk_factors = prediction.risk_factors if isinstance(prediction.risk_factors, list) else []
        
        return TodayPredictionResponse(
            date=prediction.prediction_date.strftime("%Y년 %m월 %d일"),
            direction=prediction.direction,
            direction_text=PredictionService.DIRECTION_MAP.get(prediction.direction, prediction.direction),
            confidence=prediction.confidence,
            confidence_percent=confidence_percent,
            confidence_stars=confidence_stars,
            summary=prediction.summary or "예측 요약이 없습니다.",
            key_factors=key_factors,
            risk_factors=risk_factors
        )
    
    @staticmethod
    def get_predictions(db: Session, skip: int = 0, limit: int = 10) -> List[Prediction]:
        """예측 목록 조회"""
        return db.query(Prediction)\
            .order_by(desc(Prediction.prediction_date))\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_prediction_by_id(db: Session, prediction_id: int) -> Optional[Prediction]:
        """특정 예측 조회"""
        return db.query(Prediction)\
            .filter(Prediction.id == prediction_id)\
            .first()
    
    @staticmethod
    def get_prediction_history(db: Session, days: int = 7) -> PredictionHistoryResponse:
        """
        최근 예측 기록 + 적중률
        """
        today = date.today()
        start_date = today - timedelta(days=days + 10)
        
        predictions = db.query(Prediction)\
            .filter(Prediction.prediction_date <= today)\
            .filter(Prediction.prediction_date >= start_date)\
            .order_by(desc(Prediction.prediction_date))\
            .limit(days + 5)\
            .all()
        
        history = []
        correct_count = 0
        total_count = 0
        
        for p in predictions[:days]:
            is_correct = None
            if p.actual_direction:
                is_correct = (p.direction == p.actual_direction)
                total_count += 1
                if is_correct:
                    correct_count += 1
            
            history.append(PredictionHistoryItem(
                date=p.prediction_date.strftime("%Y-%m-%d"),
                date_short=p.prediction_date.strftime("%-m/%d"),
                direction=p.direction,
                direction_text=PredictionService.DIRECTION_TEXT_MAP.get(p.direction, p.direction),
                actual_direction=p.actual_direction,
                actual_change=p.actual_change,
                is_correct=is_correct
            ))
        
        # 적중률 계산
        accuracy = round((correct_count / total_count * 100), 1) if total_count > 0 else 0
        
        # 30일 적중률
        all_with_result = db.query(Prediction)\
            .filter(Prediction.actual_direction.isnot(None))\
            .order_by(desc(Prediction.prediction_date))\
            .limit(30)\
            .all()
        
        total_30 = len(all_with_result)
        correct_30 = sum(1 for p in all_with_result if p.direction == p.actual_direction)
        accuracy_30 = round((correct_30 / total_30 * 100), 1) if total_30 > 0 else 0
        
        return PredictionHistoryResponse(
            history=history,
            stats={
                "days": days,
                "total": total_count,
                "correct": correct_count,
                "accuracy": accuracy,
                "accuracy_30d": accuracy_30,
                "total_30d": total_30,
                "correct_30d": correct_30
            }
        )
