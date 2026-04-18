#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.rules.rules import infer_r1_with_debug

# A2 数据
s2_a2 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["A主动提出邀约（下次一起去）", "B使用语气词（哈哈）"]
}

s3_a2 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": True,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": ["存在双向积极互动：双方轮流发起话题并积极回应", "A主动提出未来共同活动（一起去上课）并获得B的同意"]
}

print("=== Testing A2 ===")
result = infer_r1_with_debug(s2_a2, s3_a2)
print(f"Result: {result}")

# A3 数据
s2_a3 = {
    "initiative": "A更主动",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "浅",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["A主动给予赞美", "B使用'哈哈'缓和气氛并礼貌致谢", "B给予简短回赞"]
}

s3_a3 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": True,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": ["存在明显的双向积极互动：A发起赞美，B感谢并回赞"]
}

print("\n=== Testing A3 ===")
result = infer_r1_with_debug(s2_a3, s3_a3)
print(f"Result: {result}")