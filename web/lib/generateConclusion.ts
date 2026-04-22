import { AnalyzeResult } from './api';

/**
 * 基于分析结果生成一句话结论
 * 综合 relationship_stage, interest_level, next_step 等信息
 * 提供兜底逻辑，确保在各种情况下都有合理的输出
 */
export function generateConclusion(result: AnalyzeResult | null): string {
  // 空状态处理
  if (!result) {
    return '';
  }

  const { relationship_stage, interest_level, next_step } = result;

  // 检查字段是否有有效值（非空字符串）
  const hasStage = relationship_stage && relationship_stage.trim().length > 0;
  const hasInterest = interest_level && interest_level.trim().length > 0;
  const hasNextStep = next_step && next_step.trim().length > 0;

  // 如果所有字段都缺失，返回兜底文案
  if (!hasStage && !hasInterest && !hasNextStep) {
    return '基于分析，暂无明确结论。';
  }

  // 构建结论句子
  const parts: string[] = [];

  if (hasStage && hasInterest) {
    parts.push(`当前处于${relationship_stage.trim()}阶段，对方兴趣等级为${interest_level.trim()}。`);
  } else if (hasStage) {
    parts.push(`当前处于${relationship_stage.trim()}阶段。`);
  } else if (hasInterest) {
    parts.push(`对方兴趣等级为${interest_level.trim()}。`);
  }

  if (hasNextStep) {
    // 如果已经有前面的句子，添加空格分隔；否则直接添加
    const nextStepText = `建议${next_step.trim()}`;
    // 确保 next_step 不以句号结尾，避免重复标点
    const cleanedNextStep = nextStepText.endsWith('。')
      ? nextStepText.slice(0, -1)
      : nextStepText;
    parts.push(`${cleanedNextStep}。`);
  }

  // 合并所有部分，确保句子连贯
  let conclusion = parts.join(' ');

  // 清理可能的重复空格和标点
  conclusion = conclusion.replace(/\s+/g, ' ').trim();

  // 确保以句号结尾
  if (!conclusion.endsWith('。')) {
    conclusion += '。';
  }

  return conclusion;
}

/**
 * 生成一句话结论的简化版本，用于显示在卡片标题等位置
 * 返回更简洁的文本，避免过长
 */
export function generateShortConclusion(result: AnalyzeResult | null): string {
  const fullConclusion = generateConclusion(result);

  // 如果结论过长，可以截断，但保留完整句子
  // 这里暂时返回完整结论，后续可以根据需要调整
  return fullConclusion;
}