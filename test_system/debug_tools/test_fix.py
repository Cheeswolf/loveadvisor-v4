#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from app.rules.rules import infer_relationship_stage, infer_interest_level

# E2 actual data from test_results.json
s2_e2 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "无法判断",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["A主动发起对话", "B进行简短确认"]
}
s3_e2 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": ["对话仅为简单的发起与确认，轮数过少，未识别到任何高级关系信号。"]
}

# E3 actual data
s2_e3 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["A主动发起话题", "B仅作简短事实性回应"]
}
s3_e3 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": ["对话简短，仅为日常信息交换，未识别出任何高级关系信号。"]
}

# D1 data (need to guess)
# From D1 result, we need S2/S3. Not available in debug. Let's approximate from description.
# D1 is supposed to be冷淡期 but currently judged as拉扯期.
# We'll test after fix.

print("Testing E2:")
stage = infer_relationship_stage(s2_e2, s3_e2)
interest = infer_interest_level(s2_e2, s3_e2, stage)
print(f"  stage: {stage}")
print(f"  interest: {interest}")
print()

print("Testing E3:")
stage = infer_relationship_stage(s2_e3, s3_e3)
interest = infer_interest_level(s2_e3, s3_e3, stage)
print(f"  stage: {stage}")
print(f"  interest: {interest}")
print()

# Also test A1 to ensure not broken
s2_a1 = {
    "initiative": "A更主动",
    "response_length": "中",
    "emotional_tone": "温",
    "topic_depth": "中",
    "interaction_reciprocity": "正向承接",
    "key_signals": ["互相问候", "询问专业"]
}
s3_a1 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": []
}
print("Testing A1 (should be 初识期):")
stage = infer_relationship_stage(s2_a1, s3_a1)
interest = infer_interest_level(s2_a1, s3_a1, stage)
print(f"  stage: {stage}")
print(f"  interest: {interest}")
print()