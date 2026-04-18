"""
LoveAdvisor V3 - S3 Signal Summary Prompts
Phase 3: S2/S3 Localization Migration

This module contains prompts for the S3 (signal summary) stage.
These prompts guide LLMs in summarizing and interpreting advanced relationship signals.
Output must be strict JSON with specific boolean fields and summary array.
"""

S3_SYSTEM_PROMPT = """
你是一个专业的恋爱关系高级信号分析专家。你的任务是从对话文本中识别高级关系信号。

请仔细分析对话，关注以下高级信号维度：
1. **亲密信号 (has_intimacy_signal)**: 对话中是否有明确的亲密表达或暗示？
2. **关系试探 (has_relationship_probe)**: 是否有对关系状态的试探或确认？
3. **正向承接 (has_positive_reciprocity)**: 是否有明显的双向积极互动？
4. **拒绝信号 (has_rejection_signal)**: 是否有明确的拒绝信号（直接拒绝、回避+多轮、负面情绪）？注意：单句短回复、信息性回答不能作为拒绝信号。
5. **推拉模式 (has_push_pull_pattern)**: 是否出现"推进-后退"的矛盾模式？
6. **持续冷淡 (has_sustained_coldness)**: 是否出现持续性的冷淡或疏远？（注意：需要多轮互动且连续多个回合冷淡，单次简短回复或只有2-3轮的对话不能判定为持续冷淡）

请基于对话内容进行客观分析，关注明确表达的信号。
"""

S3_PROMPT = """
对话文本：
{conversation_text}

请分析以上对话，识别以下高级关系信号：

1. **亲密信号 (has_intimacy_signal)**:
   - true: 对话中出现明确的亲密表达，如爱意表达、亲密称呼、身体接触暗示、未来共同规划等
   - false: 没有明确的亲密表达

2. **关系试探 (has_relationship_probe)**:
   - true: 对话中出现对关系状态的试探，如"我们是什么关系"、"你觉得我怎么样"、"你对我们的关系有什么想法"等
   - false: 没有关系试探

3. **正向承接 (has_positive_reciprocity)**:
   - true: 对话中出现明显的双向积极互动，如双方都主动推进话题、积极回应对方情感、共同构建对话等
   - false: 没有明显的双向积极互动

4. **拒绝信号 (has_rejection_signal)**:
   - true: 对话中出现明确的拒绝信号，且必须满足以下条件之一：
       1. 明确拒绝表达：如"不想"、"不方便"、"不去了"等直接拒绝
       2. 回避行为 + 多轮互动：连续多轮回避话题，且对话轮数 > 2
       3. 负面情绪表达：如"烦"、"别"、"算了"等明确负面情绪
   - false: 没有明确的拒绝信号，或者出现以下情况之一：
       1. 单句短回复（如"在"、"上班"、"吃饭"）
       2. 信息性回答（如"上班"、"在忙"、"吃饭"）
       3. 对话轮数 <= 2（如果对话只有1-2轮，强制设为false）
   - **重要限制**：简短回应、信息性回答、单句回复不能作为拒绝信号。只有明确表达拒绝意图、回避+多轮、负面情绪才能触发true。

5. **推拉模式 (has_push_pull_pattern)**:
   - true: 对话中出现"推进-后退"的矛盾模式，如先表达亲密后突然冷淡、先主动后回避等
   - false: 没有推拉模式

6. **持续冷淡 (has_sustained_coldness)**:
   - true: 对话中出现持续性的冷淡或疏远，如连续多个回合都简短敷衍、情感基调持续冷淡
   - false: 没有持续冷淡
   - **重要限制**: 持续冷淡必须满足多轮互动（至少3个以上回合）且连续多个回合都表现出冷淡。单次简短回复或只有2-3轮的对话不足以判定为持续冷淡。

7. **信号摘要 (signal_summary)**: 用简短的语句总结识别到的主要信号（至少1条，最多5条）

**重要限制**:
- 绝对不允许输出 relationship_stage 字段
- 绝对不允许输出 interest_level 字段
- 必须使用严格JSON格式输出
- 所有布尔字段必须为 true 或 false，不能为其他值
- 所有字段都必须提供，不能省略
- **拒绝信号特殊限制**: 如果对话轮数 <= 2，必须设置 has_rejection_signal = false。单句短回复、信息性回答不能作为拒绝信号。

请输出以下JSON格式的分析结果：
```json
{{
  "has_intimacy_signal": false,
  "has_relationship_probe": false,
  "has_positive_reciprocity": false,
  "has_rejection_signal": false,
  "has_push_pull_pattern": false,
  "has_sustained_coldness": false,
  "signal_summary": ["信号摘要1"]
}}
```
"""