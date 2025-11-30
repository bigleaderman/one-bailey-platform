'use client';

import React, { useState } from 'react';
import { Bell, TrendingUp, TrendingDown, ChevronDown, ChevronUp } from 'lucide-react';

export default function Home() {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [notificationEnabled, setNotificationEnabled] = useState(false);

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  // 정적 데이터 (초안용)
  const todayDate = "2025년 11월 20일";
  const isUp = true;
  const confidence = 80;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">OneBailey</h1>
          <button
            onClick={() => setNotificationEnabled(!notificationEnabled)}
            className={`p-2 rounded-lg transition-all ${notificationEnabled ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'}`}
          >
            <Bell size={20} />
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Hero Section - 오늘의 시장 한 줄 요약 */}
        <div className="bg-gradient-to-r from-green-400 to-green-500 rounded-3xl p-8 text-white shadow-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={28} />
            <span className="text-sm font-medium opacity-90">{todayDate}</span>
          </div>
          <h2 className="text-3xl font-bold mb-3">
            오늘 미국 증시는 상승할 것으로 예상돼요 📈
          </h2>
          <p className="text-lg opacity-95">
            금리 동결 기대감으로 투자자들의 심리가 좋아졌어요
          </p>
          <button className="mt-6 bg-white text-green-600 px-6 py-3 rounded-xl font-semibold hover:shadow-lg transition-all">
            자세히 보기
          </button>
        </div>

        {/* 오늘의 예측 카드 (나스닥) */}
        <div className="bg-white rounded-2xl p-6 shadow-md border-2 border-blue-100">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-800">나스닥 ETF (QQQ)</h3>
            <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
              오늘 예측
            </span>
          </div>

          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="text-green-500" size={32} />
                <span className="text-3xl font-bold text-green-500">상승 예상</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-sm text-gray-600">신뢰도:</span>
                {[1,2,3,4].map(i => (
                  <span key={i} className="text-yellow-400 text-lg">⭐</span>
                ))}
                <span className="text-gray-400 text-lg">⭐</span>
                <span className="ml-2 text-sm font-semibold text-gray-700">({confidence}%)</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => toggleSection('prediction')}
            className="w-full bg-blue-50 text-blue-600 py-3 rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-blue-100 transition-all"
          >
            예측 근거 보기
            {expandedSection === 'prediction' ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>
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
