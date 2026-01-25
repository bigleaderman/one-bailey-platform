from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List

class PredictionBase(BaseModel):
    model_config = ConfigDict(json_encoders={Decimal: float})
    
    prediction_date: date
    direction: str = Field(..., pattern="^(UP|DOWN)$")
    confidence: Decimal = Field(..., ge=0.5, le=0.99)
    actual_direction: Optional[str] = None
    actual_change: Optional[Decimal] = None
    key_factors: Optional[List[str]] = None  # Dict → List[str]
    risk_factors: Optional[List[str]] = None  # Dict → List[str]
    summary: Optional[str] = None
    llm_response: Optional[Dict[str, Any]] = None

class PredictionCreate(PredictionBase):
    pass

class PredictionUpdate(PredictionBase):
    pass

class PredictionResponse(PredictionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}

class Prediction(PredictionBase):
    id: int
    created_at: str

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}

class PredictionsList(BaseModel):
    predictions: List[Prediction]