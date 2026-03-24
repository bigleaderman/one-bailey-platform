"""
시장 관련 비즈니스 로직
"""
from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.models import Prediction, MarketData
from typing import List
from app.schemas.market import (
    WeeklyTrend,
    MonthlyTrendResponse,
    MarketIndicator,
    MarketIndicatorsResponse,
    DateMarketResponse,
    TrendDataPoint,
    MarketTrendResponse,
    IndicatorCard,
    MarketTemperature,
    EconomicIndicatorCard,
    MarketSummaryResponse
)


class MarketService:
    """시장 데이터 서비스"""

    @staticmethod
    def get_market_for_date(db: Session, target_date: str) -> Optional[DateMarketResponse]:
        """특정 날짜의 시장 지표 조회"""
        row = db.query(MarketData)\
            .filter(
                MarketData.collection_meta['data_date'].astext <= target_date,
                or_(
                    MarketData.collection_meta['collection_type'].astext.is_(None),
                    MarketData.collection_meta['collection_type'].astext != 'closing_price',
                ),
                MarketData.qqq_price.isnot(None),
            )\
            .order_by(
                desc(MarketData.collection_meta['data_date'].astext),
                desc(MarketData.timestamp),
            )\
            .first()

        if not row:
            return None

        meta = row.collection_meta or {}

        return DateMarketResponse(
            qqq_price=float(row.qqq_price) if row.qqq_price else None,
            vix_level=float(row.vix_level) if row.vix_level else None,
            nq_future=float(row.nq_future) if row.nq_future else None,
            nq_change=float(row.nq_change) if row.nq_change else None,
            dxy_level=float(row.dxy_level) if row.dxy_level else None,
            dxy_change=float(row.dxy_change) if row.dxy_change else None,
            treasury_10y=float(row.treasury_10y) if row.treasury_10y else None,
            gold_price=float(row.gold_price) if row.gold_price else None,
            data_date=meta.get('data_date'),
        )

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

    # ============================================
    # 시장 현황 페이지용
    # ============================================

    @staticmethod
    def get_market_trend(db: Session, days: int = 30) -> MarketTrendResponse:
        """최근 N일 시계열 데이터 (차트용)"""
        rows = db.query(MarketData)\
            .filter(
                or_(
                    MarketData.collection_meta['collection_type'].astext.is_(None),
                    MarketData.collection_meta['collection_type'].astext != 'closing_price',
                ),
                MarketData.qqq_price.isnot(None),
            )\
            .order_by(desc(MarketData.timestamp))\
            .limit(days)\
            .all()

        data = []
        for row in reversed(rows):
            meta = row.collection_meta or {}
            data.append(TrendDataPoint(
                date=meta.get('data_date', ''),
                qqq_price=float(row.qqq_price) if row.qqq_price else None,
                vix_level=float(row.vix_level) if row.vix_level else None,
                treasury_10y=float(row.treasury_10y) if row.treasury_10y else None,
                dxy_level=float(row.dxy_level) if row.dxy_level else None,
                gold_price=float(row.gold_price) if row.gold_price else None,
                wti_oil=float(row.wti_oil) if row.wti_oil else None,
            ))

        return MarketTrendResponse(data=data, days=len(data))

    @staticmethod
    def get_market_summary(db: Session) -> MarketSummaryResponse:
        """시장 종합 상태 (온도계 + 지표 카드 + 경제 지표)"""
        # 최근 2일 데이터 (현재 + 전일)
        rows = db.query(MarketData)\
            .filter(
                or_(
                    MarketData.collection_meta['collection_type'].astext.is_(None),
                    MarketData.collection_meta['collection_type'].astext != 'closing_price',
                ),
                MarketData.qqq_price.isnot(None),
            )\
            .order_by(desc(MarketData.timestamp))\
            .limit(2)\
            .all()

        if not rows:
            raise ValueError("시장 데이터가 없습니다")

        current = rows[0]
        prev = rows[1] if len(rows) > 1 else None
        meta = current.collection_meta or {}

        # --- 지표 카드 4개 ---
        def _f(v):
            return float(v) if v is not None else None

        def _calc_change(curr_val, prev_val):
            if curr_val is not None and prev_val is not None and prev_val != 0:
                return round((float(curr_val) - float(prev_val)) / abs(float(prev_val)) * 100, 2)
            return None

        vix_val = _f(current.vix_level)
        vix_change = _f(current.vix_level) - _f(prev.vix_level) if prev and current.vix_level and prev.vix_level else None
        t10y_val = _f(current.treasury_10y)
        t10y_change = round(_f(current.treasury_10y) - _f(prev.treasury_10y), 3) if prev and current.treasury_10y and prev.treasury_10y else None
        dxy_val = _f(current.dxy_level)
        dxy_change = _calc_change(current.dxy_level, prev.dxy_level) if prev else None
        gold_val = _f(current.gold_price)
        gold_change = _calc_change(current.gold_price, prev.gold_price) if prev else None

        def _trend_info(change):
            if change is None:
                return "stable", "→ 데이터 없음"
            if change > 0:
                return "up", "↗ 상승중"
            elif change < 0:
                return "down", "↘ 하락중"
            return "stable", "→ 안정"

        # VIX 카드
        vix_trend, vix_trend_text = _trend_info(vix_change)
        if vix_val is not None:
            if vix_val < 15:
                vix_status, vix_desc = "good", "시장이 매우 안정적입니다. 투자자들이 낙관적이에요."
            elif vix_val < 20:
                vix_status, vix_desc = "good", "시장이 안정적입니다. 큰 변동 가능성이 낮아요."
            elif vix_val < 25:
                vix_status, vix_desc = "neutral", "약간의 불안감이 있지만 정상 범위입니다."
            elif vix_val < 30:
                vix_status, vix_desc = "bad", "변동성이 높습니다. 시장이 불안해하고 있어요."
            else:
                vix_status, vix_desc = "bad", "공포 수준입니다. 큰 변동이 예상됩니다."
        else:
            vix_status, vix_desc = "neutral", "데이터 없음"

        # 금리 카드
        t10y_trend, t10y_trend_text = _trend_info(t10y_change)
        if t10y_val is not None:
            if t10y_val < 3.5:
                t10y_status, t10y_desc = "good", "금리가 낮아 기술주에 유리한 환경입니다."
            elif t10y_val < 4.5:
                t10y_status, t10y_desc = "neutral", "금리가 보통 수준입니다. 시장 영향이 제한적이에요."
            else:
                t10y_status, t10y_desc = "bad", "금리가 높아 기술주에 부담이 됩니다."
        else:
            t10y_status, t10y_desc = "neutral", "데이터 없음"

        # 달러 카드
        dxy_trend, dxy_trend_text = _trend_info(dxy_change)
        if dxy_change is not None:
            if dxy_change < -0.3:
                dxy_status, dxy_desc = "good", "달러 약세로 위험자산 투자에 유리해요."
            elif dxy_change <= 0.3:
                dxy_status, dxy_desc = "neutral", "달러가 안정적입니다. 큰 영향은 없어요."
            else:
                dxy_status, dxy_desc = "bad", "달러 강세로 기술주에 부정적일 수 있어요."
        else:
            dxy_status, dxy_desc = "neutral", "데이터 없음"

        # 금 카드
        gold_trend, gold_trend_text = _trend_info(gold_change)
        if gold_change is not None:
            if gold_change > 1:
                gold_status, gold_desc = "bad", "금 가격 급등은 안전자산 선호를 의미해요."
            elif gold_change > 0:
                gold_status, gold_desc = "neutral", "금 가격이 소폭 올랐습니다."
            else:
                gold_status, gold_desc = "good", "금 가격 하락은 위험자산 선호를 의미해요."
        else:
            gold_status, gold_desc = "neutral", "데이터 없음"

        # HY 스프레드 카드
        hy_val = _f(current.hy_spread)
        hy_prev = _f(prev.hy_spread) if prev and hasattr(prev, 'hy_spread') else None
        hy_change = round(hy_val - hy_prev, 2) if hy_val is not None and hy_prev is not None else None
        hy_trend, hy_trend_text = _trend_info(hy_change)
        if hy_val is not None:
            if hy_val < 3.0:
                hy_status, hy_desc = "good", "신용 시장이 안정적입니다. 투자자들이 위험을 감수하고 있어요."
            elif hy_val < 4.5:
                hy_status, hy_desc = "neutral", "신용 스프레드가 보통 수준입니다."
            else:
                hy_status, hy_desc = "bad", "신용 시장이 불안합니다. 기업 부도 위험을 경계하고 있어요."
        else:
            hy_status, hy_desc = "neutral", "데이터 없음"

        # 실질금리 카드
        real_val = _f(current.real_rate_10y)
        real_prev = _f(prev.real_rate_10y) if prev and hasattr(prev, 'real_rate_10y') else None
        real_change = round(real_val - real_prev, 3) if real_val is not None and real_prev is not None else None
        real_trend, real_trend_text = _trend_info(real_change)
        if real_val is not None:
            if real_val < 1.0:
                real_status, real_desc = "good", "실질금리가 낮아 성장주/기술주에 유리한 환경입니다."
            elif real_val < 2.0:
                real_status, real_desc = "neutral", "실질금리가 보통 수준입니다."
            else:
                real_status, real_desc = "bad", "실질금리가 높아 기술주 밸류에이션에 부담됩니다."
        else:
            real_status, real_desc = "neutral", "데이터 없음"

        indicators = [
            IndicatorCard(
                name="vix", label="VIX 공포지수", value=vix_val,
                change=round(vix_change, 2) if vix_change else None,
                unit="", trend=vix_trend, trend_text=vix_trend_text,
                status=vix_status, description=vix_desc,
            ),
            IndicatorCard(
                name="treasury_10y", label="10년물 금리", value=t10y_val,
                change=t10y_change, unit="%",
                trend=t10y_trend, trend_text=t10y_trend_text,
                status=t10y_status, description=t10y_desc,
            ),
            IndicatorCard(
                name="hy_spread", label="HY 스프레드", value=hy_val,
                change=hy_change, unit="%",
                trend=hy_trend, trend_text=hy_trend_text,
                status=hy_status, description=hy_desc,
            ),
            IndicatorCard(
                name="real_rate", label="실질금리(10Y)", value=real_val,
                change=real_change, unit="%",
                trend=real_trend, trend_text=real_trend_text,
                status=real_status, description=real_desc,
            ),
            IndicatorCard(
                name="dxy", label="달러(DXY)", value=dxy_val,
                change=dxy_change, unit="",
                trend=dxy_trend, trend_text=dxy_trend_text,
                status=dxy_status, description=dxy_desc,
            ),
            IndicatorCard(
                name="gold", label="금 가격", value=gold_val,
                change=gold_change, unit="$",
                trend=gold_trend, trend_text=gold_trend_text,
                status=gold_status, description=gold_desc,
            ),
        ]

        # --- 시장 온도계 ---
        score = 50  # 기본 중립
        factors = 0

        if vix_val is not None:
            if vix_val < 15: score += 20
            elif vix_val < 20: score += 10
            elif vix_val < 25: score += 0
            elif vix_val < 30: score -= 10
            else: score -= 20
            factors += 1

        if t10y_val is not None:
            if t10y_val < 3.5: score += 10
            elif t10y_val < 4.5: score += 0
            else: score -= 10
            factors += 1

        if dxy_change is not None:
            if dxy_change < -0.3: score += 10
            elif dxy_change > 0.3: score -= 10
            factors += 1

        nq_change = _f(current.nq_change)
        if nq_change is not None:
            if nq_change > 1: score += 15
            elif nq_change > 0: score += 5
            elif nq_change > -1: score -= 5
            else: score -= 15
            factors += 1

        if hy_val is not None:
            if hy_val < 3.0: score += 10
            elif hy_val < 4.5: score += 0
            else: score -= 15
            factors += 1

        if real_val is not None:
            if real_val < 1.0: score += 10
            elif real_val < 2.0: score += 0
            else: score -= 10
            factors += 1

        score = max(0, min(100, score))

        if score >= 75:
            temp_label, temp_emoji = "탐욕", "🤑"
        elif score >= 60:
            temp_label, temp_emoji = "낙관", "😊"
        elif score >= 40:
            temp_label, temp_emoji = "중립", "😐"
        elif score >= 25:
            temp_label, temp_emoji = "불안", "😰"
        else:
            temp_label, temp_emoji = "공포", "😱"

        # 온도계 설명
        parts = []
        if vix_val is not None:
            if vix_val >= 25: parts.append("변동성이 높고")
            elif vix_val < 20: parts.append("시장이 안정적이고")
        if nq_change is not None:
            if nq_change > 0: parts.append("선물은 강세")
            else: parts.append("선물은 약세")
        if t10y_val is not None:
            if t10y_val >= 4.5: parts.append("금리 부담이 있고")
            else: parts.append("금리는 보통 수준이고")
        if hy_val is not None:
            if hy_val >= 4.5: parts.append("신용 시장이 불안합니다")
            elif hy_val < 3.0: parts.append("신용 시장은 안정적입니다")
            else: parts.append("신용 스프레드는 보통입니다")
        else:
            parts.append("시장을 종합적으로 판단합니다")

        temp_desc = ", ".join(parts) + "." if parts else "시장 데이터를 분석 중입니다."

        temperature = MarketTemperature(
            score=score, label=temp_label, emoji=temp_emoji, description=temp_desc,
        )

        # --- 경제 지표 ---
        from app.models.market_data import MarketData as MD
        from sqlalchemy import text as sql_text

        economic = []
        econ_config = [
            ("물가", "CPI", "소비자물가지수", "%"),
            ("물가", "Core_PCE", "근원 PCE", "%"),
            ("고용", "Unemployment", "실업률", "%"),
            ("고용", "NFP", "비농업 고용", "K"),
            ("성장", "GDP", "GDP 성장률", "%"),
        ]

        for category, name, label, unit in econ_config:
            row = db.execute(sql_text("""
                SELECT actual_value, mom_change, yoy_change
                FROM economic_indicators
                WHERE indicator_name = :name
                ORDER BY release_date DESC LIMIT 1
            """), {"name": name}).fetchone()

            if row:
                val = float(row[0]) if row[0] else None
                yoy = float(row[2]) if row[2] else None
                change = float(row[1]) if row[1] else None

                # 쉬운 해설
                if name == "CPI":
                    econ_desc = f"물가가 전년 대비 {yoy:+.1f}% 변동" if yoy else "물가 데이터"
                    if yoy and yoy > 3: econ_desc += " (높은 수준)"
                    elif yoy and yoy < 2.5: econ_desc += " (안정적)"
                elif name == "Core_PCE":
                    econ_desc = f"Fed 목표(2%) 대비 {yoy:.1f}% 수준" if yoy else "핵심 물가 데이터"
                elif name == "Unemployment":
                    econ_desc = f"실업률 {val:.1f}%" if val else "고용 데이터"
                    if val and val < 4: econ_desc += " (양호)"
                    elif val and val >= 5: econ_desc += " (악화)"
                elif name == "NFP":
                    econ_desc = f"전월 대비 {change:+.0f}K 변동" if change else "고용 데이터"
                elif name == "GDP":
                    econ_desc = f"경제 성장률 {yoy:+.1f}%" if yoy else "성장 데이터"
                    if yoy and yoy > 2: econ_desc += " (양호)"
                    elif yoy and yoy < 0: econ_desc += " (위축)"
                else:
                    econ_desc = ""

                display_val = yoy if name in ("CPI", "Core_PCE", "GDP") else val

                economic.append(EconomicIndicatorCard(
                    category=category, name=name, label=label,
                    value=display_val, change=change, unit=unit, description=econ_desc,
                ))

        return MarketSummaryResponse(
            temperature=temperature,
            indicators=indicators,
            economic=economic,
            updated_at=meta.get('data_date', ''),
        )

    # 시장 지표 해설 데이터
    MARKET_EXPLAINER = {
        'vix': {
            'label': 'VIX 공포지수',
            'field': 'vix_level',
            'unit': '',
            'what_is': '향후 30일간 S&P 500의 예상 변동성을 나타내는 지수입니다. "공포 지수"라고도 불립니다.',
            'why_matters': 'VIX가 높으면 시장이 불안하다는 뜻입니다. 20 이하면 안정적, 30 이상이면 공포 수준으로 큰 변동이 예상됩니다.',
            'thresholds': [(15, 'good', '매우 안정'), (20, 'good', '안정'), (25, 'neutral', '보통'), (30, 'bad', '불안'), (999, 'bad', '공포')],
        },
        'treasury_10y': {
            'label': '10년물 국채 금리',
            'field': 'treasury_10y',
            'unit': '%',
            'what_is': '미국 정부가 10년간 빌리는 돈에 대한 이자율입니다. 시장의 장기 금리 기대를 반영합니다.',
            'why_matters': '금리가 오르면 미래 수익의 현재 가치가 줄어들어 기술주 같은 성장주에 부정적입니다.',
            'thresholds': [(3.5, 'good', '낮음'), (4.5, 'neutral', '보통'), (999, 'bad', '높음')],
        },
        'hy_spread': {
            'label': 'HY 스프레드 (하이일드)',
            'field': 'hy_spread',
            'unit': '%',
            'what_is': '고위험 회사채와 국채의 금리 차이입니다. 기업의 부도 위험에 대한 시장의 걱정을 보여줍니다.',
            'why_matters': 'HY 스프레드가 급등하면 금융 위기의 전조일 수 있습니다. 2020년 코로나, 2022년 하락장 때 모두 급등했습니다.',
            'thresholds': [(3.0, 'good', '안정'), (4.5, 'neutral', '보통'), (999, 'bad', '위험')],
        },
        'real_rate': {
            'label': '실질금리 (10Y TIPS)',
            'field': 'real_rate_10y',
            'unit': '%',
            'what_is': '명목금리에서 인플레이션 기대를 뺀 실질적인 자금 비용입니다.',
            'why_matters': '기술주 밸류에이션에 가장 직접적인 영향을 미칩니다. 같은 명목금리라도 실질금리가 다르면 시장 반응이 완전히 다릅니다.',
            'thresholds': [(1.0, 'good', '낮음'), (2.0, 'neutral', '보통'), (999, 'bad', '높음')],
        },
        'dxy': {
            'label': '달러 인덱스 (DXY)',
            'field': 'dxy_level',
            'unit': '',
            'what_is': '유로, 엔 등 주요 통화 대비 달러의 가치를 측정하는 지수입니다.',
            'why_matters': '달러가 강해지면 미국 기업의 해외 수익이 줄고, 신흥국 자금이 빠져나가 글로벌 위험자산에 부정적입니다.',
            'thresholds': None,  # 변화율 기반 판단
        },
        'gold': {
            'label': '금 가격',
            'field': 'gold_price',
            'unit': '$',
            'what_is': '안전자산의 대표격인 금의 국제 시세입니다.',
            'why_matters': '금 가격이 급등하면 투자자들이 위험을 회피하고 안전자산으로 이동하는 신호입니다. 주식에 부정적일 수 있습니다.',
            'thresholds': None,
        },
    }

    # 경제 지표 해설 데이터
    ECON_EXPLAINER = {
        'CPI': {
            'label': '소비자물가지수 (CPI)',
            'unit': '%',
            'what_is': '우리가 일상에서 사는 물건과 서비스의 평균 가격 변화를 측정하는 지수입니다.',
            'why_matters': 'CPI가 오르면 물가가 오르는 것(인플레이션)이고, Fed가 금리를 올릴 수 있어 주식에 부정적입니다.',
        },
        'Core_CPI': {
            'label': '근원 소비자물가 (Core CPI)',
            'unit': '%',
            'what_is': '변동이 큰 식품과 에너지를 제외한 물가 지수입니다. 물가의 기조적 흐름을 보여줍니다.',
            'why_matters': 'Fed가 통화정책 결정 시 가장 중요하게 보는 지표 중 하나입니다.',
        },
        'PCE': {
            'label': 'PCE 물가지수',
            'unit': '%',
            'what_is': '개인소비지출(PCE) 기반 물가 지수로, 소비 패턴 변화를 반영합니다.',
            'why_matters': 'Fed가 인플레이션 목표(2%)를 정할 때 공식적으로 사용하는 지표입니다.',
        },
        'Core_PCE': {
            'label': '근원 PCE 물가지수',
            'unit': '%',
            'what_is': '식품·에너지를 제외한 PCE 물가입니다. Fed의 공식 인플레이션 목표 지표입니다.',
            'why_matters': '이 수치가 2%에 가까울수록 금리 인하 가능성이 높아져 주식에 긍정적입니다.',
        },
        'NFP': {
            'label': '비농업 고용 (NFP)',
            'unit': 'K',
            'what_is': '농업을 제외한 미국의 월간 신규 일자리 수입니다.',
            'why_matters': '고용이 강하면 경제가 좋다는 뜻이지만, 너무 강하면 Fed가 금리를 올려 주식에 부정적일 수 있습니다.',
        },
        'Unemployment': {
            'label': '실업률',
            'unit': '%',
            'what_is': '일할 의사가 있는 사람 중 일자리를 찾지 못한 비율입니다.',
            'why_matters': '실업률이 낮으면 경제가 건강하다는 신호이지만, 너무 낮으면 임금 상승 → 인플레이션 우려가 생깁니다.',
        },
        'Industrial_Production': {
            'label': '산업생산지수',
            'unit': 'index',
            'what_is': '공장, 광업, 전기·가스 분야의 생산량을 측정한 지수입니다.',
            'why_matters': '제조업 경기를 직접 보여주는 지표로, 하락하면 경기 둔화 신호입니다.',
        },
        'Consumer_Sentiment': {
            'label': '소비자심리지수',
            'unit': 'index',
            'what_is': '미시간대학이 소비자 설문으로 측정하는 경기 체감 지수입니다.',
            'why_matters': '소비자가 경제를 비관적으로 보면 소비가 줄어 기업 실적과 주가에 부정적입니다.',
        },
        'GDP': {
            'label': 'GDP (국내총생산)',
            'unit': '%',
            'what_is': '미국 경제가 생산한 모든 재화와 서비스의 총 가치입니다. 분기별로 발표됩니다.',
            'why_matters': 'GDP 성장률이 높으면 경제가 잘 돌아가는 것이고, 마이너스면 경기 침체 우려가 커집니다.',
        },
        'Real_GDP': {
            'label': '실질 GDP',
            'unit': '%',
            'what_is': '물가 변동을 제거한 실질적인 경제 성장을 보여주는 GDP입니다.',
            'why_matters': '인플레이션을 빼고 순수한 경제 성장만 보여줘서 경제 건강 상태의 핵심 지표입니다.',
        },
    }

    @staticmethod
    def get_economic_detail(db: Session, indicator_name: str):
        """경제 지표 상세 정보 + 시계열"""
        from app.schemas.market import EconomicDetailResponse, EconomicHistoryPoint
        from sqlalchemy import text as sql_text
        import math

        def _safe_float(v):
            """NaN/Inf를 None으로 변환"""
            if v is None:
                return None
            f = float(v)
            if math.isnan(f) or math.isinf(f):
                return None
            return f

        explainer = MarketService.ECON_EXPLAINER.get(indicator_name)
        if not explainer:
            return None

        # 시계열 데이터 (최근 3년)
        rows = db.execute(sql_text("""
            SELECT release_date, actual_value, yoy_change
            FROM economic_indicators
            WHERE indicator_name = :name
            ORDER BY release_date
        """), {"name": indicator_name}).fetchall()

        if not rows:
            return None

        history = [
            EconomicHistoryPoint(
                date=str(r[0]),
                value=_safe_float(r[1]),
                yoy_change=_safe_float(r[2]),
            )
            for r in rows
        ]

        # 최신값
        latest = rows[-1]
        current_value = _safe_float(latest[1])
        current_yoy = _safe_float(latest[2])

        # 상태 판단 + 현재 의미 해설
        if indicator_name in ('CPI', 'Core_CPI', 'PCE', 'Core_PCE'):
            if current_yoy is not None:
                if current_yoy > 3.5:
                    status, status_text = "bad", "높음"
                    meaning = f"전년 대비 {current_yoy:.1f}% 상승으로 인플레이션이 높은 수준입니다. Fed의 금리 인상 가능성이 있어 기술주에 부정적입니다."
                elif current_yoy > 2.5:
                    status, status_text = "neutral", "보통"
                    meaning = f"전년 대비 {current_yoy:.1f}% 상승으로 물가가 다소 높지만 관리 가능한 수준입니다."
                else:
                    status, status_text = "good", "안정"
                    meaning = f"전년 대비 {current_yoy:.1f}% 상승으로 물가가 안정적입니다. 금리 인하 기대감이 커져 주식에 긍정적입니다."
            else:
                status, status_text, meaning = "neutral", "데이터 없음", "최신 데이터가 없습니다."

        elif indicator_name == 'Unemployment':
            if current_value is not None:
                if current_value < 4.0:
                    status, status_text = "good", "양호"
                    meaning = f"실업률 {current_value:.1f}%로 고용시장이 매우 건강합니다."
                elif current_value < 5.0:
                    status, status_text = "neutral", "보통"
                    meaning = f"실업률 {current_value:.1f}%로 고용시장이 무난한 수준입니다."
                else:
                    status, status_text = "bad", "악화"
                    meaning = f"실업률 {current_value:.1f}%로 고용시장이 약화되고 있습니다. 경기 둔화 우려가 있습니다."
            else:
                status, status_text, meaning = "neutral", "데이터 없음", ""

        elif indicator_name == 'NFP':
            mom = float(rows[-1][2]) if len(rows) > 0 and rows[-1][2] else None
            if mom is not None:
                # mom_change는 economic_indicators에서 가져와야 하지만, yoy_change 자리에 있을 수 있음
                pass
            status, status_text = "neutral", "참고"
            meaning = "고용 증가가 지속되면 경제가 건강하다는 신호입니다."
            if current_value:
                meaning = f"현재 비농업 고용자 수 {current_value/1000:.0f}K입니다. " + meaning

        elif indicator_name in ('GDP', 'Real_GDP'):
            if current_yoy is not None:
                if current_yoy > 2:
                    status, status_text = "good", "양호"
                    meaning = f"경제 성장률 {current_yoy:.1f}%로 건강한 성장세를 보이고 있습니다."
                elif current_yoy > 0:
                    status, status_text = "neutral", "둔화"
                    meaning = f"경제 성장률 {current_yoy:.1f}%로 성장세가 다소 둔화되었습니다."
                else:
                    status, status_text = "bad", "위축"
                    meaning = f"경제 성장률 {current_yoy:.1f}%로 경기 침체 우려가 있습니다."
            else:
                status, status_text, meaning = "neutral", "데이터 없음", ""

        else:
            status, status_text = "neutral", "참고"
            meaning = "해당 지표를 확인하세요."

        # 표시 값 결정
        display_value = current_yoy if indicator_name in ('CPI', 'Core_CPI', 'PCE', 'Core_PCE', 'GDP', 'Real_GDP') else current_value

        return EconomicDetailResponse(
            name=indicator_name,
            label=explainer['label'],
            current_value=display_value,
            current_yoy=current_yoy,
            unit=explainer['unit'],
            status=status,
            status_text=status_text,
            what_is=explainer['what_is'],
            why_matters=explainer['why_matters'],
            current_meaning=meaning,
            history=history,
        )

    @staticmethod
    def get_market_indicator_detail(db: Session, indicator_name: str):
        """시장 지표 상세 (해설 + 30일 시계열)"""
        from app.schemas.market import MarketIndicatorDetailResponse

        explainer = MarketService.MARKET_EXPLAINER.get(indicator_name)
        if not explainer:
            return None

        field = explainer['field']

        # 최근 30일 시계열
        rows = db.query(MarketData)\
            .filter(
                or_(
                    MarketData.collection_meta['collection_type'].astext.is_(None),
                    MarketData.collection_meta['collection_type'].astext != 'closing_price',
                ),
                MarketData.qqq_price.isnot(None),
            )\
            .order_by(desc(MarketData.timestamp))\
            .limit(30)\
            .all()

        if not rows:
            return None

        history = []
        for row in reversed(rows):
            meta = row.collection_meta or {}
            val = getattr(row, field, None)
            history.append(TrendDataPoint(
                date=meta.get('data_date', ''),
                qqq_price=float(row.qqq_price) if row.qqq_price else None,
                vix_level=float(row.vix_level) if row.vix_level else None,
                treasury_10y=float(row.treasury_10y) if row.treasury_10y else None,
                dxy_level=float(row.dxy_level) if row.dxy_level else None,
                gold_price=float(row.gold_price) if row.gold_price else None,
                wti_oil=float(row.wti_oil) if row.wti_oil else None,
            ))

        # 최신값
        current = rows[0]
        current_val = float(getattr(current, field)) if getattr(current, field, None) is not None else None

        # 전일 대비 변화
        prev = rows[1] if len(rows) > 1 else None
        prev_val = float(getattr(prev, field)) if prev and getattr(prev, field, None) is not None else None
        change = round(current_val - prev_val, 3) if current_val is not None and prev_val is not None else None

        # 상태 판단
        thresholds = explainer.get('thresholds')
        if thresholds and current_val is not None:
            status, status_text = "neutral", "보통"
            for threshold, st, st_text in thresholds:
                if current_val < threshold:
                    status, status_text = st, st_text
                    break
        elif indicator_name == 'dxy':
            if change is not None:
                if change < -0.3: status, status_text = "good", "약세"
                elif change > 0.3: status, status_text = "bad", "강세"
                else: status, status_text = "neutral", "보합"
            else:
                status, status_text = "neutral", "데이터 없음"
        elif indicator_name == 'gold':
            if change is not None:
                if change > 1: status, status_text = "bad", "급등"
                elif change > 0: status, status_text = "neutral", "상승"
                else: status, status_text = "good", "하락"
            else:
                status, status_text = "neutral", "데이터 없음"
        else:
            status, status_text = "neutral", "참고"

        # 현재 의미 해설
        meanings = {
            'vix': lambda v: f"VIX {v:.1f}로 {'시장이 매우 불안합니다. 큰 변동에 대비하세요.' if v >= 30 else '변동성이 높은 상태입니다.' if v >= 25 else '시장이 비교적 안정적입니다.' if v >= 20 else '시장이 매우 안정적입니다.'}",
            'treasury_10y': lambda v: f"10년물 금리 {v:.3f}%로 {'기술주에 상당한 부담입니다.' if v >= 4.5 else '보통 수준으로 큰 영향은 제한적입니다.' if v >= 3.5 else '낮은 수준으로 성장주에 유리합니다.'}",
            'hy_spread': lambda v: f"HY 스프레드 {v:.2f}%로 {'신용 시장에 심각한 스트레스가 있습니다.' if v >= 4.5 else '보통 수준으로 큰 우려는 없습니다.' if v >= 3.0 else '신용 시장이 안정적이고 투자 심리가 양호합니다.'}",
            'real_rate': lambda v: f"실질금리 {v:.3f}%로 {'기술주 밸류에이션에 큰 부담이 됩니다.' if v >= 2.0 else '보통 수준입니다.' if v >= 1.0 else '성장주/기술주에 유리한 환경입니다.'}",
            'dxy': lambda v: f"달러 지수가 {'강세' if change and change > 0 else '약세'} 흐름으로, {'위험자산에 부정적' if change and change > 0.3 else '위험자산 투자에 유리' if change and change < -0.3 else '큰 영향은 없는'} 환경입니다.",
            'gold': lambda v: f"금 가격 ${v:,.0f}로 {'안전자산 수요가 급증하고 있습니다.' if change and change > 1 else '소폭 상승세입니다.' if change and change > 0 else '위험자산 선호가 나타나고 있습니다.'}",
        }

        meaning_func = meanings.get(indicator_name)
        current_meaning = meaning_func(current_val) if meaning_func and current_val is not None else "데이터를 확인하세요."

        return MarketIndicatorDetailResponse(
            name=indicator_name,
            label=explainer['label'],
            current_value=current_val,
            change=change,
            unit=explainer['unit'],
            status=status,
            status_text=status_text,
            what_is=explainer['what_is'],
            why_matters=explainer['why_matters'],
            current_meaning=current_meaning,
            history=history,
        )
