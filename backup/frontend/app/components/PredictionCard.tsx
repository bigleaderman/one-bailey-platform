'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { TrendingUp, TrendingDown, ChevronDown, ChevronUp } from 'lucide-react';
import type { Prediction } from '@/lib/api';

interface PredictionCardProps {
  prediction: Prediction;
  isUp: boolean;
  confidencePercent: number;
}

export default function PredictionCard({ prediction, isUp, confidencePercent }: PredictionCardProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-md border-2 border-blue-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-gray-800">나스닥 ETF (QQQ)</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${isUp ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          오늘 예측
        </span>
      </div>

      <div className="flex items-center gap-4 mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {isUp ? <TrendingUp className="text-green-500" size={32} /> : <TrendingDown className="text-red-500" size={32} />}
            <span className={`text-3xl font-bold ${isUp ? 'text-green-500' : 'text-red-500'}`}>
              {isUp ? '상승' : '하락'} 예상
            </span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm text-gray-600">신뢰도:</span>
            {[1,2,3,4,5].map(i => (
              <span key={i} className={`text-lg ${i <= Math.round(confidencePercent / 20) ? 'text-yellow-400' : 'text-gray-400'}`}>⭐</span>
            ))}
            <span className="ml-2 text-sm font-semibold text-gray-700">({confidencePercent}%)</span>
          </div>
        </div>
      </div>

      <button
        onClick={() => toggleSection('prediction')}
        className="w-full bg-blue-50 text-blue-600 py-3 rounded-xl font-semibold flex items-center justify-center gap-2 hover:bg-blue-100 transition-all mb-4"
      >
        예측 근거 보기
        {expandedSection === 'prediction' ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>

      {/* 예측 근거 확장 섹션 */}
      {expandedSection === 'prediction' && (
        <div className="space-y-4 animate-in fade-in duration-300">
          {/* 핵심 요인 */}
          {prediction.key_factors && prediction.key_factors.length > 0 && (
            <div className="bg-green-50 rounded-xl p-4">
              <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                <span className="text-xl">📊</span>
                {isUp ? '상승' : '하락'} 예상 근거
              </h4>
              <div className="space-y-2">
                {prediction.key_factors.map((factor, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <span className={`flex-shrink-0 w-6 h-6 rounded-full text-white flex items-center justify-center text-sm font-bold ${isUp ? 'bg-green-500' : 'bg-red-500'}`}>
                      {index + 1}
                    </span>
                    <p className="text-sm text-gray-700">{factor}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 리스크 요인 */}
          {prediction.risk_factors && prediction.risk_factors.length > 0 && (
            <div className="bg-orange-50 rounded-xl p-4">
              <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                <span className="text-xl">⚠️</span>
                주의해야 할 리스크
              </h4>
              <div className="space-y-2">
                {prediction.risk_factors.map((risk, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-orange-500 text-white flex items-center justify-center text-sm font-bold">
                      !
                    </span>
                    <p className="text-sm text-gray-700">{risk}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 상세보기 버튼 */}
          <Link href={`/prediction/${prediction.id}`}>
            <button className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 transition-all">
              전체 분석 보기
            </button>
          </Link>
        </div>
      )}
    </div>
  );
}
