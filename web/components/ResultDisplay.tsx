import React from 'react';
import { AnalyzeResult } from '@/lib/api';
import ResultCard from './ResultCard';
import OneSentenceConclusion from './OneSentenceConclusion';
import SummaryCard from './result/SummaryCard';
import NextActionsCard from './result/NextActionsCard';
import { getRelationshipStageExplanation, getInterestLevelExplanation } from '@/lib/resultExplanations';
import { generateCredibilityHints, getDataSourceExplanation } from '@/lib/resultReasoning';

interface ResultDisplayProps {
  result: AnalyzeResult | null;
  status?: 'idle' | 'loading' | 'error' | 'success';
  errorMessage?: string;
  requestId?: string;
  onNewAnalysis?: () => void;
  onFeedback?: (helpful: boolean) => void;
}

export default function ResultDisplay({
  result,
  status,
  errorMessage,
  requestId,
  onNewAnalysis,
  onFeedback
}: ResultDisplayProps) {
  // 确定实际状态
  const actualStatus = status || (result ? 'success' : 'idle');

  // 未分析状态 - 温和引导型空状态
  if (actualStatus === 'idle') {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-50 mb-4">
            <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">等待分析</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            请在上方输入或上传对话内容，填写您的问题，然后点击"确认并开始分析"按钮获取情感分析结果。
          </p>
        </div>
        {/* 保留原有的卡片结构占位，但使用更温和的文案 */}
        <OneSentenceConclusion result={null} />
        <ResultCard title="关系阶段">
          <p className="text-gray-400 italic">分析后将显示关系阶段评估</p>
        </ResultCard>
        <ResultCard title="兴趣等级">
          <p className="text-gray-400 italic">分析后将显示兴趣等级评估</p>
        </ResultCard>
        <ResultCard title="心理分析">
          <p className="text-gray-400 italic">分析后将显示心理分析洞察</p>
        </ResultCard>
        <ResultCard title="分析依据" variant="default">
          <p className="text-gray-400 italic">分析后将显示分析依据和信号来源</p>
        </ResultCard>
        <ResultCard title="风险点" variant="risk">
          <p className="text-gray-400 italic">分析后将识别潜在风险点</p>
        </ResultCard>
        <ResultCard title="建议">
          <p className="text-gray-400 italic">分析后将提供具体建议</p>
        </ResultCard>
        <ResultCard title="下一步行动" variant="next_step">
          <p className="text-gray-400 italic">分析后将推荐下一步行动</p>
        </ResultCard>
      </div>
    );
  }

  // 分析中状态 - 明确加载状态
  if (actualStatus === 'loading') {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-50 mb-4">
            <svg className="animate-spin w-8 h-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">分析进行中，请稍候...</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            正在深度分析您提供的对话内容和问题，请稍候片刻...
          </p>
          <div className="mt-4">
            <div className="h-1 w-48 bg-gray-200 rounded-full overflow-hidden mx-auto">
              <div className="h-full bg-blue-500 animate-pulse" style={{ width: '60%' }}></div>
            </div>
          </div>
        </div>
        {/* 加载状态下的卡片骨架 */}
        <ResultCard title="一句话结论">
          <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
        </ResultCard>
        {['关系阶段', '兴趣等级', '心理分析', '分析依据', '风险点', '建议', '下一步行动'].map((title) => (
          <ResultCard key={title} title={title} variant={title === '风险点' ? 'risk' : title === '下一步行动' ? 'next_step' : undefined}>
            <div className="space-y-2">
              <div className="h-3 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-3 bg-gray-200 rounded animate-pulse w-5/6"></div>
            </div>
          </ResultCard>
        ))}
      </div>
    );
  }

  // 分析失败状态 - 明确错误状态
  if (actualStatus === 'error') {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-50 mb-4">
            <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">分析失败</h3>
          <p className="text-gray-600 max-w-md mx-auto mb-4">
            {errorMessage || '分析过程中出现错误，请检查输入内容或稍后重试。'}
          </p>
          <div className="mt-6">
            <button
              className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md font-medium hover:bg-blue-200"
              onClick={() => window.location.reload()}
            >
              刷新页面重试
            </button>
          </div>
        </div>
        {/* 错误状态下的卡片占位 */}
        <OneSentenceConclusion result={null} />
        {['关系阶段', '兴趣等级', '心理分析', '分析依据', '风险点', '建议', '下一步行动'].map((title) => (
          <ResultCard key={title} title={title} variant={title === '风险点' ? 'risk' : title === '下一步行动' ? 'next_step' : undefined}>
            <p className="text-gray-400 italic">分析失败，无法显示内容</p>
          </ResultCard>
        ))}
      </div>
    );
  }

  // 分析成功状态 - 显示结果卡片结构
  const {
    relationship_stage,
    interest_level,
    psychological_analysis,
    risk_points,
    suggestions,
    next_step,
  } = result!;

  return (
    <div className="space-y-6 min-w-0 break-words">
      <SummaryCard result={result!} />
      <ResultCard title="关系阶段">
        <p className="text-gray-800">{relationship_stage}</p>
        <p className="text-gray-500 text-sm mt-1">{getRelationshipStageExplanation(relationship_stage)}</p>
      </ResultCard>

      <ResultCard title="兴趣等级">
        <p className="text-gray-800">{interest_level}</p>
        <p className="text-gray-500 text-sm mt-1">{getInterestLevelExplanation(interest_level)}</p>
      </ResultCard>

      <ResultCard title="心理分析">
        <p className="text-gray-800">{psychological_analysis}</p>
      </ResultCard>

      <ResultCard title="分析依据" variant="default">
        <div className="text-sm text-gray-600 mb-2">
          {getDataSourceExplanation()}
        </div>
        <ul className="space-y-1.5">
          {generateCredibilityHints(result!).map((hint, index) => (
            <li key={index} className="flex items-start">
              <span className="inline-block w-1.5 h-1.5 mt-1.5 mr-2 rounded-full bg-gray-300 flex-shrink-0"></span>
              <span className="text-gray-700">{hint}</span>
            </li>
          ))}
        </ul>
      </ResultCard>

      <ResultCard title="风险点" variant="risk">
        {risk_points && risk_points.length > 0 ? (
          <ul className="space-y-2">
            {risk_points.map((risk, index) => (
              <li key={index} className="flex items-start">
                <span className="inline-flex items-center justify-center w-5 h-5 mr-2 mt-0.5 text-red-500 flex-shrink-0">⚠️</span>
                <span className="text-gray-800 font-medium">{risk}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 italic">当前未识别到明显风险点</p>
        )}
      </ResultCard>

      <ResultCard title="建议">
        {suggestions && suggestions.length > 0 ? (
          <ol className="space-y-3">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 mr-3 mt-0.5 flex items-center justify-center rounded-full bg-green-100 text-green-800 text-sm font-medium">
                  {index + 1}
                </span>
                <span className="text-gray-800 leading-relaxed">{suggestion}</span>
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-gray-500 italic">当前暂无明确建议</p>
        )}
      </ResultCard>

      <ResultCard title="下一步行动" variant="next_step">
        {next_step && next_step.trim() ? (
          <p>{next_step}</p>
        ) : (
          <p className="italic">当前暂无明确下一步建议</p>
        )}
      </ResultCard>

      {/* 用户下一步行动区 */}
      <NextActionsCard
        requestId={requestId}
        onNewAnalysis={onNewAnalysis}
        onFeedback={onFeedback}
      />
    </div>
  );
}