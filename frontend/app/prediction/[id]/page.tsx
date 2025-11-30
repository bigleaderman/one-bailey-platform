import Link from 'next/link';
import { getLatestPrediction } from '@/lib/api';

export default async function PredictionDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
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
