import { getLatestPrediction } from '@/lib/api';

export default async function Home() {
  let prediction;
  
  try {
    prediction = await getLatestPrediction();
  } catch (error) {
    // Mock 데이터
    prediction = {
      id: 1,
      prediction_date: new Date().toISOString().split('T')[0],
      direction: 'UP' as const,
      confidence: 0.80,
      summary: '글린 통걸 기대감으로 투자자들의 심리가 좋아졌어요',
      key_factors: ['나스닥 선물 강세', '달러 약세'],
      created_at: new Date().toISOString()
    };
  }
  
  const isUp = prediction.direction === 'UP';
  const confidencePercent = Math.round(prediction.confidence * 100);
  
  const predictionDate = new Date(prediction.prediction_date);
  const formattedDate = `${predictionDate.getFullYear()}년 ${predictionDate.getMonth() + 1}월 ${predictionDate.getDate()}일`;

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-600">쉬운경제</h1>
          <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </button>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
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
          
          <button className="bg-white text-green-600 px-6 py-3 rounded-full font-semibold hover:bg-opacity-90 transition-all">
            자세히 보기
          </button>
        </div>

        <div className="bg-white rounded-3xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold">나스닥 ETF (QQQ)</h3>
            <span className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-full">
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
        </div>
      </div>

      <footer className="bg-gray-900 text-gray-400 py-8 mt-12">
        <div className="max-w-4xl mx-auto px-4 text-center text-sm">
          <p className="mb-2">본 정보는 투자 참고용이며, 투자 손실에 대한 책임은 투자자 본인에게 있습니다.</p>
          <p>© 2025 쉬운경제. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
