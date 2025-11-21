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

export async function getLatestPrediction(): Promise<Prediction> {
  const res = await fetch(`${API_URL}/api/predictions/latest`, {
    cache: 'no-store'
  });
  
  if (!res.ok) {
    throw new Error('Failed to fetch prediction');
  }
  
  return res.json();
}
