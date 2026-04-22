import React from 'react';
import { AnalyzeResult } from '@/lib/api';
import { getRelationshipStageExplanation, getInterestLevelExplanation } from '@/lib/resultExplanations';
import { generateConclusion } from '@/lib/generateConclusion';

interface SummaryCardProps {
  result: AnalyzeResult;
}

export default function SummaryCard({ result }: SummaryCardProps) {
  const { relationship_stage, interest_level } = result;
  const conclusion = generateConclusion(result);

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6 shadow-sm">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 关系阶段 */}
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center mr-3">
              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5 5.197a6 6 0 00-9-5.197M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5 5.197a6 6 0 00-9-5.197" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-800">关系阶段</h3>
          </div>
          <p className="text-gray-700 font-medium text-xl mb-1">{relationship_stage}</p>
          <p className="text-gray-500 text-sm">
            {getRelationshipStageExplanation(relationship_stage)}
          </p>
        </div>

        {/* 兴趣等级 */}
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center mr-3">
              <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-800">兴趣等级</h3>
          </div>
          <p className="text-gray-700 font-medium text-xl mb-1">{interest_level}</p>
          <p className="text-gray-500 text-sm">
            {getInterestLevelExplanation(interest_level)}
          </p>
        </div>

        {/* 一句话总结 */}
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center mr-3">
              <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-800">核心总结</h3>
          </div>
          <p className="text-gray-700 font-medium text-lg leading-relaxed">{conclusion}</p>
        </div>
      </div>

      {/* 移动端分隔线 */}
      <div className="lg:hidden mt-6 pt-6 border-t border-blue-200"></div>
      <div className="lg:hidden text-center text-gray-400 text-sm">
        滑动查看完整分析
      </div>
    </div>
  );
}