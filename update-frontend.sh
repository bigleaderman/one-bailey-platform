#!/bin/bash

# OneBailey 프론트엔드 업데이트 스크립트

set -e

echo "🚀 OneBailey 프론트엔드 업데이트 시작..."

cd frontend

# 1. app/page.tsx 업데이트
echo "📝 메인 페이지 업데이트..."
cat > app/page.tsx << 'EOFPAGE'
import Link from 'next/link';
import { getLatestPrediction } from '@/lib/api';

export default async function Home() {
  const prediction = await getLatestPrediction();
  
  const isUp = prediction.direction === 'UP';
  const confidencePercent = Math.round(prediction.confidence * 100);
  
  const predictionDate = new Date(prediction.prediction_date);
  const formattedDate = `${predictionDate.getFullYear()}년 ${predictionDate.getMonth() + 1}월 ${predictionDate.getDate()}일`;

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* 헤더 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-600">OneBailey</h1>
          <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* 메인 예측 카드 */}
        <div className={`rounded-3xl p-8 ${isUp ? 'bg-gradient-to-br from-green-400 to-green-500' : 'bg-gradient-to-br from-red-400 to-red-500'} text-white shadow-xl`}>
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <span className="text-sm opacity-90">{formattedDate}</span>
          </div>
          
          <h2 className="text-3xl font-bold mb-3">
            오늘 미국 증시는 {isUp ? '상승' : '하락'}할 것으로 예상돼요 {isUp ? '📈' : '📉'}
          </h2>
          
          <p className="text-lg opacity-90 mb-6">
            {prediction.summary}
          </p>
          
          <Link href={`/prediction/${prediction.id}`}>
            <button className="bg-white text-green-600 px-6 py-3 rounded-full font-semibold hover:bg-opacity-90 transition-all">
              자세히 보기
            </button>
          </Link>
        </div>

        {/* 나스닥 ETF 카드 */}
        <div className="bg-white rounded-3xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold">나스닥 ETF (QQQ)</h3>
            <span className={`text-sm px-3 py-1 rounded-full ${isUp ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              오늘 예측
            </span>
          </div>
          
          <div className="flex items-center gap-3 mb-4">
            <svg className={`w-8 h-8 ${isUp ? 'text-green-500' : 'text-red-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isUp ? "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" : "M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"} />
            </svg>
            <span className={`text-3xl font-bold ${isUp ? 'text-green-600' : 'text-red-600'}`}>
              {isUp ? '상승' : '하락'} 예상
            </span>
          </div>
          
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm text-gray-600">신뢰도:</span>
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <span key={i} className={i < Math.round(confidencePercent / 20) ? 'text-yellow-400' : 'text-gray-300'}>
                  ⭐
                </span>
              ))}
              <span className="ml-2 font-semibold">({confidencePercent}%)</span>
            </div>
          </div>
          
          <Link href={`/prediction/${prediction.id}`}>
            <button className="w-full text-blue-600 py-3 border-t border-gray-200 font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
              예측 근거 보기
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </Link>
        </div>
      </div>

      {/* 푸터 */}
      <footer className="bg-gray-900 text-gray-400 py-8 mt-12">
        <div className="max-w-4xl mx-auto px-4 text-center text-sm">
          <p className="mb-2">본 정보는 투자 참고용이며, 투자 손실에 대한 책임은 투자자 본인에게 있습니다.</p>
          <p>© 2025 OneBailey. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
EOFPAGE

# 2. 상세 페이지 디렉토리 생성
echo "📁 상세 페이지 디렉토리 생성..."
mkdir -p app/prediction/[id]

# 3. 상세 페이지 생성
echo "📝 상세 페이지 생성..."
cat > app/prediction/[id]/page.tsx << 'EOFDETAIL'
import Link from 'next/link';
import { getLatestPrediction } from '@/lib/api';

