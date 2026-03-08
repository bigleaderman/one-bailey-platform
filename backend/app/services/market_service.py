"""
시장 관련 비즈니스 로직
"""
from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Prediction, MarketData
from app.schemas.market import (
    WeeklyTrend,
    MonthlyTrendResponse,
    MarketIndicator,
    MarketIndicatorsResponse
)


class MarketService:
    """시장 데이터 서비스"""
    
    @staticmethod
    def get_monthly_trend(db: Session) -> MonthlyTrendResponse:
        """
        최근 4주 시장 흐름
        - 이번주 포함 최근 4주 데이터 표시
        - 복리 방식으로 주간 변동률 계산
        """
        today = date.today()
        
        # 이번 주 월요일 찾기
        days_since_monday = today.weekday()
        this_monday = today - timedelta(days=days_since_monday)
        
        weeks_data = []
        
        # 최근 4주 데이터 조회 (이번주 포함)
        for i in range(4):
            # i=0: 3주 전, i=1: 2주 전, i=2: 1주 전, i=3: 이번주
            week_offset = 3 - i
            week_monday = this_monday - timedelta(weeks=week_offset)
            week_sunday = week_monday + timedelta(days=6)
            
            # 해당 주의 예측 데이터 조회 (날짜순 정렬)
            predictions = db.query(Prediction).filter(
                Prediction.prediction_date >= week_monday,
                Prediction.prediction_date <= week_sunday,
                Prediction.actual_change.isnot(None)
            ).order_by(Prediction.prediction_date).all()
            
            # 주간 총 변동률 계산 (복리 방식)
            cumulative = 1.0
            for p in predictions:
                if p.actual_change is not None:
                    cumulative *= (1 + p.actual_change / 100)
            
            total_change = (cumulative - 1) * 100
            
            # 방향 결정
            direction, direction_text = MarketService._determine_direction(total_change)
            
            # 이번 주 여부
            is_current_week = (week_offset == 0)
            
            # 주차 라벨
            week_number = i + 1
            week_label = "이번주" if is_current_week else f"{week_number}주차"
            
            # 요약 생성
            summary = MarketService._generate_summary(
                db, week_monday, is_current_week, predictions, 
                total_change, direction, direction_text
            )
            
            # 이번주면 방향 업데이트
            if is_current_week:
                direction, direction_text = MarketService._get_current_week_direction(
                    db, week_monday, predictions, total_change
                )
            
            weeks_data.append(WeeklyTrend(
                week_number=week_number,
                week_label=week_label,
                start_date=week_monday.strftime("%-m/%d"),
                end_date=week_sunday.strftime("%-m/%d"),
                direction=direction,
                direction_text=direction_text,
                total_change=round(total_change, 2),
                summary=summary,
                is_current_week=is_current_week
            ))
        
        return MonthlyTrendResponse(
            month=f"{today.month}월",
            weeks=weeks_data
        )
    
    @staticmethod
    def _determine_direction(total_change: float) -> tuple:
        """변동률에 따른 방향 결정"""
        if total_change > 0.5:
            return "UP", "상승"
        elif total_change < -0.5:
            return "DOWN", "하락"
        else:
            return "HOLD", "보합"
    
    @staticmethod
    def _get_current_week_direction(db: Session, week_monday: date, 
                                     predictions: list, total_change: float) -> tuple:
        """이번 주 방향 결정 (실제 데이터 or 예측)"""
        if predictions:
            # 실제 데이터 기반
            if total_change > 0.5:
                return "UP", "상승 중"
            elif total_change < -0.5:
                return "DOWN", "하락 중"
            else:
                return "HOLD", "보합 중"
        else:
            # 예측 기반
            latest = db.query(Prediction)\
                .filter(Prediction.prediction_date >= week_monday)\
                .order_by(desc(Prediction.prediction_date))\
                .first()
            
            if latest:
                direction_map = {
                    "UP": "상승 예상",
                    "DOWN": "하락 예상",
                    "HOLD": "보합 예상"
                }
                return latest.direction, direction_map.get(latest.direction, "예상")
            
            return "HOLD", "데이터 없음"
    
    @staticmethod
    def _generate_summary(db: Session, week_monday: date, is_current_week: bool,
                          predictions: list, total_change: float,
                          direction: str, direction_text: str) -> str:
        """주간 요약 생성"""
        if is_current_week:
            latest = db.query(Prediction)\
                .filter(Prediction.prediction_date >= week_monday)\
                .order_by(desc(Prediction.prediction_date))\
                .first()
            
            if predictions:
                if latest and latest.summary:
                    summary = latest.summary.split('.')[0] + "."
                    return summary[:30] + "..." if len(summary) > 30 else summary
                return f"현재까지 {total_change:+.2f}% 변동"
            else:
                if latest and latest.summary:
                    summary = latest.summary.split('.')[0] + "."
                    return summary[:30] + "..." if len(summary) > 30 else summary
                return "예측 데이터 없음"
        else:
            summary_map = {
                "UP": "시장 상승세 기록",
                "DOWN": "시장 하락세 기록",
                "HOLD": "시장 보합세 유지"
            }
            return summary_map.get(direction, "시장 보합세 유지")
    
    @staticmethod
    def get_market_indicators(db: Session) -> MarketIndicatorsResponse:
        """
        주요 시장 지표 조회
        - VIX, 나스닥 선물, 금리 등 6개 지표
        """
        market = db.query(MarketData)\
            .order_by(desc(MarketData.timestamp))\
            .first()
        
        if not market:
            return MarketIndicatorsResponse(
                date=date.today().strftime("%Y년 %m월 %d일"),
                indicators=[]
            )
        
        indicators = []
        
        # 1. VIX
        if market.vix_level:
            status, status_text = MarketService._get_vix_status(market.vix_level)
            indicators.append(MarketIndicator(
                name="vix",
                label="VIX 공포지수",
                value=round(market.vix_level, 2),
                unit="",
                status=status,
                status_text=status_text
            ))
        
        # 2. 나스닥 선물
        if market.nq_change is not None:
            status, status_text = MarketService._get_change_status(market.nq_change)
            indicators.append(MarketIndicator(
                name="nq_change",
                label="나스닥 선물",
                value=round(market.nq_change, 2),
                unit="%",
                status=status,
                status_text=status_text
            ))
        
        # 3. 10년물 금리
        if market.treasury_10y:
            status, status_text = MarketService._get_treasury_status(market.treasury_10y)
            indicators.append(MarketIndicator(
                name="treasury_10y",
                label="10Y 금리",
                value=round(market.treasury_10y, 3),
                unit="%",
                status=status,
                status_text=status_text
            ))
        
        # 4. 금리차
        if market.spread_2_10y is not None:
            status, status_text = MarketService._get_spread_status(market.spread_2_10y)
            indicators.append(MarketIndicator(
                name="spread_2_10y",
                label="금리차 2-10Y",
                value=round(market.spread_2_10y, 3),
                unit="%",
                status=status,
                status_text=status_text
            ))
        
        # 5. 달러 인덱스
        if market.dxy_level:
            dxy_change = market.dxy_change or 0
            status, status_text = MarketService._get_dxy_status(dxy_change)
            indicators.append(MarketIndicator(
                name="dxy",
                label="달러 인덱스",
                value=round(market.dxy_level, 2),
                unit="",
                status=status,
                status_text=status_text
            ))
        
        # 6. 금
        if market.gold_price:
            indicators.append(MarketIndicator(
                name="gold",
                label="금",
                value=round(market.gold_price, 2),
                unit="$",
                status="neutral",
                status_text=""
            ))
        
        return MarketIndicatorsResponse(
            date=market.timestamp.strftime("%Y년 %m월 %d일"),
            indicators=indicators
        )
    
    @staticmethod
    def _get_vix_status(value: float) -> tuple:
        if value < 15:
            return "good", "낙관"
        elif value <= 25:
            return "neutral", "중립"
        return "bad", "공포"
    
    @staticmethod
    def _get_change_status(value: float) -> tuple:
        if value > 0.3:
            return "good", "상승"
        elif value >= -0.3:
            return "neutral", "보합"
        return "bad", "하락"
    
    @staticmethod
    def _get_treasury_status(value: float) -> tuple:
        if value < 4.0:
            return "good", "안정"
        elif value <= 4.5:
            return "neutral", "보통"
        return "bad", "높음"
    
    @staticmethod
    def _get_spread_status(value: float) -> tuple:
        if value > 0.5:
            return "good", "정상"
        elif value >= 0:
            return "neutral", "주의"
        return "bad", "역전"
    
    @staticmethod
    def _get_dxy_status(change: float) -> tuple:
        if change < -0.3:
            return "good", "약세"
        elif change <= 0.3:
            return "neutral", "보합"
        return "bad", "강세"
