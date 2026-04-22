'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getHistoryRecord, FullHistoryRecord } from '@/lib/api';

export default function HistoryDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [record, setRecord] = useState<FullHistoryRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const request_id = params.request_id as string;

  useEffect(() => {
    loadRecord();
  }, [request_id]);

  const loadRecord = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getHistoryRecord(request_id);
      setRecord(data);
    } catch (err: any) {
      setError(err.error || err.message || 'Failed to load record details');
      console.error('Failed to load record:', err);
    } finally {
      setLoading(false);
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    } catch {
      return dateString;
    }
  };

  // Get color for relationship stage
  const getStageColor = (stage: string) => {
    switch (stage) {
      case '初识期': return 'bg-blue-100 text-blue-800';
      case '暧昧期': return 'bg-purple-100 text-purple-800';
      case '拉扯期': return 'bg-yellow-100 text-yellow-800';
      case '冷淡期': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Get color for interest level
  const getInterestColor = (level: string) => {
    switch (level) {
      case '高': return 'bg-green-100 text-green-800';
      case '中': return 'bg-yellow-100 text-yellow-800';
      case '低': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  // Render list items with bullet points
  const renderList = (items: string[] | undefined, title: string) => {
    if (!items || items.length === 0) {
      return (
        <div className="mt-4">
          <h3 className="font-medium text-gray-900 mb-2">{title}</h3>
          <p className="text-gray-500 italic">无</p>
        </div>
      );
    }

    return (
      <div className="mt-4">
        <h3 className="font-medium text-gray-900 mb-2">{title}</h3>
        <ul className="list-disc pl-5 space-y-1">
          {items.map((item, index) => (
            <li key={index} className="text-gray-700">{item}</li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">分析记录详情</h1>
              <p className="text-gray-600 mt-2">查看完整的情感分析结果</p>
            </div>
            <div className="flex space-x-3">
              <Link
                href="/history"
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                返回历史记录
              </Link>
              <Link
                href="/"
                className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
              >
                返回首页
              </Link>
            </div>
          </div>
          <div className="border-t pt-4">
            <p className="text-sm text-gray-500">
              此页面展示分析记录的完整详情，包括关系阶段、兴趣等级、心理分析、风险点、建议和下一步行动。
            </p>
          </div>
        </header>

        {/* Loading state */}
        {loading && (
          <div className="bg-white rounded-xl shadow-md p-12 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-50 mb-4">
              <svg className="animate-spin w-8 h-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">加载记录详情</h3>
            <p className="text-gray-500 max-w-md mx-auto">
              正在从服务器获取记录详情，请稍候片刻...
            </p>
          </div>
        )}

        {/* Error state */}
        {error && !loading && (
          <div className="bg-white rounded-xl shadow-md p-12 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-50 mb-4">
              <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">加载失败</h3>
            <p className="text-gray-600 max-w-md mx-auto mb-4">{error}</p>
            <div className="mt-6 space-x-4">
              <button
                className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md font-medium hover:bg-blue-200"
                onClick={loadRecord}
              >
                重新加载
              </button>
              <Link
                href="/history"
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md font-medium hover:bg-gray-200 inline-block"
              >
                返回历史记录
              </Link>
            </div>
          </div>
        )}

        {/* Record details */}
        {!loading && !error && record && (
          <div className="space-y-6">
            {/* Basic info card */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 pb-3 border-b">基本信息</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-500">请求ID</p>
                  <p className="font-mono text-gray-900 break-all">{record.request_id}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">分析时间</p>
                  <p className="text-gray-900">{formatDate(record.created_at)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">用户问题</p>
                  <p className="text-gray-900">{record.user_question || '未记录问题'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">分析模型</p>
                  <p className="text-gray-900">{record.provider_name || '未记录'}</p>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-500">关系阶段</p>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-1 ${getStageColor(record.relationship_stage)}`}>
                    {record.relationship_stage}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-500">兴趣等级</p>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-1 ${getInterestColor(record.interest_level)}`}>
                    {record.interest_level}
                  </span>
                </div>
              </div>

              <div className="mt-6">
                <p className="text-sm text-gray-500">对话文本</p>
                <div className="mt-1 p-3 bg-gray-50 rounded-md max-h-60 overflow-y-auto">
                  <pre className="text-gray-800 whitespace-pre-wrap text-sm">{record.chat_text}</pre>
                </div>
              </div>
            </div>

            {/* Analysis results card */}
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4 pb-3 border-b">分析结果</h2>

              {/* Psychological analysis */}
              <div className="mt-4">
                <h3 className="font-medium text-gray-900 mb-2">心理分析</h3>
                <div className="p-3 bg-blue-50 rounded-md">
                  <p className="text-gray-800">{record.psychological_analysis || '无心理分析内容'}</p>
                </div>
              </div>

              {/* Risk points */}
              {renderList(record.risk_points, '风险点')}

              {/* Suggestions */}
              {renderList(record.suggestions, '行动建议')}

              {/* Next step */}
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
                <h3 className="font-medium text-green-900 mb-1">下一步行动</h3>
                <p className="text-green-800">{record.next_step}</p>
              </div>
            </div>

            {/* Debug info (if available) */}
            {record.debug && Object.keys(record.debug).length > 0 && (
              <div className="bg-white rounded-xl shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 pb-3 border-b">调试信息</h2>
                <div className="p-3 bg-gray-50 rounded-md max-h-80 overflow-y-auto">
                  <pre className="text-gray-800 text-sm">{JSON.stringify(record.debug, null, 2)}</pre>
                </div>
              </div>
            )}

            {/* Footer actions */}
            <div className="flex justify-between items-center pt-6 border-t">
              <Link
                href="/history"
                className="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-md font-medium hover:bg-gray-200 transition-colors"
              >
                ← 返回历史记录
              </Link>
              <div className="flex items-center space-x-4">
                <Link
                  href={`/?chat_text=${encodeURIComponent(record.chat_text)}&user_question=${encodeURIComponent(record.user_question || '')}`}
                  className="px-5 py-2.5 bg-green-100 text-green-700 rounded-md font-medium hover:bg-green-200 transition-colors"
                >
                  再次分析
                </Link>
                <div className="text-sm text-gray-500">
                  记录ID: {record.request_id.substring(0, 12)}...
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-8 pt-6 border-t text-center text-gray-500 text-sm">
          <p>LoveAdvisor V4 历史记录详情页面 | 开发阶段：Phase4-MTU6 | 最后更新：2026-04-18</p>
          <p className="mt-2">此页面为最小实现版本，仅展示记录详情，不提供编辑、删除或更新功能。</p>
        </footer>
      </div>
    </div>
  );
}