export default async function PredictionDetail({ params }: { params: { id: string } }) {
  const prediction = await getLatestPrediction();
  
  const isUp = prediction.direction === 'UP';
  const confidencePercent = Math.round(prediction.confidence * 100);
  
  const predictionDate = new Date(prediction.prediction_date);
  const formattedDate = `${predictionDate.getFullYear()}년 ${predictionDate.getMonth() + 1}월 ${predictionDate.getDate()}일`;

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* 헤더 */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6 flex items-center justify-between">
          <Link href="/">
            <h1 className="text-2xl font-bold text-blue-600 cursor-pointer hover:text-blue-700">OneBailey</h1>
          </Link>
          <Link href="/">
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
          </Link>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* 예측 요약 카드 */}
        <div className={`rounded-3xl p-8 ${isUp ? 'bg-gradient-to-br from-green-400 to-green-500' : 'bg-gradient-to-br from-red-400 to-red-500'} text-white shadow-xl`}>
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-sm opacity-90">{formattedDate} 예측</span>
          </div>
          
          <div className="flex items-center gap-4 mb-4">
            <svg className={`w-16 h-16`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isUp ? "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" : "M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"} />
            </svg>
            <div>
              <h2 className="text-4xl font-bold mb-2">
                {isUp ? '상승' : '하락'} 예상
              </h2>
              <p className="text-lg opacity-90">
                나스닥 ETF (QQQ)
              </p>
            </div>
          </div>
          
          <div className="bg-white bg-opacity-20 rounded-2xl p-4 mb-4">
            <div className="flex items-center gap-2">
              <span className="text-sm">AI 신뢰도:</span>
              <div className="flex items-center gap-1">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className={i < Math.round(confidencePercent / 20) ? 'text-yellow-300' : 'text-white text-opacity-30'}>
                    ⭐
                  </span>
                ))}
                <span className="ml-2 font-bold text-lg">({confidencePercent}%)</span>
              </div>
            </div>
          </div>
        </div>

        {/* 한줄 요약 */}
        <div className="bg-white rounded-3xl p-6 shadow-lg">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span className="text-2xl">💡</span>
            한줄 요약
          </h3>
          <p className="text-lg text-gray-700 leading-relaxed">
            {prediction.summary}
          </p>
        </div>

        {/* 핵심 요인 */}
        {prediction.key_factors && prediction.key_factors.length > 0 && (
          <div className="bg-white rounded-3xl p-6 shadow-lg">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <span className="text-2xl">📊</span>
              {isUp ? '상승' : '하락'} 예상 근거
            </h3>
            <div className="space-y-3">
              {prediction.key_factors.map((factor, index) => (
                <div key={index} className="flex items-start gap-3 p-4 bg-green-50 rounded-xl">
                  <span className={`flex-shrink-0 w-6 h-6 rounded-full ${isUp ? 'bg-green-500' : 'bg-red-500'} text-white flex items-center justify-center text-sm font-bold`}>
                    {index + 1}
                  </span>
                  <p className="text-gray-700 flex-1">{factor}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 리스크 요인 */}
        {prediction.risk_factors && prediction.risk_factors.length > 0 && (
          <div className="bg-white rounded-3xl p-6 shadow-lg">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <span className="text-2xl">⚠️</span>
              주의해야 할 리스크
            </h3>
            <div className="space-y-3">
              {prediction.risk_factors.map((risk, index) => (
                <div key={index} className="flex items-start gap-3 p-4 bg-orange-50 rounded-xl">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-orange-500 text-white flex items-center justify-center text-sm font-bold">
                    !
                  </span>
                  <p className="text-gray-700 flex-1">{risk}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 실제 결과 (있는 경우) */}
        {prediction.actual_direction && (
          <div className="bg-white rounded-3xl p-6 shadow-lg border-2 border-blue-500">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <span className="text-2xl">✅</span>
              실제 결과
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-xl">
                <p className="text-sm text-gray-600 mb-1">예측</p>
                <p className={`text-2xl font-bold ${isUp ? 'text-green-600' : 'text-red-600'}`}>
                  {prediction.direction === 'UP' ? '상승' : '하락'}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-xl">
                <p className="text-sm text-gray-600 mb-1">실제</p>
                <p className={`text-2xl font-bold ${prediction.actual_direction === 'UP' ? 'text-green-600' : 'text-red-600'}`}>
                  {prediction.actual_direction === 'UP' ? '상승' : '하락'}
                  {prediction.actual_change && (
                    <span className="text-lg ml-2">
                      ({prediction.actual_change > 0 ? '+' : ''}{prediction.actual_change.toFixed(2)}%)
                    </span>
                  )}
                </p>
              </div>
            </div>
            <div className="mt-4 p-4 bg-blue-50 rounded-xl text-center">
              <p className="font-bold text-blue-700">
                {prediction.direction === prediction.actual_direction ? '✅ 예측 성공!' : '❌ 예측 실패'}
              </p>
            </div>
          </div>
        )}

        {/* 뒤로가기 버튼 */}
        <Link href="/">
          <button className="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold hover:bg-blue-700 transition-colors">
            메인으로 돌아가기
          </button>
        </Link>
      </div>

      {/* 푸터 */}
      <footer className="bg-gray-900 text-gray-400 py-8 mt-12">
        <div className="max-w-4xl mx-auto px-4 text-center text-sm">
          <p className="mb-2">본 정보는 투자 참고용이며, 투자 손실에 대한 책임은 투자자 본인에게 있습니다.</p>
          <p>© 2025 OneBailey. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
EOFDETAIL

# 4. layout.tsx 업데이트
echo "📝 Layout 업데이트..."
cat > app/layout.tsx << 'EOFLAYOUT'
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'OneBailey - QQQ ETF 예측',
  description: 'AI 기반 나스닥 100 ETF 일일 예측 서비스',
  keywords: 'QQQ, 나스닥, ETF, 주식예측, AI예측, 투자',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="antialiased">{children}</body>
    </html>
  );
}
EOFLAYOUT

echo ""
echo "✅ 업데이트 완료!"
echo ""
echo "📋 변경사항:"
echo "  - 브랜드명: 쉬운경제 → OneBailey"
echo "  - 메인 페이지: Backend API 연동"
echo "  - 상세 페이지: /prediction/[id] 추가"
echo "  - 상세 정보: 예측 근거, 리스크, 실제 결과"
echo ""
echo "🚀 다음 단계:"
echo "  npm run dev"
echo ""
