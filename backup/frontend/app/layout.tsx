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
