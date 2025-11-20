import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '쉬운경제 - QQQ 예측',
  description: 'AI 기반 나스닥 ETF 일일 예측 서비스',
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
