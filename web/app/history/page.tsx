'use client';

import { useState, useEffect } from 'react';
import { getHistory, HistoryRecord, HistoryResponse } from '@/lib/api';
import Link from 'next/link';

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState(0);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const response: HistoryResponse = await getHistory(20);
      setRecords(response.records);
      setCount(response.count);
    } catch (err: any) {
      setError(err.error || err.message || 'Failed to load history');
      console.error('Failed to load history:', err);
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

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">分析历史记录</h1>
              <p className="text-gray-600 mt-2">查看您最近的情感分析记录</p>
            </div>
            <Link
              href="/"
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              返回首页
            </Link>
          </div>
          <div className="border-t pt-4">
            <p className="text-sm text-gray-500">
              此页面展示您最近的分析记录。每条记录包含关系阶段、兴趣等级、下一步建议和分析时间。
            </p>
          </div>
        </header>

        {/* Stats */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">总记录数</p>
            <p className="text-2xl font-bold text-gray-900">{count}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">当前显示</p>
            <p className="text-2xl font-bold text-gray-900">{records.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">最近更新</p>
            <p className="text-lg font-medium text-gray-900">
              {records.length > 0 ? formatDate(records[0]?.created_at) : '无记录'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">状态</p>
            <p className="text-lg font-medium">
              {loading ? (
                <span className="text-blue-600">加载中...</span>
              ) : error ? (
                <span className="text-red-600">加载失败</span>
              ) : (
                <span className="text-green-600">已加载</span>
              )}
            </p>
          </div>
        </div>

        {/* Main content */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          {/* Loading state */}
          {loading && (
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-50 mb-4">
                <svg className="animate-spin w-8 h-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">加载历史记录</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                正在从服务器获取您的分析历史记录，请稍候片刻...
              </p>
            </div>
          )}

          {/* Error state */}
          {error && !loading && (
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-50 mb-4">
                <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">加载失败</h3>
              <p className="text-gray-600 max-w-md mx-auto mb-4">{error}</p>
              <div className="mt-6">
                <button
                  className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md font-medium hover:bg-blue-200"
                  onClick={loadHistory}
                >
                  重新加载
                </button>
              </div>
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && records.length === 0 && (
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-50 mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">暂无历史记录</h3>
              <p className="text-gray-500 max-w-md mx-auto mb-6">
                您还没有进行过情感分析。返回首页开始您的第一次分析吧！
              </p>
              <Link
                href="/"
                className="px-6 py-3 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 transition-colors"
              >
                开始分析
              </Link>
            </div>
          )}

          {/* Records list */}
          {!loading && !error && records.length > 0 && (
            <div>
              <div className="p-4 bg-gray-50 border-b">
                <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-700">
                  <div className="col-span-3">分析时间</div>
                  <div className="col-span-2">关系阶段</div>
                  <div className="col-span-2">兴趣等级</div>
                  <div className="col-span-3">用户问题</div>
                  <div className="col-span-2">下一步建议</div>
                </div>
              </div>

              {records.map((record) => (
                <Link
                  key={record.request_id}
                  href={`/history/${record.request_id}`}
                  className="block p-4 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-b-0"
                >
                  <div className="grid grid-cols-12 gap-4 items-center">
                    {/* Created at */}
                    <div className="col-span-3">
                      <p className="font-medium text-gray-900">{formatDate(record.created_at)}</p>
                      <p className="text-xs text-gray-500 mt-1">ID: {record.request_id.substring(0, 8)}...</p>
                    </div>

                    {/* Relationship stage */}
                    <div className="col-span-2">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStageColor(record.relationship_stage)}`}>
                        {record.relationship_stage}
                      </span>
                    </div>

                    {/* Interest level */}
                    <div className="col-span-2">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getInterestColor(record.interest_level)}`}>
                        {record.interest_level}
                      </span>
                    </div>

                    {/* User question */}
                    <div className="col-span-3">
                      <p className="text-gray-800 line-clamp-2">
                        {record.user_question || '未记录问题'}
                      </p>
                    </div>

                    {/* Next step */}
                    <div className="col-span-2">
                      <p className="text-gray-800 line-clamp-2">
                        {record.next_step}
                      </p>
                    </div>
                  </div>

                  {/* Provider info (hidden on small screens) */}
                  <div className="mt-3 pt-3 border-t border-gray-100 flex justify-between items-center text-sm text-gray-500">
                    <div>
                      {record.provider_name && (
                        <span>分析模型: {record.provider_name}</span>
                      )}
                    </div>
                    <div className="text-xs">
                      <span className="text-blue-600">查看详情 →</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-8 pt-6 border-t text-center text-gray-500 text-sm">
          <p>LoveAdvisor V4 历史记录页面 | 开发阶段：Phase4-MTU5 | 最后更新：2026-04-18</p>
          <p className="mt-2">此页面为最小实现版本，仅展示历史记录，不提供分页、筛选或删除功能。</p>
        </footer>
      </div>
    </div>
  );
}