import React from 'react';
import Link from 'next/link';

interface NextActionsCardProps {
  requestId?: string;
  onNewAnalysis?: () => void;
  onFeedback?: (helpful: boolean) => void;
}

export default function NextActionsCard({
  requestId,
  onNewAnalysis,
  onFeedback
}: NextActionsCardProps) {
  const handleFeedback = (helpful: boolean) => {
    if (onFeedback) {
      onFeedback(helpful);
    } else {
      // 默认行为：控制台记录或简单提示
      console.log(`用户反馈：${helpful ? '有帮助' : '无帮助'}`);
      alert(`感谢您的反馈！分析工具会持续改进。`);
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl border border-gray-200 p-6 shadow-sm mt-6">
      <div className="flex items-center mb-4">
        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-800">接下来可以做什么？</h3>
          <p className="text-gray-600 text-sm">基于本次分析结果，您可以考虑以下行动</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* 查看历史记录 */}
        <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center mr-3">
              <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <p className="font-medium text-gray-700">回顾历史分析</p>
              <p className="text-gray-500 text-sm">查看过往的分析记录，跟踪关系变化</p>
            </div>
          </div>
          <Link
            href="/history"
            className="px-4 py-2 bg-purple-100 text-purple-700 rounded-md font-medium hover:bg-purple-200 transition-colors text-sm"
          >
            查看历史
          </Link>
        </div>

        {/* 查看本次记录（如果有requestId） */}
        {requestId && (
          <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center mr-3">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div>
                <p className="font-medium text-gray-700">查看本次分析详情</p>
                <p className="text-gray-500 text-sm">保存本次分析结果，便于后续回顾</p>
              </div>
            </div>
            <Link
              href={`/history/${requestId}`}
              className="px-4 py-2 bg-green-100 text-green-700 rounded-md font-medium hover:bg-green-200 transition-colors text-sm"
            >
              查看详情
            </Link>
          </div>
        )}

        {/* 重新分析 */}
        <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3">
              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
            </div>
            <div>
              <p className="font-medium text-gray-700">再次分析或修改输入</p>
              <p className="text-gray-500 text-sm">调整对话内容或问题，获取新的分析视角</p>
            </div>
          </div>
          <button
            onClick={onNewAnalysis}
            className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md font-medium hover:bg-blue-200 transition-colors text-sm"
          >
            重新分析
          </button>
        </div>

        {/* 轻量反馈 */}
        <div className="bg-white p-4 rounded-lg border border-gray-100">
          <div className="flex items-center mb-3">
            <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center mr-3">
              <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
              </svg>
            </div>
            <div>
              <p className="font-medium text-gray-700">这次分析对您有帮助吗？</p>
              <p className="text-gray-500 text-sm">您的反馈将帮助我们改进分析质量</p>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => handleFeedback(true)}
              className="flex-1 py-2 bg-green-50 text-green-700 rounded-md font-medium hover:bg-green-100 transition-colors text-sm"
            >
              有帮助
            </button>
            <button
              onClick={() => handleFeedback(false)}
              className="flex-1 py-2 bg-red-50 text-red-700 rounded-md font-medium hover:bg-red-100 transition-colors text-sm"
            >
              帮助不大
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-gray-500 text-sm text-center">
          分析结果仅供参考，现实沟通与真诚交流才是关系发展的基石
        </p>
      </div>
    </div>
  );
}