"""
LoveAdvisor V3 - S2 Signal Extraction Prompts
Phase 3: S2/S3 Localization Migration

This module contains prompts for the S2 (signal extraction) stage.
These prompts guide LLMs in extracting emotional and relational signals from text.
Output must be strict JSON with specific fields.
"""

S2_SYSTEM_PROMPT = """
你是一个专业的恋爱关系信号分析专家。你的任务是从对话文本中提取基础信号。

请仔细分析对话，关注以下维度：
1. **主动性 (initiative)**: 谁在对话中更主动发起话题或推进对话？
2. **回应长度 (response_length)**: B的回应长度如何？
3. **情感基调 (emotional_tone)**: 对话的情感温度是怎样的？
4. **话题深度 (topic_depth)**: 对话涉及的话题深度如何？
5. **互动承接性 (interaction_reciprocity)**: B如何承接A的话题？
6. **关键信号 (key_signals)**: 对话中出现的值得注意的具体信号。

请基于对话内容进行客观分析，不要猜测未明确表达的信息。
"""

S2_PROMPT = """
对话文本：
{conversation_text}

请分析以上对话，提取以下基础信号：

1. **主动性 (initiative)**:
   - "A更主动": A明显更主动发起和推进对话
   - "B更主动": B明显更主动回应或推进对话
   - "双方接近": 双方主动性相近
   - "无法判断": 信息不足无法判断

2. **回应长度 (response_length)**:
   - "短": B的回应简短（通常1-5字）
   - "中": B的回应适中（通常6-15字）
   - "长": B的回应较长（16字以上）
   - "无法判断": 信息不足无法判断

3. **情感基调 (emotional_tone)**:
   - "热": 情感表达积极、热情、亲密
   - "温": 情感表达中性、礼貌、友好
   - "冷": 情感表达冷淡、疏远、消极
   - "无法判断": 信息不足无法判断

4. **话题深度 (topic_depth)**:
   - "浅": 话题停留在表面、日常、功能层面
   - "中": 话题涉及一定个人分享或轻度情感表达
   - "深": 话题涉及深度情感、关系或隐私内容
   - "无法判断": 信息不足无法判断

5. **互动承接性 (interaction_reciprocity)**:
   - "正向承接": B积极回应A的话题，推进对话
   - "弱承接": B简单回应但没有明显推进
   - "明显回避": B回避或转移A的话题
   - "无法判断": 信息不足无法判断

6. **关键信号 (key_signals)**: 列出对话中出现的具体信号，如：
   - 表情符号使用
   - 主动提问
   - 分享个人信息
   - 表达情感
   - 提出邀约
   - 使用亲密称呼
   - 等（至少1条，最多5条）

**重要限制**:
- 绝对不允许输出 relationship_stage 字段
- 绝对不允许输出 interest_level 字段
- 必须使用严格JSON格式输出
- 所有字段都必须提供，不能省略

请输出以下JSON格式的分析结果：
```json
{{
  "initiative": "A更主动",
  "response_length": "短",
  "emotional_tone": "温",
  "topic_depth": "浅",
  "interaction_reciprocity": "弱承接",
  "key_signals": ["信号1", "信号2"]
}}
```
"""