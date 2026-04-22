/**
 * Result Reasoning - Credibility Hints Module
 *
 * Provides simple explanations for how analysis conclusions were reached,
 * enhancing user trust by showing "how this conclusion came about".
 *
 * Implementation constraints:
 * - Frontend local generation only (simplest)
 * - No LLM usage
 * - No backend modifications
 * - Uses existing fields only (no new backend fields)
 * - Can be based on S2/S3 signal summaries (if available in debug)
 * - Or simple rule descriptions (frontend hardcoded)
 */

import { AnalyzeResult } from './api';

/**
 * Generate credibility hints based on analysis result
 * Returns an array of bullet point explanations
 */
export function generateCredibilityHints(result: AnalyzeResult): string[] {
  const hints: string[] = [];

  // Add relationship stage based hint
  if (result.relationship_stage && result.relationship_stage !== '无法判断') {
    const stageHint = getRelationshipStageHint(result.relationship_stage);
    if (stageHint) hints.push(stageHint);
  }

  // Add interest level based hint
  if (result.interest_level && result.interest_level !== '无法判断') {
    const levelHint = getInterestLevelHint(result.interest_level);
    if (levelHint) hints.push(levelHint);
  }

  // Add psychological analysis based hint (if contains certain keywords)
  if (result.psychological_analysis) {
    const psychHint = getPsychologicalAnalysisHint(result.psychological_analysis);
    if (psychHint) hints.push(psychHint);
  }

  // Add risk points based hint (if risks present)
  if (result.risk_points && result.risk_points.length > 0) {
    const riskHint = getRiskPointsHint(result.risk_points);
    if (riskHint) hints.push(riskHint);
  }

  // Check for S2/S3 signal summaries in debug field
  if (result.debug) {
    const signalHints = getSignalBasedHints(result.debug);
    hints.push(...signalHints);
  }

  // Fallback generic hints if we don't have specific ones
  if (hints.length === 0) {
    hints.push(
      '对话中存在持续回应',
      '话题有一定延续性',
      '未检测到明显拒绝信号'
    );
  }

  return hints.slice(0, 5); // Limit to 5 hints max
}

/**
 * Get hint based on relationship stage
 */
function getRelationshipStageHint(stage: string): string | null {
  const hintMap: Record<string, string> = {
    '初识期': '对话处于初步接触阶段，互动较为表面',
    '暧昧期': '双方表现出相互好感，互动带有试探性',
    '拉扯期': '关系进展不稳定，存在吸引与回避的波动',
    '冷淡期': '互动频率降低，回应较为简短'
  };

  return hintMap[stage] || null;
}

/**
 * Get hint based on interest level
 */
function getInterestLevelHint(level: string): string | null {
  const hintMap: Record<string, string> = {
    '低': '对方回应较为简短，缺乏深入互动意愿',
    '中': '对方有一定回应积极性，但仍处于观察阶段',
    '高': '对方表现出积极回应和进一步互动意愿'
  };

  return hintMap[level] || null;
}

/**
 * Get hint based on psychological analysis keywords
 */
function getPsychologicalAnalysisHint(analysis: string): string | null {
  const lowerAnalysis = analysis.toLowerCase();

  if (lowerAnalysis.includes('安全感') || lowerAnalysis.includes('信任')) {
    return '对话中体现出对安全感的关注';
  }

  if (lowerAnalysis.includes('试探') || lowerAnalysis.includes('谨慎')) {
    return '互动中表现出试探性行为';
  }

  if (lowerAnalysis.includes('主动') || lowerAnalysis.includes('积极')) {
    return '对话中检测到主动互动信号';
  }

  if (lowerAnalysis.includes('被动') || lowerAnalysis.includes('回避')) {
    return '对话中检测到被动或回避倾向';
  }

  return null;
}

/**
 * Get hint based on risk points
 */
function getRiskPointsHint(riskPoints: string[]): string | null {
  const riskCount = riskPoints.length;

  if (riskCount === 0) {
    return null;
  }

  if (riskCount === 1) {
    return '检测到1个潜在风险点';
  }

  return `检测到${riskCount}个潜在风险点`;
}

/**
 * Extract signal-based hints from debug field
 */
function getSignalBasedHints(debug: Record<string, any>): string[] {
  const hints: string[] = [];

  // Check for S2 signals (raw signals)
  if (debug.s2_signals && Array.isArray(debug.s2_signals) && debug.s2_signals.length > 0) {
    const signalCount = debug.s2_signals.length;
    hints.push(`基于${signalCount}个互动信号分析`);
  }

  // Check for S3 summary (signal summary)
  if (debug.s3_summary && typeof debug.s3_summary === 'string') {
    // Extract key phrases from summary
    const summary = debug.s3_summary;
    if (summary.includes('持续回应')) {
      hints.push('对话中存在持续回应模式');
    }
    if (summary.includes('话题延续')) {
      hints.push('话题有一定延续性');
    }
    if (summary.includes('拒绝') && summary.includes('未检测')) {
      hints.push('未检测到明显拒绝信号');
    }
  }

  // Check for other signal-related fields
  if (debug.signals_extracted && debug.signals_extracted > 0) {
    hints.push(`提取了${debug.signals_extracted}个关键互动特征`);
  }

  return hints;
}

/**
 * Get a simple explanation of data sources for display
 */
export function getDataSourceExplanation(): string {
  return '内容来源：基于对话文本分析，结合互动信号提取';
}