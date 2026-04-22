import React from 'react';
import { AnalyzeResult } from '@/lib/api';
import { generateConclusion } from '@/lib/generateConclusion';
import ResultCard from './ResultCard';

interface OneSentenceConclusionProps {
  result: AnalyzeResult | null;
}

export default function OneSentenceConclusion({ result }: OneSentenceConclusionProps) {
  const conclusion = generateConclusion(result);

  // 空状态处理：当没有结论时显示占位文案
  if (!conclusion) {
    return (
      <ResultCard title="一句话结论" className="bg-blue-50 border-l-4 border-blue-500">
        <p className="text-gray-500">等待分析结果生成...</p>
      </ResultCard>
    );
  }

  return (
    <ResultCard title="一句话结论" className="bg-blue-50 border-l-4 border-blue-500">
      <p className="text-gray-800 font-medium">{conclusion}</p>
    </ResultCard>
  );
}