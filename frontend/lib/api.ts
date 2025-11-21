const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Prediction {
  id: number;
  prediction_date: string;
  direction: 'UP' | 'DOWN';
  confidence: number;
  actual_direction?: string;
  actual_change?: number;
  key_factors?: string[];
  risk_factors?: string[];
  summary?: string;
  created_at: string;
}

// Mock 데이터 (개발/테스트용)
const mockPrediction: Prediction = {
  id: 1,
  prediction_date: new Date().toISOString().split('T')[0],
  direction: 'UP',
  confidence: 0.80,
  key_factors: [
    '나스닥 선물 강세',
    '달러 약세로 위험자산 선호',
    '양의 2-10 스프레드 유지'
  ],
  risk_factors: [
    '높은 VIX 수준',
    '반도체 섹터 부진'
  ],
  summary: '글린 통걸 기대감으로 투자자들의 심리가 좋아졌어요',
  created_at: new Date().toISOString()
};

export async function getLatestPrediction(): Promise<Prediction> {
  try {
    console.log('Fetching from:', `${API_URL}/api/predictions/latest`);
    
    const res = await fetch(`${API_URL}/api/predictions/latest`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(10000) // 10초 타임아웃
    });
    
    if (!res.ok) {
      console.warn(`API returned ${res.status}, using mock data`);
      return mockPrediction;
    }
    
    const data = await res.json();
    console.log('API response:', data);
    return data;
    
  } catch (error) {
    console.error('API fetch failed:', error);
    console.log('Using mock data');
    return mockPrediction;
  }
}

export async function getAccuracyStats() {
  try {
    const res = await fetch(`${API_URL}/api/predictions/stats/accuracy`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(10000)
    });
    
    if (!res.ok) {
      return { total: 0, correct: 0, accuracy: 0, avg_confidence: 0 };
    }
    
    return res.json();
  } catch (error) {
    console.error('Stats fetch failed:', error);
    return { total: 0, correct: 0, accuracy: 0, avg_confidence: 0 };
  }
}
