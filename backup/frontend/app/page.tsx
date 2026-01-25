import React from 'react';
import Link from 'next/link';
import { getLatestPrediction } from '@/lib/api';
import { Bell, TrendingUp, TrendingDown } from 'lucide-react';
import PredictionCard from './components/PredictionCard';

// 동적 렌더링 강제 - 매 요청마다 최신 데이터를 가져옴
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function Home() {
  const prediction = await getLatestPrediction();

  const isUp = prediction.direction === 'UP';
  const confidencePercent = Math.round(prediction.confidence * 100);

  const predictionDate = new Date(prediction.prediction_date);
  const todayDate = `${predictionDate.getFullYear()}년 ${predictionDate.getMonth() + 1}월 ${predictionDate.getDate()}일`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">OneBailey</h1>
          <div className="p-2 rounded-lg bg-gray-100 text-gray-600">
            <Bell size={20} />
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Hero Section - 오늘의 시장 한 줄 요약 */}
        <div className={`rounded-3xl p-8 text-white shadow-lg ${isUp ? 'bg-gradient-to-r from-green-400 to-green-500' : 'bg-gradient-to-r from-red-400 to-red-500'}`}>
          <div className="flex items-center gap-2 mb-2">
            {isUp ? <TrendingUp size={28} /> : <TrendingDown size={28} />}
            <span className="text-sm font-medium opacity-90">{todayDate}</span>
          </div>
          <h2 className="text-3xl font-bold mb-3">
            오늘 미국 증시는 {isUp ? '상승' : '하락'}할 것으로 예상돼요 {isUp ? '📈' : '📉'}
          </h2>
          <p className="text-lg opacity-95">
            {prediction.summary || '금리 동결 기대감으로 투자자들의 심리가 좋아졌어요'}
          </p>
          <Link href={`/prediction/${prediction.id}`}>
            <button className={`mt-6 bg-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all ${isUp ? 'text-green-600' : 'text-red-600'}`}>
              자세히 보기
            </button>
          </Link>
        </div>

        {/* 오늘의 예측 카드 (나스닥) - Client Component */}
        <PredictionCard
          prediction={prediction}
          isUp={isUp}
          confidencePercent={confidencePercent}
        />
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 mt-12 py-8">
        <div className="max-w-4xl mx-auto px-4 text-center text-sm text-gray-600">
          <p>본 정보는 투자 참고용이며, 투자 손실에 대한 책임은 투자자 본인에게 있습니다.</p>
          <p className="mt-2">© 2025 OneBailey. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
