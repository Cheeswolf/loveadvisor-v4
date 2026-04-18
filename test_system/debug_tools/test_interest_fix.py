#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from app.rules.rules import _initial_medium_signal, _pull_medium_signal

# Test A2-like sample
s2_a2 = {
    "initiative": "双方接近",
    "response_length": "中",
    "emotional_tone": "热",
    "topic_depth": "中",
    "interaction_reciprocity": "正向承接",
    "key_signals": ["表达共情", "提出邀约"]
}
s3_a2 = {
    "has_intimacy_signal": False,
    "has_relationship_probe": False,
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": ["基础互动"]
}

print("Testing A2-like sample:")
print(f"  s2: {s2_a2}")
print(f"  s3: {s3_a2}")
result = _initial_medium_signal(s2_a2, s3_a2)
print(f"  _initial_medium_signal result: {result}")
print()

# Test A3-like sample
s2_a3 = {
    "initiative": "一方主动",
    "response_length": "中",
    "emotional_tone": "热",
    "topic_depth": "浅",
    "interaction_reciprocity": "正向承接",
    "key_signals": ["互相夸奖"]
}
s3_a3 = s3_a2.copy()
print("Testing A3-like sample:")
print(f"  s2: {s2_a3}")
print(f"  s3: {s3_a3}")
result = _initial_medium_signal(s2_a3, s3_a3)
print(f"  _initial_medium_signal result: {result}")
print()

# Test weak interaction sample (should be False)
s2_weak = {
    "initiative": "双方接近",
    "response_length": "短",
    "emotional_tone": "温",
    "topic_depth": "中",
    "interaction_reciprocity": "弱承接",
    "key_signals": ["简短回应"]
}
s3_weak = {
    "has_intimacy_signal": False,
    "has_relationship_probe": True,  # 关系试探
    "has_positive_reciprocity": False,
    "has_rejection_signal": False,
    "has_push_pull_pattern": False,
    "has_sustained_coldness": False,
    "signal_summary": []
}
print("Testing weak interaction sample (礼貌回应，应返回False):")
print(f"  s2: {s2_weak}")
print(f"  s3: {s3_weak}")
result = _initial_medium_signal(s2_weak, s3_weak)
print(f"  _initial_medium_signal result: {result}")