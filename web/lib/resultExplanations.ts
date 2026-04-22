/**
 * Result Explanations Mapping
 *
 * Provides human-readable explanations for relationship stage and interest level values
 * to help users better understand analysis results.
 */

export const RELATIONSHIP_STAGE_EXPLANATIONS: Record<string, string> = {
  "初识期": "双方刚开始接触，互动较浅，关系尚未建立",
  "暧昧期": "双方互有好感，但尚未明确关系，处于试探阶段",
  "拉扯期": "关系进展不稳定，既有吸引又有回避，处于波动状态",
  "冷淡期": "互动减少，兴趣下降，关系可能出现问题",
  "无法判断": "信号有限，难以准确判断当前关系阶段"
} as const;

export const INTEREST_LEVEL_EXPLANATIONS: Record<string, string> = {
  "低": "对方兴趣较低，可能只是礼貌性回应或缺乏深入交往意愿",
  "中": "对方有一定兴趣，但仍在观察阶段，需要进一步互动确认",
  "高": "对方兴趣较高，表现出积极回应和进一步发展的意愿",
  "无法判断": "信号有限，难以准确判断兴趣等级"
} as const;

/**
 * Get explanation for relationship stage
 */
export function getRelationshipStageExplanation(stage: string): string {
  return RELATIONSHIP_STAGE_EXPLANATIONS[stage] || "未知关系阶段";
}

/**
 * Get explanation for interest level
 */
export function getInterestLevelExplanation(level: string): string {
  return INTEREST_LEVEL_EXPLANATIONS[level] || "未知兴趣等级";
}

/**
 * Get combined display text with explanation
 */
export function getExplainedText(value: string, type: 'relationship_stage' | 'interest_level'): string {
  const explanation = type === 'relationship_stage'
    ? getRelationshipStageExplanation(value)
    : getInterestLevelExplanation(value);

  return `${value}：${explanation}`;
}